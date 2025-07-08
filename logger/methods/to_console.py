import json
from datetime import datetime, timedelta
from typing import Dict, Any
from colorama import init as colorama_init, Fore, Back, Style
import requests
from api.mysql.fastapi_app import get_url

colorama_init(autoreset=True)


class ConsoleLogger:
    COLORS = {
        "black": Fore.BLACK,
        "red": Fore.RED,
        "green": Fore.GREEN,
        "yellow": Fore.YELLOW,
        "blue": Fore.BLUE,
        "magenta": Fore.MAGENTA,
        "cyan": Fore.CYAN,
        "white": Fore.WHITE,
        "None": "",  # для отсутствия цвета
    }

    HIGHLIGHTS = {
        "black": Back.BLACK,
        "red": Back.RED,
        "green": Back.GREEN,
        "yellow": Back.YELLOW,
        "blue": Back.BLUE,
        "magenta": Back.MAGENTA,
        "cyan": Back.CYAN,
        "white": Back.WHITE,
        "None": "",  # для отсутствия подложки
    }

    def __init__(self):
        try:
            # Получение настроек из API
            raw = requests.get(f"{get_url()}/secret/many?keys=log_console_settings").json()
            timezone = requests.get(f"{get_url()}/secret/many?keys=log_timezone").json()

            # Распаковка JSON первого уровня
            settings = json.loads(raw.get("log_console_settings", "{}"))

            # Получение значений
            self.columns_order = settings.get("columns", [])
            self.columns_styles = settings.get("styles", {})
            self.time_format = settings.get("time_format", "%Y-%m-%d %H:%M:%S")
            self.timezone_offset = int(timezone.get("log_timezone", 0))

        except Exception as e:
            raise ValueError(f"[Formatter] Ошибка загрузки настроек: {e}")

    def style_text(self, text: str, style: Dict[str, Any]) -> str:
        color = self.COLORS.get(style.get("color", "None"), "")
        highlight = self.HIGHLIGHTS.get(style.get("highlight", "None"), "")
        bold = Style.BRIGHT if style.get("bold", False) else ""
        underline = "\033[4m" if style.get("underline", False) else ""
        return f"{bold}{underline}{highlight}{color}{text}{Style.RESET_ALL}"

    def format_log(self, log: Dict[str, Any]) -> str:
        parts = []
        error_mode = int(log.get("code", 0)) > 200

        for column in self.columns_order:
            if not self.columns_styles.get(column, {}).get("show", False):
                continue

            value = log.get(column, "")
            style = self.columns_styles.get(column, {})

            # Преобразование timestamp в указанный формат
            if column == "timestamp" and value:
                try:
                    dt = datetime.fromisoformat(value) + timedelta(hours=self.timezone_offset)
                    value = dt.strftime(self.time_format)
                except Exception:
                    pass

            styled = self.style_text(str(value), style) if not error_mode else f"{Style.BRIGHT}{Fore.RED}{value}"
            parts.append(styled)

        return " | ".join(parts)
