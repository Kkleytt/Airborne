-- ==========================
-- SCHEMA: Airborne
-- ==========================

-- Logs Table
CREATE TABLE IF NOT EXISTS logs (
    id SERIAL PRIMARY KEY NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW() NOT NULL,
    level VARCHAR(16) NOT NULL,
    module VARCHAR(64) NOT NULL,
    message TEXT NOT NULL,
    code INT NOT NULL
);

-- Telegram Queries Table
CREATE TABLE IF NOT EXISTS telegram_query (
    id SERIAL PRIMARY KEY NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW() NOT NULL,
    user_id BIGINT NOT NULL,
    chat_id BIGINT NOT NULL,
    query_type VARCHAR(64) NOT NULL,
    query_text TEXT NOT NULL,
    response_time INT,
    status_code INT
);

-- Превращаем в hypertable (TimeScaleDB)
SELECT create_hypertable('logs', 'timestamp', if_not_exists => TRUE);
SELECT create_hypertable('telegram_query', 'timestamp', if_not_exists => TRUE);
