# Bot Suggester

Микросервисный каталог товаров с Telegram-ботом и Telegram Mini App (TMA). Администратор может добавлять товары через бота, а пользователи - просматривать каталог и управлять своей корзиной через веб-интерфейс.

## Важное Персональное уточнение для команды ООО Евростройгрупп

Хотел, да забыл упомянуть, при развертывании проекта basket в MinIO сам по себе не создаться, автоматизировать это дело у меня не получилось,
поэтому после запуска сервиса minio, не забудьте создать basket с именем products, для этого будет удобно воспользоваться вэб-консолью 
управления minio по локальному адресу http://127.0.0.1:9001 вставив значения MINIO_ROOT_USER и MINIO_ROOT_PASSWORD из .env.local для входа.

## Ссылки
Бот: [@Suggester_products_BOT](https://t.me/Suggester_products_BOT)
Развернутый проект: https://bot-suggester.duckdns.org/

Предупреждение: Проект развернут на недолгий срок, предположительно до 01.11.2026 (включительно).

После этого воспользоваться или проверить его не получится. 

## Компоненты проекта

- **Telegram-бот — aiogram 3.x.** Обрабатывает `/start`, предлагает открыть каталог в Mini App и позволяет администратору добавить товар, отправив фотографию с названием в одном сообщении.
- **Backend — FastAPI.** Предоставляет API для каталога, изображений, авторизации пользователей и корзины. Проверяет Telegram `initData`, выдает JWT и разграничивает доступ по ролям.
- **Frontend — Next.js (App Router).** Отображает каталог товаров и работает как в обычном браузере, так и внутри Telegram Mini App. Запросы к backend проходят через прокси `/backend`.
- **PostgreSQL.** Хранит пользователей, товары, корзины и связи между товарами и корзинами.
- **MinIO.** S3-совместимое хранилище для изображений товаров.
- **Redis.** Предназначен для общего хранения FSM и изоляции событий между экземплярами бота в режиме webhook.
- **Alembic.** Управляет версиями схемы базы данных и применением миграций.
- **Docker Compose.** Используется для локального запуска сервисов и подготовки production-развертывания.

## Структура репозитория

```text
.
├── frontend/                 # Next.js: каталог и Telegram Mini App
├── migrations/               # Миграции Alembic
├── src/
│   ├── api/                  # HTTP-маршруты FastAPI
│   ├── bot_suggester/        # Бот и обработчики Telegram
│   ├── models/               # SQLAlchemy-модели
│   ├── schemas/              # Pydantic-схемы API
│   ├── services/             # Бизнес-логика
│   ├── storage/              # Работа с MinIO
│   └── utilities/            # Telegram-аутентификация и JWT
├── Dockerfile.python
├── docker-compose.local.yml
├── docker-compose.production.yml
├── alembic.ini
├── pyproject.toml
├── README.md
├── uv.lock
├── .env.local.example
├── .env.production.example
├── .python-version
├── .gitignore
└── .dockerignore 
```

## Основные сценарии

1. Администратор отправляет боту фотографию и название товара в одном сообщении.
2. Бот обращается к backend; изображение сохраняется в MinIO, а данные товара — в PostgreSQL.
3. Пользователь открывает каталог в браузере или Telegram Mini App.
4. В TMA backend проверяет Telegram `initData` и возвращает JWT. Авторизованный пользователь может просматривать свою корзину, добавлять и удалять товары.

## Технологии

Python 3.12+, FastAPI, aiogram 3.x, SQLAlchemy (async), PostgreSQL, Alembic, MinIO, Redis, Next.js, TypeScript и Docker Compose.