import logging
import os
from typing import ClassVar, Final, Optional


class NinjaRequestMessageFilter(logging.Filter):
    """
    Rewrites ninja-extra request log messages (emitted via logger "django.request").

    Original example message (from ninja-extra):
      "POST - Controller[action] /path" 1.234

    Desired message:
      HTTP POST - Controller[action] /path 1.234 seconds - 200
    """

    METHODS: ClassVar[tuple[str, ...]] = ("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD")

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            # Operate only on django.request logger to be safe
            if record.name != "django.request":
                return True

            message = record.getMessage() if hasattr(record, "getMessage") else record.msg
            if not isinstance(message, str):
                return True

            message = message.strip()

            # Pattern 1: message starts with quoted part then duration and optional status
            # Example: "POST - Controller[action] /api" 4.36 200
            if message.startswith('"'):
                closing = message.find('"', 1)
                if closing != -1:
                    inside = message[1:closing]
                    rest = message[closing + 1 :].lstrip()
                    record.msg = self._compose(inside, rest)
                    record.args = None
                    return True

            # Pattern 2: message starts directly with METHOD - ...
            upper = message.upper()
            if any(upper.startswith(m) for m in self.METHODS):
                # Append status code if available
                status_code = self._get_status_code()
                record.msg = f"HTTP {message}" + (f" - {status_code}" if status_code is not None else "")
                record.args = None
                return True

            return True
        except Exception:
            # Never break logging; pass original record
            return True

    def _compose(self, inside: str, rest: str) -> str:
        """Compose the final HTTP message using the parsed pieces.
        - inside: the inner "METHOD - Controller[action] /path"
        - rest: the remainder after the closing quote (can contain duration and/or status code or be empty)
        """
        duration_s: Optional[float] = None
        status_code: Optional[int] = None

        tokens = rest.strip().split()
        # Try to parse up to two numeric tokens: duration(float) and status(int)
        if any(tokens):
            # First token might be duration (float) or status (int)
            t0 = tokens[0]
            try:
                # duration usually is a float seconds in ninja-extra
                duration_s = float(t0)
            except Exception:
                if t0.isdigit():
                    status_code = int(t0)
            # Second token could be status code when duration was first
            if len(tokens) > 1 and status_code is None:
                t1 = tokens[1]
                if t1.isdigit():
                    status_code = int(t1)

        # If status_code still unknown, try to fetch from context var
        if status_code is None:
            status_code = self._get_status_code()

        parts: list[str] = [f"HTTP {inside}"]
        if duration_s is not None:
            parts.append(f"{round(duration_s, 2)} seconds")
        if status_code is not None:
            parts.append(f"- {status_code}")

        return " ".join(parts)

    @staticmethod
    def _get_status_code() -> Optional[int]:
        """Try to obtain the current response status_code from ninja-extra context.
        Falls back to None if unavailable.
        """
        try:
            from ninja_extra.constants import ROUTE_CONTEXT_VAR

            ctx = ROUTE_CONTEXT_VAR.get()
            # ctx may be None or may not have response yet; be defensive
            response = getattr(ctx, "response", None)
            status = getattr(response, "status_code", None)
            return int(status) if status is not None else None
        except Exception:
            return None


class ColorFormatter(logging.Formatter):
    """A lightweight ANSI color formatter for console logs.

    - Colors timestamp (dim), level name (per severity), logger name (cyan).
    - If message starts with "HTTP <METHOD>", colors the HTTP prefix dim and method brightly.
    - Designed for use with StreamHandler; uses colors when running in a TTY and NO_COLOR is not set.
    """

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
        # Loguru-aligned palette with INFO as white per project preference
        logging.DEBUG: FG["bright_blue"],
        logging.INFO: FG["bright_white"],
        logging.WARNING: FG["bright_yellow"],
        logging.ERROR: FG["bright_red"],
        logging.CRITICAL: BOLD + FG["bright_red"],
    }

    HTTP_METHOD_COLORS: ClassVar[dict[str, str]] = {
        "GET": FG["cyan"],
        "POST": BOLD + FG["green"],
        "PUT": FG["yellow"],
        "PATCH": FG["yellow"],
        "DELETE": BOLD + FG["red"],
        "OPTIONS": FG["blue"],
        "HEAD": FG["bright_black"],
    }

    def format(self, record: logging.LogRecord) -> str:
        # Time with milliseconds: use logging.Formatter default which already includes milliseconds
        ts = self.formatTime(record, self.datefmt)

        # Colors
        level_color = self.LEVEL_COLORS.get(record.levelno, self.FG["white"])

        # Timestamp in green
        ts_colored = self._color(self.FG["green"], ts)

        # Level name padded to width 8, then colored
        level_padded = f"{record.levelname:<8}"
        levelname_colored = self._color(level_color, level_padded)

        # Logger name in blue
        name_colored = self._color(self.FG["cyan"], record.name)

        # Message colored like Loguru: color the entire message with the level color
        message = record.getMessage()
        # message_colored = self._color(level_color, message)
        message_colored = self._colorize_http_message(level_color, message)

        # Base line with hyphen separator and single space between level and logger
        line = f"{ts_colored} {levelname_colored} {name_colored} - {message_colored}"

        # Exceptions/stack
        if record.exc_info:
            exc_text = self.formatException(record.exc_info)
            line = f"{line}\n{exc_text}"

        if record.stack_info:
            line = f"{line}\n{self.formatStack(record.stack_info)}"

        return line

    def _colorize_http_message(self, level_color: str, message: str) -> str:
        http_prefix: Final[str] = "HTTP "

        if not self.USE_COLOR or not message.startswith(http_prefix):
            return message

        # Specific handling for our rewritten HTTP messages
        message_rest = message[5:]

        # method is up to first space or hyphen
        method_end = message_rest.find(" ")

        if method_end == -1:
            method_end = len(message_rest)

        method = message_rest[:method_end].upper()
        colorized_message = self._color(level_color, message_rest[method_end:])
        colorized_http_method = self._color(self.HTTP_METHOD_COLORS.get(method, self.FG["bright_white"]), method, bold=True)

        return f"{self._dim(http_prefix)}{colorized_http_method}{colorized_message}"

    def _dim(self, text: str) -> str:
        return f"{self.DIM}{text}{self.RESET}" if self.USE_COLOR else text

    def _color(self, color_code: str, text: str, bold: bool = False) -> str:
        if not self.USE_COLOR:
            return text

        prefix = self.BOLD if bold and not color_code.startswith(self.BOLD) else ""
        return f"{prefix}{color_code}{text}{self.RESET}"
