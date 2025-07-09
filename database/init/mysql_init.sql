-- ==========================
-- SCHEMA: Airborne
-- ==========================

CREATE TABLE IF NOT EXISTS settings (
    `key` VARCHAR(64) NOT NULL PRIMARY KEY COMMENT 'Ключ настройки',
    `type` VARCHAR(16) NOT NULL COMMENT 'Тип значения (str, int, bool, list, dict, float)',
    `value` TEXT NOT NULL COMMENT 'Значение настройки',
    `tag` VARCHAR(64) DEFAULT NULL COMMENT 'Тэг для группировки или быстрого поиска',
    `description` TEXT DEFAULT NULL COMMENT 'Описание настройки',
    `editable` TINYINT(1) NOT NULL DEFAULT 1 COMMENT 'Может ли быть изменена вручную'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
