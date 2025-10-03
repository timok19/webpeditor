import logging
import os
from enum import StrEnum
from http import HTTPMethod
from typing import Final


class _Colors(StrEnum):
    BLACK = "black"
    RED = "red"
    GREEN = "green"
    YELLOW = "yellow"
    BLUE = "blue"
    MAGENTA = "magenta"
    CYAN = "cyan"
    WHITE = "white"
    BRIGHT_BLACK = "bright_black"
    BRIGHT_RED = "bright_red"
    BRIGHT_GREEN = "bright_green"
    BRIGHT_YELLOW = "bright_yellow"
    BRIGHT_BLUE = "bright_blue"
    BRIGHT_MAGENTA = "bright_magenta"
    BRIGHT_CYAN = "bright_cyan"
    BRIGHT_WHITE = "bright_white"


class ColorFormatter(logging.Formatter):
    USE_COLOR: Final[bool] = True if not os.getenv("NO_COLOR") else False
    RESET: Final[str] = "\033[0m"
    BOLD: Final[str] = "\033[1m"
    DIM: Final[str] = "\033[2m"
    FG: Final[dict[_Colors, str]] = {
        _Colors.BLACK: "\033[30m",
        _Colors.RED: "\033[31m",
        _Colors.GREEN: "\033[32m",
        _Colors.YELLOW: "\033[33m",
        _Colors.BLUE: "\033[34m",
        _Colors.MAGENTA: "\033[35m",
        _Colors.CYAN: "\033[36m",
        _Colors.WHITE: "\033[37m",
        _Colors.BRIGHT_BLACK: "\033[90m",
        _Colors.BRIGHT_RED: "\033[91m",
        _Colors.BRIGHT_GREEN: "\033[92m",
        _Colors.BRIGHT_YELLOW: "\033[93m",
        _Colors.BRIGHT_BLUE: "\033[94m",
        _Colors.BRIGHT_MAGENTA: "\033[95m",
        _Colors.BRIGHT_CYAN: "\033[96m",
        _Colors.BRIGHT_WHITE: "\033[97m",
    }

    LEVEL_COLORS: Final[dict[int, str]] = {
        logging.DEBUG: BOLD + FG[_Colors.BLUE],
        logging.INFO: BOLD + FG[_Colors.BRIGHT_WHITE],
        logging.WARNING: BOLD + FG[_Colors.BRIGHT_YELLOW],
        logging.ERROR: BOLD + FG[_Colors.BRIGHT_RED],
        logging.CRITICAL: BOLD + FG[_Colors.BRIGHT_RED],
    }

    HTTP_METHOD_COLORS: Final[dict[str, str]] = {
        HTTPMethod.GET: BOLD + FG[_Colors.BLUE],
        HTTPMethod.POST: BOLD + FG[_Colors.GREEN],
        HTTPMethod.PUT: BOLD + FG[_Colors.YELLOW],
        HTTPMethod.PATCH: BOLD + FG[_Colors.YELLOW],
        HTTPMethod.DELETE: BOLD + FG[_Colors.RED],
        HTTPMethod.OPTIONS: BOLD + FG[_Colors.BLUE],
        HTTPMethod.HEAD: BOLD + FG[_Colors.BRIGHT_BLACK],
    }

    def format(self, record: logging.LogRecord) -> str:
        level_color = self.LEVEL_COLORS.get(record.levelno, self.FG[_Colors.WHITE])

        colorized_datetime = self.__colorize(self.FG[_Colors.GREEN], self.formatTime(record, self.datefmt))
        colorized_levelname = self.__colorize(level_color, f"{record.levelname:<8}")
        colorized_name = self.__colorize(self.FG[_Colors.CYAN], record.name)

        colorized_message = self.__colorize(level_color, record.getMessage())

        result = f"{colorized_datetime} {colorized_levelname} {colorized_name} - {colorized_message}"

        if record.exc_info:
            exc_text = self.formatException(record.exc_info)
            result = f"{result}\n{exc_text}"

        if record.stack_info:
            result = f"{result}\n{self.formatStack(record.stack_info)}"

        return result

    def __colorize(self, color_code: str, text: str, bold: bool = False) -> str:
        return (
            f"{self.BOLD if bold and not color_code.startswith(self.BOLD) else ''}{color_code}{text}{self.RESET}"
            if self.USE_COLOR
            else text
        )
