import os  # Работа с ОС
import json  # Работа с JSON строками
import zipfile  # ZIP архивация данных
from datetime import datetime, timedelta, timezone  # Работа со временем
from pathlib import Path  # Путь
from typing import Dict  # Тип данных Словарь
import requests  # Отправка HTTP запросов
from api.mysql.fastapi_app import get_url  # Получение URL API настроек


# Класс для автоматической записи логов в файл
class FileLogger:
    def __init__(self):
        # Получение настроек из API
        raw = requests.get(f"{get_url()}/secret/many?keys=log_file_settings").json()
        utc = requests.get(f"{get_url()}/secret/many?keys=log_timezone").json()

        # Распаковка JSON первого уровня
        settings = json.loads(raw.get("log_file_settings", "{}"))

        # Получение настроек из config
        self.utc = int(utc.get("log_timezone", 0))
        self.format = settings.get("filename", "YY-MM-DD.log")
        self.change_days = int(settings.get("change_days", 1))
        self.save_dir = Path(settings.get("directory", "./logger/logs/"))
        self.delete_old = settings.get("delete_logs", False)
        self.max_files = int(settings.get("max_files", 10))
        self.max_archives = int(settings.get("max_archive", 60))

        # Создание переменных для хранения актуального имени файла и даты
        self.current_file: Path = None
        self.current_date = None

        # Создание необходимых папок для сохранения файлов
        self.save_dir.mkdir(parents=True, exist_ok=True)
        (self.save_dir / "archive").mkdir(parents=True, exist_ok=True)

        # Форсированный запуск проверки на актуальность файла
        self._rotate_file(force=True)

    # Пишем лог в файл
    def log(self, entry: Dict[str, str]):
        self._rotate_file()

        # Разбор параметров
        ts = entry.get("timestamp", datetime.utcnow().isoformat())
        level = entry.get("level", "INFO")
        module = entry.get("module", "unknown")
        message = entry.get("message", "")
        code = entry.get("code", 0)

        # Форматирование времени
        try:
            # Преобразуем timestamp из ISO 8601 и явно делаем его UTC
            dt = datetime.fromisoformat(ts)
            dt = dt.replace(tzinfo=timezone.utc)

            # Применяем смещение
            tz = timezone(timedelta(hours=int(self.utc)))
            dt = dt.astimezone(tz)

            timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            timestamp = ts  # fallback

        # Форматирование строки
        log_line = f"[{timestamp}] [{level}] [{module}] {message} [code: {code}]\n"

        # Запись строки в файл
        with self.current_file.open("a", encoding="utf-8") as f:
            f.write(log_line)

    # Проверка актуальности файла, начало и окончание файла
    def _rotate_file(self, force: bool = False):
        # Получаем актуальную дату, учитывая смещение часового пояса
        tz = timezone(timedelta(hours=int(self.utc)))
        now = datetime.now(tz)
        date_key = now.date()

        # Проверяем что актуальная дата разниться с последним файлом
        if self.current_date is None or (now.date() - self.current_date).days >= self.change_days or force:

            # Проверяем что есть последний файл и завершаем его
            if self.current_file:
                with self.current_file.open("a", encoding="utf-8") as f:
                    f.write("# === END OF FILE ===\n")

            # Получаем актуальную дату и форматируем имя нового файла
            self.current_date = date_key
            file_name = now.strftime(self.format.replace("YY", "%y").replace("MM", "%m").replace("DD", "%d"))
            self.current_file = self.save_dir / file_name

            # Создаем строку для старта
            string_start = "" if self.current_file.exists() else f"# === START OF FILE: {now.strftime('%Y-%m-%d %H:%M:%S')} ===\n"

            # Создаем новый файл и добавляем в него строчку старта
            with self.current_file.open("a", encoding="utf-8") as f:
                f.write(string_start)

            # Запускаем проверку количества файлов в директории logs и archive
            self._manage_file_limits()

    # Проверка количество файлов логов в директориях
    def _manage_file_limits(self):

        # Сортируем список файлов относительно даты
        log_files = sorted(self.save_dir.glob("*.log"), key=os.path.getmtime)

        # Архивация лишних файлов
        while len(log_files) > self.max_files:
            oldest = log_files.pop(0)
            self._archive_file(oldest)

        # Удаление старых архивов
        if self.delete_old:
            archive_files = sorted((self.save_dir / "archive").glob("*.zip"), key=os.path.getmtime)
            while len(archive_files) > self.max_archives:
                archive_files.pop(0).unlink()

    # Архивация файла логов
    def _archive_file(self, file: Path):
        # Форматируем название архива
        archive_name = (self.save_dir / "archive") / f"archive_{file.stem}.zip"

        # Создаем новый архив и добавляем в него файл
        with zipfile.ZipFile(archive_name, 'w', zipfile.ZIP_DEFLATED) as archive:
            archive.write(file, arcname=file.name)

        # Заканчивает операцию с архивом
        file.unlink()
