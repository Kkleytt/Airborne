# 🪂 AirborneClub Bot — Telegram Knowledge & Management Platform

![License](https://img.shields.io/badge/license-MIT-blue.svg )
![Python](https://img.shields.io/badge/python-3.12%2B-yellow.svg )
![Docker](https://img.shields.io/badge/dockerized-yes-blue.svg )
![FastAPI](https://img.shields.io/badge/api-FastAPI-00b894.svg )
![SQLAlchemy](https://img.shields.io/badge/sqlalchemy-SQL%20Toolkit-blue.svg )
![Aiogram]( https://img.shields.io/badge/aiogram-5.0-blueviolet.svg?logo=telegram&logoColor=white)
![AsyncIO]( https://img.shields.io/badge/asyncio-%23008BFF.svg?logo=python&logoColor=white)

![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?logo=redis&logoColor=white)
![PostgreSQL]( https://img.shields.io/badge/postgresql-%23316192.svg?logo=postgresql&logoColor=white)
![MySQL]( https://img.shields.io/badge/mysql-%23005C78.svg?logo=mysql&logoColor=white)
![TimeScaleDB]( https://img.shields.io/badge/timescaledb-black?logo=timescaledb&logoColor=brightgreen)


> Многофункциональный Telegram-бот и платформа для хранения, распространения и анализа информации: база знаний, пользователи, группы, события, логирование и многое другое.

---

## ⚙️ Основной функционал

- 📦 **Хранение Базы Знаний** (документы, изображения, аудио, клавиатуры, текст).
- 🧠 **Интеллектуальная архитектура** с Redis-кэшированием, RabbitMQ и асинхронными API.
- 🔐 **Ролевая модель пользователей** (user, trusted, admin, root).
- 📊 **Подключение статистики и логирования** через TimeScaleDB и очереди RabbitMQ.
- ⚡️ **Высокая производительность** за счёт Redis и TimeScaleDB
- 🔧 **Управление настройками бота через MySQL API** (включая live-конфигурацию).
- 📁 **Поддержка бэкапов, архивирования и синхронизации между БД**.
- 🔁 **Модульная система** с масштабируемой файловой архитектурой.

---

## 🧰 Используемые технологии

| Компонент       | Стек                              |
|-----------------|-----------------------------------|
| ЯП              | `Python 3.10+`                    |
| Telegram API    | `aiogram`                         |
| API сервер      | `FastAPI`, `Pydantic`, `Uvicorn`  |
| БД              | `MySQL`, `PostgreSQL`, `Redis`, `TimeScaleDB` |
| Очереди         | `RabbitMQ`                        |
| Кэш             | `Redis`                           |
| Логгер          | `aio_pika`, `colorama`, `JSON`    |
| ORM             | `SQLAlchemy 2.0 async`            |
| Планировщик     | `APScheduler`                     |
| Докеризация     | `Docker`, `docker-compose`        |

---

## 📂 Структура проекта

```bash
airborne/
├── api/               # FastAPI backend
├── bot/               # Telegram Bot
├── logger/            # Модуль логирования и консольного вывода
├── database/          # Подключение, ORM модели, схемыБ инициализация
├── scheduler/         # Планировщик задач (бэкапы, логи, Redis-синхронизация)
├── backup/            # Архивация и перенос данных
├── storage/           # Работа с файлами (структура, загрузка, сохранение)
├── docker/            # Докеризация проекта
│   ├── .env
│   ├── docker-compose.yml
├── settings/          # JSON и .env конфигурации
└── requirements.txt   # Список зависимостей
```

## 📦 Установка и запуск проекта
#### 🔧 Установка зависимостей

`pip install -r requirements.txt`

#### 🐳 Быстрый запуск через Docker
1. Убедитесь, что у вас установлен Docker и Docker Compose.
2. Перейдите в папку проекта:
`cd docker/`
3. Запустите сервисы:
`docker-compose up -d`
4. [📁 Открыть docker-compose.yml](./database/docker/docker-compose.yml)

## 💾 Инициализация БД
Проект использует init_database/ для начальной структуры таблиц и наполнения: [📁 Смотреть папку init_database](./database/init/)

## 📚 Библиотеки и зависимости
Примеры ключевых библиотек:
- fastapi, uvicorn
- sqlalchemy[asyncio], asyncmy, asyncpg
- redis, aio_pika, pika
- colorama, aiofiles, requests
- aiogram, apscheduler
[📄 Полный список зависимостей](requirements.txt)

## 📈 Планы по развитию
- 📡 Webhook-режим для Telegram бота
- 📊 Панель администратора на базе FastAPI + Vue
- ☁️ Интеграция с S3-хранилищами (Yandex Object Storage, Backblaze)
- 🧠 AI-модуль для автоматического анализа запросов и базы знаний
- 🔌 Микросервисная архитектура на базе RabbitMQ

## 🙏 Благодарности
Проект реализуется с максимальным вниманием к модульности, безопасности и производительности. Благодарю всех, кто помогает развивать архитектуру и сопровождает её на каждом этапе.

## 📄 Лицензия
Проект распространяется под лицензией MIT
