-- ==========================
-- SCHEMA: Airborne
-- ==========================

-- База знаний
CREATE TABLE knowledge (
    id SERIAL PRIMARY KEY,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    edited TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    editor BIGINT NOT NULL, -- Telegram-Id
    type TEXT NOT NULL, -- [file, text, keyboard]
    tag TEXT,  -- 'Любой текст'
    description TEXT, -- 'Любой текст'
    meta JSONB NOT NULL, -- {'size', 'format', 'type'}
    value TEXT -- ['Путь до файла', 'Текст', 'JSON клавиатура']
);

-- Новости
CREATE TABLE news (
    id SERIAL PRIMARY KEY,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    creator BIGINT NOT NULL,
    name TEXT NOT NULL,
    tag TEXT,
    text_id INT NOT NULL,
    images_id JSONB DEFAULT '[]',
    files_id JSONB DEFAULT '[]',
    keyboard_id INT NOT NULL,
    users JSONB DEFAULT '[]',
    ignors JSONB DEFAULT '[]'
);

-- Данные пользователей
CREATE TABLE usersdata (
    id BIGINT PRIMARY KEY,
    nick TEXT,
    birthday DATE,
    phone BIGINT,
    name_rus TEXT,
    name_first TEXT,
    name_second TEXT,
    request_total INT DEFAULT 0,
    request_first TIMESTAMP,
    request_last TIMESTAMP,
    blocked_status BOOLEAN DEFAULT FALSE,
    blocked_time TIMESTAMP DEFAULT '2200-01-01 00:00:00',
    ip TEXT,
    device TEXT,
    role TEXT DEFAULT 'user',
    rating FLOAT DEFAULT 0,
    description TEXT,
    groups JSONB DEFAULT '[]'
);

-- Группы пользователей
CREATE TABLE groups (
    id SERIAL PRIMARY KEY,
    tag TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    admins JSONB DEFAULT '[]',
    users JSONB DEFAULT '[]',
    invits JSONB DEFAULT '[]',
    events JSONB DEFAULT '[]'
);

-- События
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    date TIMESTAMP NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    location TEXT,
    users JSONB DEFAULT '[]',
    invits JSONB DEFAULT '[]'
);

-- Индексы
CREATE INDEX idx_knowledge_tag ON knowledge(tag);
CREATE INDEX idx_news_tag ON news(tag);
CREATE INDEX idx_usersdata_nick ON usersdata(nick);
CREATE INDEX idx_groups_tag ON groups(tag);