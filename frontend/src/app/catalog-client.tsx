"use client";

import { useCallback, useEffect, useState } from "react";
import TelegramAuth from "./telegram-auth";

type Product = {
  id: string;
  title: string;
  image_key: string;
};

type BasketResponse = {
  products: Product[];
};

type CatalogClientProps = {
  initialProducts: Product[];
};

async function getErrorMessage(response: Response): Promise<string> {
  const body = (await response.json().catch(() => null)) as {
    detail?: unknown;
  } | null;

  return typeof body?.detail === "string"
    ? body.detail
    : `HTTP ${response.status}`;
}

export default function CatalogClient({
  initialProducts,
}: CatalogClientProps) {
  const [accessToken, setAccessToken] = useState<string | null>(null);

  const [basketProducts, setBasketProducts] = useState<Product[]>([]);
  const [isBasketLoading, setIsBasketLoading] = useState(false);

  const [basketError, setBasketError] = useState<string | null>(null);
  const [actionMessage, setActionMessage] = useState<string | null>(null);

  const [addingProductId, setAddingProductId] = useState<string | null>(null);
  const [removingProductId, setRemovingProductId] = useState<string | null>(
    null,
  );

  // Получаем JWT от компонента TelegramAuth.
  const handleAuthenticated = useCallback((token: string) => {
    setAccessToken(token);
  }, []);

  // Загружаем корзину после успешной авторизации.
  useEffect(() => {
    if (!accessToken) {
      return;
    }

    let cancelled = false;

    async function loadBasket() {
      setIsBasketLoading(true);
      setBasketError(null);

      try {
        const response = await fetch("/backend/api/basket", {
          method: "GET",
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
          cache: "no-store",
        });

        if (!response.ok) {
          throw new Error(await getErrorMessage(response));
        }

        const basket = (await response.json()) as BasketResponse;

        if (!cancelled) {
          setBasketProducts(basket.products);
        }
      } catch (error) {
        if (!cancelled) {
          setBasketError(
            error instanceof Error
              ? error.message
              : "Не удалось загрузить корзину.",
          );
        }
      } finally {
        if (!cancelled) {
          setIsBasketLoading(false);
        }
      }
    }

    void loadBasket();

    return () => {
      cancelled = true;
    };
  }, [accessToken]);

  // Добавляем товар и получаем обновлённую корзину от backend.
  async function addProduct(product: Product) {
    if (!accessToken) {
      return;
    }

    setAddingProductId(product.id);
    setBasketError(null);
    setActionMessage(null);

    try {
      const response = await fetch(
        `/backend/api/basket/items/${product.id}`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        },
      );

      if (!response.ok) {
        throw new Error(await getErrorMessage(response));
      }

      const basket = (await response.json()) as BasketResponse;

      setBasketProducts(basket.products);
      setActionMessage(`«${product.title}» добавлен в корзину.`);
    } catch (error) {
      setBasketError(
        error instanceof Error
          ? error.message
          : "Не удалось добавить товар.",
      );
    } finally {
      setAddingProductId(null);
    }
  }

  // Удаляем товар. Endpoint возвращает HTTP 204 без тела ответа.
  async function removeProduct(product: Product) {
    if (!accessToken) {
      return;
    }

    setRemovingProductId(product.id);
    setBasketError(null);
    setActionMessage(null);

    try {
      const response = await fetch(
        `/backend/api/basket/items/${product.id}`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        },
      );

      if (!response.ok) {
        throw new Error(await getErrorMessage(response));
      }

      // Запрос успешен — убираем товар из локального состояния.
      setBasketProducts((currentProducts) =>
        currentProducts.filter((item) => item.id !== product.id),
      );

      setActionMessage(`«${product.title}» удалён из корзины.`);
    } catch (error) {
      setBasketError(
        error instanceof Error
          ? error.message
          : "Не удалось удалить товар.",
      );
    } finally {
      setRemovingProductId(null);
    }
  }

  const isBusy =
    isBasketLoading ||
    addingProductId !== null ||
    removingProductId !== null;

  return (
    <main>
      <h1>Каталог</h1>

      <TelegramAuth onAuthenticated={handleAuthenticated} />

      <section aria-labelledby="basket-heading">
        <h2 id="basket-heading">
          Корзина ({basketProducts.length})
        </h2>

        {!accessToken ? (
          <p>Корзина станет доступна после авторизации через Telegram.</p>
        ) : isBasketLoading ? (
          <p>Загружаем корзину...</p>
        ) : basketProducts.length === 0 ? (
          <p>Корзина пуста.</p>
        ) : (
          <ul>
            {basketProducts.map((product) => (
              <li key={product.id}>
                <span>{product.title}</span>{" "}

                <button
                  type="button"
                  onClick={() => void removeProduct(product)}
                  disabled={isBusy}
                >
                  {removingProductId === product.id
                    ? "Удаляем..."
                    : "Удалить"}
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>

      {basketError && <p role="alert">Ошибка: {basketError}</p>}

      {actionMessage && <p role="status">{actionMessage}</p>}

      <section aria-labelledby="catalog-heading">
        <h2 id="catalog-heading">Все товары:</h2>

        {initialProducts.length === 0 ? (
          <p>Каталог пока пуст.</p>
        ) : (
          <ul>
            {initialProducts.map((product) => (
              <li key={product.id}>
                <h3>{product.title}</h3>

                <img
                  src={`/backend/api/product/${product.id}/image`}
                  alt={product.title}
                  width={200}
                />

                <p>ID: {product.id}</p>

                <button
                  type="button"
                  onClick={() => void addProduct(product)}
                  disabled={!accessToken || isBusy}
                >
                  {addingProductId === product.id
                    ? "Добавляем..."
                    : "Добавить в корзину"}
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}
