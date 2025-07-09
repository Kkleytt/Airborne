-- ==========================
-- SCHEMA: Airborne
-- ==========================

-- База знаний
CREATE TABLE knowledge (
    id SERIAL PRIMARY KEY NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT NOW(),
    edited TIMESTAMP NOT NULL DEFAULT NOW(),
    editor BIGINT NOT NULL, -- Telegram-Id
    type VARCHAR(16) NOT NULL, -- [file, text, keyboard]
    tag VARCHAR(64),  -- 'Любой текст'
    description TEXT, -- 'Любой текст'
    meta JSONB NOT NULL, -- {'size', 'format', 'type'}
    value TEXT -- ['Путь до файла', 'Текст', 'JSON клавиатура']
);

-- Новости
CREATE TABLE news (
    id SERIAL PRIMARY KEY NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT NOW(),
    creator BIGINT NOT NULL,
    name TEXT NOT NULL,
    tag VARCHAR(64),
    text_id INT NOT NULL,
    images_id JSONB DEFAULT '[]',
    files_id JSONB DEFAULT '[]',
    keyboard_id INT NOT NULL,
    users JSONB DEFAULT '[]',
    ignores JSONB DEFAULT '[]'
);

-- Данные пользователей
CREATE TABLE users (
    id BIGINT PRIMARY KEY NOT NULL,
    nick VARCHAR(64),
    birthday DATE,
    phone VARCHAR(16),
    name_rus TEXT,
    name_first TEXT,
    name_second TEXT,
    request_total INT DEFAULT 0 NOT NULL,
    request_first TIMESTAMP DEFAULT NOW() NOT NULL,
    request_last TIMESTAMP DEFAULT NOW() NOT NULL,
    blocked_status BOOLEAN DEFAULT FALSE NOT NULL,
    blocked_time TIMESTAMP DEFAULT NOW() NOT NULL,
    ip VARCHAR(32),
    device VARCHAR(64),
    role VARCHAR(16) DEFAULT 'user' NOT NULL,
    rating FLOAT DEFAULT 0 NOT NULL,
    description TEXT,
    groups JSONB DEFAULT '[]'
);

-- Группы пользователей
CREATE TABLE groups (
    id SERIAL PRIMARY KEY NOT NULL,
    name TEXT NOT NULL,
    tag VARCHAR(64),
    description TEXT,
    admins JSONB DEFAULT '[]' NOT NULL,
    users JSONB DEFAULT '[]' NOT NULL,
    invites JSONB DEFAULT '[]' NOT NULL,
    events JSONB DEFAULT '[]' NOT NULL
);

-- События
CREATE TABLE events (
    id SERIAL PRIMARY KEY NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    date TIMESTAMP DEFAULT NOW() NOT NULL,
    location TEXT,
    users JSONB DEFAULT '[]' NOT NULL,
    invites JSONB DEFAULT '[]' NOT NULL
);

-- Индексы
CREATE INDEX idx_knowledge_tag ON knowledge(tag);
CREATE INDEX idx_news_tag ON news(tag);
CREATE INDEX idx_users_nick ON users(nick);
CREATE INDEX idx_groups_tag ON groups(tag);