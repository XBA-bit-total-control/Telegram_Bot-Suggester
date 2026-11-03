# Bot Suggester

MVP каталога товаров с Telegram-ботом и Telegram Mini App (TMA). Администратор добавляет товары через бота, 
пользователи просматривают каталог и управляют корзиной в браузере или внутри Telegram.

## Важное Персональное уточнение для команды ООО Евростройгрупп

Хотел, да забыл упомянуть, при развертывании проекта basket в MinIO сам по себе не создаться, автоматизировать это дело у меня не получилось,
поэтому после запуска сервиса minio, не забудьте создать basket с именем products, для этого будет удобно воспользоваться вэб-консолью 
управления minio по локальному адресу http://127.0.0.1:9001 вставив значения MINIO_ROOT_USER и MINIO_ROOT_PASSWORD из .env.local для входа.

## Ссылки
Бот: [@Suggester_products_BOT](https://t.me/Suggester_products_BOT)

Развернутый проект: https://bot-suggester.duckdns.org/

Предупреждение: Проект развернут на недолгий срок, предположительно до 16:00 03.11.2026 по МСК.

После этого воспользоваться или проверить его не получится. 

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

## Возможности

- Просмотр каталога и карточек товаров.
- Добавление товара администратором через Telegram-бота: фотография и название отправляются одним сообщением.
- Хранение изображений товаров в MinIO.
- Авторизация в Telegram Mini App с проверкой `initData` и выдачей JWT.
- Просмотр корзины, добавление и удаление товаров.
- Разграничение доступа пользователей и администраторов.
- Запуск в браузере или Telegram Mini App.
- Локальный запуск и подготовка production-развёртывания через Docker Compose.

## Как работает приложение

1. Пользователь открывает бота и переходит в каталог TMA.
2. Backend проверяет Telegram `initData`, создаёт пользователя при необходимости и выдаёт JWT.
3. Пользователь просматривает каталог и управляет своей корзиной.
4. Администратор отправляет боту фотографию с названием товара.
5. Бот передаёт данные backend: изображение сохраняется в MinIO, информация о товаре — в PostgreSQL.

## Архитектура

| Компонент | Назначение |
| --- | --- |
| **Backend — FastAPI** | REST API, авторизация и логика каталога и корзины |
| **PostgreSQL** | Хранение пользователей, товаров и корзин |
| **SQLAlchemy Async** | Асинхронный доступ к данным |
| **Alembic** | Миграции схемы базы данных |
| **Telegram-бот — aiogram 3** | Переход в Mini App, первоначальная настройка администратора и добавление товаров |
| **Frontend — Next.js** | Каталог и интерфейс Telegram Mini App |
| **MinIO** | Хранение изображений товаров |
| **Redis** | Хранение состояний FSM и изоляция событий бота в режиме webhook |
| **Docker Compose** | Локальный запуск и production-конфигурация |
| **Traefik** | HTTPS и маршрутизация production-трафика |

### Модели данных

В проекте определены четыре SQLAlchemy-модели:

- `User` — пользователь Telegram и его роль.
- `Product` — название товара и ключ изображения в MinIO.
- `Basket` — корзина пользователя.
- `BasketProduct` — связь товаров с корзинами.

В репозитории находятся две миграции Alembic.

## Backend API

В приложении определено **8 URL-шаблонов** и **10 сочетаний маршрута с HTTP-методом**.

| Метод | Маршрут | Назначение |
| --- | --- | --- |
| `GET` | `/health` | Проверка доступности backend |
| `POST` | `/validate` | Проверка Telegram `initData`, создание пользователя и выдача JWT |
| `POST` | `/internal/bootstrap-admin` | Первоначальное назначение администратора |
| `GET` | `/api/product` | Получение списка товаров |
| `POST` | `/api/product` | Добавление товара через внутренний запрос бота |
| `GET` | `/api/product/{product_id}` | Получение товара по идентификатору |
| `GET` | `/api/product/{product_id}/image` | Получение изображения товара |
| `GET` | `/api/basket` | Получение корзины текущего пользователя |
| `POST` | `/api/basket/items/{product_id}` | Добавление товара в корзину |
| `DELETE` | `/api/basket/items/{product_id}` | Удаление товара из корзины |

У корзины добавление и удаление используют один URL-шаблон, но разные HTTP-методы.

## Аутентификация и доступ

- Для входа из Telegram Mini App backend проверяет подпись и содержимое `initData`.
- После успешной проверки backend выдаёт JWT. Защищённые запросы используют Bearer-токен.
- Пользователь может работать со своей корзиной.
- Добавлять товары может пользователь с ролью администратора.
- Внутренние запросы бота к backend используют заголовок `X-Internal-API-Key`.
- Первоначальное назначение администратора выполняется через одноразовый bootstrap-сценарий.

## Локальный запуск на Windows

Инструкция рассчитана на Windows с установленным и запущенным Docker Desktop. Команды выполняются в PowerShell из корневого каталога
уже клонированного проекта на устройство.

### 1. Создайте файл конфигурации

```powershell
Copy-Item .env.local.example .env.local
```

Откройте `.env.local` и укажите необходимые значения:

- `BOT_TOKEN` - токен Telegram-бота.
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` - параметры PostgreSQL.
- `MINIO_ROOT_USER`, `MINIO_ROOT_PASSWORD` - учётные данные MinIO.
- `BOT_API_SECRET_KEY` - секрет для внутренних запросов бота.
- `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `JWT_LIFE_LENGTH` - параметры JWT.
- `MINIO_BUCKET=products` - имя basket для изображений.

### 2. Выберите режим запуска

**-> Только браузер:** оставьте значение:

```dotenv
FRONTEND_ORIGIN=http://localhost:3000
```

При таком режиме можно не запускать сервис `bot` и открыть приложение в браузере.

**-> Telegram Mini App:** Понадобиться ngrok, установите и настройте его, если этого ещё не сделано. Запустите туннель на порт frontend:

```powershell
ngrok http 3000
```

Укажите выданный ngrok адрес в `FRONTEND_ORIGIN`, включая `https://` и без завершающего `/`. Например:

```dotenv
FRONTEND_ORIGIN=https://example.ngrok-free.app
```

Если адрес при запуске ngrok вы сразу не нашли, его можно посмотреть в интерфейсе ngrok по адресу [http://127.0.0.1:4040](http://127.0.0.1:4040).

Во время работы Mini App процесс ngrok должен оставаться запущенным. При перезапуске ngrok адрес может измениться из-за чего потребуется 
установить корректное значение для `FRONTEND_ORIGIN`.

### 3. Запустите PostgreSQL, Redis и MinIO

```powershell
docker compose --env-file .env.local -f docker-compose.yml -f docker-compose.local.yml up -d postgres redis minio
```

Проверьте состояние контейнеров:

```powershell
docker compose --env-file .env.local -f docker-compose.yml -f docker-compose.local.yml ps -a
```

Дождитесь, пока PostgreSQL будет готов принимать соединения.

### 4. Создайте бакет MinIO

Basket `products` автоматически не создаётся. После запуска MinIO откройте [http://127.0.0.1:9001](http://127.0.0.1:9001) 
и войдите, используя `MINIO_ROOT_USER` и `MINIO_ROOT_PASSWORD` из `.env.local`.

Создайте basket с именем `products`.

### 5. Примените миграции

```powershell
docker compose --env-file .env.local -f docker-compose.yml -f docker-compose.local.yml run --rm backend uv run --no-sync alembic upgrade head
```

### 6. Запустите приложение

Для запуска backend и frontend без Telegram-бота:

```powershell
docker compose --env-file .env.local -f docker-compose.yml -f docker-compose.local.yml up -d --build backend frontend
```

Для запуска полного набора сервисов, включая бота:

```powershell
docker compose --env-file .env.local -f docker-compose.yml -f docker-compose.local.yml up -d --build backend frontend bot
```

Проверьте состояние контейнеров:

```powershell
docker compose --env-file .env.local -f docker-compose.yml -f docker-compose.local.yml ps -a
```

Если какой-либо из них не был запущен или работает некорректно, рекомендую проверить логи и самостоятельно разбираться в ошибке.
Если ошибка в MinIO - читайте ниже.

При успешном запуске Frontend будет доступен по адресу `http://localhost:3000`, backend — на `http://localhost:8000`. 
Документация API FastAPI доступна по адресу `http://localhost:8000/docs`.

### Если MinIO выдаёт `file access denied`

Остановите контейнер MinIO, если он работает:

```powershell
docker compose --env-file .env.local -f docker-compose.yml -f docker-compose.local.yml stop minio
```

Затем выполните команду исправления прав на данные MinIO:

```powershell
docker run --rm --user 0:0 -v bot_suggester_minio_data:/data busybox:1.36 sh -c 'chown -R 65532:65532 /data && chmod -R u+rwX /data'
```

После этого запустите MinIO снова:

```powershell
docker compose --env-file .env.local -f docker-compose.yml -f docker-compose.local.yml up -d minio
```

## Production-развёртывание

Для production подготовлен отдельный файл `docker-compose.production.yml`. В конфигурации предусмотрены Traefik, HTTPS с сертификатами Let's Encrypt и запуск Telegram-бота в режиме webhook.

Для развёртывания нужны сервер, домен, заполненный `.env.production` и настроенная внешняя Docker-сеть для Traefik.

## Стек технологий

**Python 3.12+, FastAPI, SQLAlchemy Async, PostgreSQL, Alembic, Pydantic, JWT, aiogram 3, Redis, MinIO, Next.js, TypeScript, Docker Compose, Traefik.**

## Ограничения

- Это MVP с минималистичным интерфейсом.
- Basket в MinIO необходимо создать вручную.
- Тестов для проверки не написано.
- Доступность демонстрационного развёртывания временная.
