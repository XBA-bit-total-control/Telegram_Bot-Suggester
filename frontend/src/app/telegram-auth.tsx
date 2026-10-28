
"use client";

import { useEffect, useState } from "react";

type TelegramWebApp = {
  initData: string;
  ready: () => void;
  expand: () => void;
};

// 1. Добавляем тип пропсов компонента
type TelegramAuthProps = {
  onAuthenticated: (token: string) => void;
};

declare global {
  interface Window {
    Telegram?: {
      WebApp: TelegramWebApp;
    };
  }
}

// 2. Принимаем пропс onAuthenticated
export default function TelegramAuth({
  onAuthenticated,
}: TelegramAuthProps) {
  const [status, setStatus] = useState("Проверяем Telegram...");

  useEffect(() => {
    const webApp = window.Telegram?.WebApp;

    if (!webApp) {
      setStatus("Открой приложение через Telegram.");
      return;
    }

    webApp.ready();
    webApp.expand();

    const initData = webApp.initData;

    if (!initData) {
      setStatus("Telegram не передал initData.");
      return;
    }

    let cancelled = false;

    async function validateTelegramData() {
      try {
        const response = await fetch("/backend/validate", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            init_data: initData,
          }),
        });

        const result = (await response.json().catch(() => ({}))) as {
          access_token?: string;
          detail?: string;
        };

        if (!response.ok) {
          throw new Error(result.detail ?? `HTTP ${response.status}`);
        }

        if (!result.access_token) {
          throw new Error("Backend не вернул JWT.");
        }

        // 3. Передаём JWT в родительский компонент
        if (!cancelled) {
          onAuthenticated(result.access_token);
          setStatus("Telegram проверен, авторизация выполнена.");
        }
      } catch (error) {
        if (!cancelled) {
          const message =
            error instanceof Error
              ? error.message
              : "Неизвестная ошибка";

          setStatus(`Не удалось проверить Telegram: ${message}`);
        }
      }
    }

    void validateTelegramData();

    return () => {
      cancelled = true;
    };
  }, [onAuthenticated]);

  return <p role="status">{status}</p>;
}
