# Courier Delivery Service Backend API

![FastAPI Version](https://img.shields.io/badge/FastAPI-latest-green.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Docker](https://img.shields.io/badge/Docker-supported-blue.svg)
![Nginx](https://img.shields.io/badge/Nginx-configured-brightgreen.svg)

Backend API сервис для системы курьерской доставки, разработанный с использованием FastAPI. Сервис обеспечивает полную функциональность для работы [мобильного приложения курьеров](https://github.com/Ambassador-of-programming/Courier_delivery_service_Flet).

## Основные возможности

- 🔐 JWT аутентификация
- 📦 Управление заказами
- 👤 Система пользователей (курьеры, администраторы)
- 📱 REST API для мобильного приложения
- 📸 Обработка QR-кодов для подтверждения доставки
- 🗄️ PostgreSQL для хранения данных
- 🚀 Nginx в качестве reverse proxy
- 🐳 Docker для развертывания

## Требования

- Python 3.8+
- Docker и Docker Compose
- PostgreSQL
- Nginx

## Зависимости

```toml
fastapi = "*"
uvicorn = "*"
pipenv = "*"
opencv-python = "*"
pyzbar = "*"
pillow = "*"
asyncpg = "*"
python-multipart = "*"
python-jose = "*"
```

## Установка и запуск

### Локальная разработка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/Ambassador-of-programming/Courier_delivery_service_FastAPI.git
cd Courier_delivery_service_FastAPI
```

2. Установите зависимости:
```bash
pipenv install
```

3. Активируйте виртуальное окружение:
```bash
pipenv shell
```

4. Запустите сервер для разработки:
```bash
uvicorn app.main:app --reload
```

### Запуск через Docker

1. Соберите и запустите контейнеры:
```bash
docker-compose up -d --build
```

## Конфигурация

### Переменные окружения

Создайте файл `.env` в корневой директории:

```env
DATABASE_URL=postgresql://user:password@db:5432/dbname
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Nginx конфигурация

Базовая конфигурация находится в `docker/nginx/nginx.conf`

## Интеграция с мобильным приложением

Данный backend сервис разработан для работы с [мобильным приложением для курьеров](https://github.com/Ambassador-of-programming/Courier_delivery_service_Flet).

## Развертывание

1. Убедитесь, что Docker и Docker Compose установлены
2. Настройте переменные окружения
3. Запустите:
```bash
docker-compose up -d
```

## Связанные проекты

- [Мобильное приложение](https://github.com/Ambassador-of-programming/Courier_delivery_service_Flet) - Frontend часть на Flet

## Контакты

Ссылка на проект: [https://github.com/Ambassador-of-programming/Courier_delivery_service_FastAPI](https://github.com/Ambassador-of-programming/Courier_delivery_service_FastAPI)

## Благодарности

* FastAPI
* PostgreSQL
* Nginx
* Docker
* Всем контрибьюторам проекта