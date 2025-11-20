import logging
import os
from enum import StrEnum
from typing import Final


class _Colors(StrEnum):
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"


class _Style(StrEnum):
    RESET = "\033[0m"
    BOLD = "\033[1m"


class ColorFormatter(logging.Formatter):
    USE_COLOR: Final[bool] = True if not os.getenv("NO_COLOR") else False
    LEVEL_COLORS: Final[dict[int, str]] = {
        logging.DEBUG: _Style.BOLD + _Colors.BLUE,
        logging.INFO: _Style.BOLD + _Colors.BRIGHT_WHITE,
        logging.WARNING: _Style.BOLD + _Colors.BRIGHT_YELLOW,
        logging.ERROR: _Style.BOLD + _Colors.BRIGHT_RED,
        logging.CRITICAL: _Style.BOLD + _Colors.BRIGHT_RED,
    }

    def format(self, record: logging.LogRecord) -> str:
        level_color = self.LEVEL_COLORS.get(record.levelno, _Colors.WHITE)

        colorized_datetime = self.__colorize_or_default(_Colors.GREEN, self.formatTime(record, self.datefmt))
        colorized_levelname = self.__colorize_or_default(level_color, f"{record.levelname:<8}")
        colorized_name = self.__colorize_or_default(_Colors.CYAN, record.name)
        colorized_message = self.__colorize_or_default(level_color, record.getMessage())

        result = f"{colorized_datetime} {colorized_levelname} {colorized_name} - {colorized_message}"

        if record.exc_info is not None:
            result = f"{result}\n{self.formatException(record.exc_info)}"

        if record.stack_info is not None:
            result = f"{result}\n{self.formatStack(record.stack_info)}"

        return result

    def __colorize_or_default(self, level_color: str, text: str) -> str:
        return f"{level_color}{text}{_Style.RESET}" if self.USE_COLOR else text
