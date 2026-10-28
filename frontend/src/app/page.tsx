import CatalogClient from "./catalog-client";

type Product = {
  id: string;
  title: string;
  image_key: string;
};

export default async function Home() {
  const backendUrl = process.env.BACKEND_URL?.replace(/\/+$/, "");

  if (!backendUrl) {
    return (
      <main>
        <h1>Каталог</h1>
        <p>Не задана переменная BACKEND_URL в .env.local.</p>
      </main>
    );
  }

  let products: Product[];

  try {
    const response = await fetch(`${backendUrl}/api/product`, {
      cache: "no-store",
    });

    if (!response.ok) {
      throw new Error(
        `Ошибка при загрузке каталога: HTTP ${response.status}`,
      );
    }

    products = (await response.json()) as Product[];
  } catch (error) {
    const message =
      error instanceof Error ? error.message : "Неизвестная ошибка";

    return (
      <main>
        <h1>Каталог</h1>
        <p>Не удалось загрузить товары.</p>
        <p>{message}</p>
        <p>Проверь, что FastAPI запущен и доступен.</p>
      </main>
    );
  }

  return <CatalogClient initialProducts={products} />;
}
