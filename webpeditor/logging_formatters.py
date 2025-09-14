from http import HTTPMethod
import logging
import os
from typing import ClassVar, Optional

from django.http import HttpResponse


class ColorFormatter(logging.Formatter):
    USE_COLOR: ClassVar[bool] = True if not os.getenv("NO_COLOR") else False
    RESET: ClassVar[str] = "\033[0m"
    BOLD: ClassVar[str] = "\033[1m"
    DIM: ClassVar[str] = "\033[2m"
    FG: ClassVar[dict[str, str]] = {
        "black": "\033[30m",
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
        "bright_black": "\033[90m",
        "bright_red": "\033[91m",
        "bright_green": "\033[92m",
        "bright_yellow": "\033[93m",
        "bright_blue": "\033[94m",
        "bright_magenta": "\033[95m",
        "bright_cyan": "\033[96m",
        "bright_white": "\033[97m",
    }

    LEVEL_COLORS: ClassVar[dict[int, str]] = {
        logging.DEBUG: FG["blue"],
        logging.INFO: FG["bright_white"],
        logging.WARNING: FG["bright_yellow"],
        logging.ERROR: FG["bright_red"],
        logging.CRITICAL: BOLD + FG["bright_red"],
    }

    HTTP_METHOD_COLORS: ClassVar[dict[str, str]] = {
        HTTPMethod.GET: FG["cyan"],
        HTTPMethod.POST: BOLD + FG["green"],
        HTTPMethod.PUT: FG["yellow"],
        HTTPMethod.PATCH: FG["yellow"],
        HTTPMethod.DELETE: BOLD + FG["red"],
        HTTPMethod.OPTIONS: FG["blue"],
        HTTPMethod.HEAD: FG["bright_black"],
    }

    def format(self, record: logging.LogRecord) -> str:
        level_color = self.LEVEL_COLORS.get(record.levelno, self.FG["white"])

        colorized_datetime = self.__colorize(self.FG["green"], self.formatTime(record, self.datefmt))
        colorized_levelname = self.__colorize(level_color, f"{record.levelname:<8}")
        colorized_name = self.__colorize(self.FG["cyan"], record.name)

        status_code = self.__get_status_code()
        colorized_message = self.__colorize(level_color, f"{record.getMessage()} {f'- {status_code}' if status_code else ''}")

        result = f"{colorized_datetime} {colorized_levelname} {colorized_name} - {colorized_message}"

        if record.exc_info:
            exc_text = self.formatException(record.exc_info)
            result = f"{result}\n{exc_text}"

        if record.stack_info:
            result = f"{result}\n{self.formatStack(record.stack_info)}"

        return result

    def __colorize(self, color_code: str, text: str, bold: bool = False) -> str:
        if not self.USE_COLOR:
            return text

        prefix = self.BOLD if bold and not color_code.startswith(self.BOLD) else ""
        return f"{prefix}{color_code}{text}{self.RESET}"

    @staticmethod
    def __get_status_code() -> Optional[int]:
        try:
            from ninja_extra.constants import ROUTE_CONTEXT_VAR

            context = ROUTE_CONTEXT_VAR.get()
            if context is None:
                return None

            response = context.response
            if not isinstance(response, HttpResponse):
                return None

            return response.status_code
        except Exception:
            return None
