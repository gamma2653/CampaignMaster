import contextlib
import logging
import os
import sys
import threading

# TODO: Use settings.py logging config instead
_DEFAULT_LEVEL = "INFO"
_CM_LOG_LEVEL = os.getenv("CM_LOG_LEVEL", _DEFAULT_LEVEL).upper() or _DEFAULT_LEVEL
try:
    CM_LOG_LEVEL = logging.getLevelNamesMapping()[_CM_LOG_LEVEL]  # Validate log level
except KeyError:
    print(f"Invalid CM_LOG_LEVEL '{_CM_LOG_LEVEL}'")
    sys.exit(1)


def get_basic_formatter() -> logging.Formatter:
    return logging.Formatter(
        "[%(name)s:%(levelname)s](%(asctime)s):`%(message)s`",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def get_basic_logger(name: str, level: int = CM_LOG_LEVEL) -> logging.Logger:
    """
    Creates and returns a basic logger with the specified name.

    Args:
        name (str): The name of the logger.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        logger.setLevel(level)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(get_basic_formatter())
        logger.addHandler(handler)
    return logger


def setup_file_logging(log_file_path: str, level: int = logging.DEBUG) -> logging.FileHandler:
    """
    Creates and returns a file handler for logging.

    Args:
        log_file_path (str): Path to the log file.
        level (int): Log level for the file handler. Defaults to DEBUG.

    Returns:
        logging.FileHandler: Configured file handler.
    """
    from pathlib import Path

    log_path = Path(log_file_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    file_handler = logging.FileHandler(log_file_path, mode="a", encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(get_basic_formatter())
    return file_handler


def get_uvicorn_log_config(log_file_path: str) -> dict:
    """
    Creates a uvicorn logging configuration dict that logs to both console and file.

    Args:
        log_file_path (str): Path to the log file.

    Returns:
        dict: Uvicorn logging configuration.
    """
    from pathlib import Path

    log_path = Path(log_file_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "[%(name)s:%(levelname)s](%(asctime)s):`%(message)s`",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "access": {
                "format": "[%(name)s:%(levelname)s](%(asctime)s):`%(client_addr)s - %(request_line)s %(status_code)s`",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "default": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": "ext://sys.stdout",
            },
            "access": {
                "class": "logging.StreamHandler",
                "formatter": "access",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.FileHandler",
                "formatter": "default",
                "filename": str(log_file_path),
                "mode": "a",
                "encoding": "utf-8",
            },
            "access_file": {
                "class": "logging.FileHandler",
                "formatter": "access",
                "filename": str(log_file_path),
                "mode": "a",
                "encoding": "utf-8",
            },
        },
        "loggers": {
            "uvicorn": {
                "handlers": ["default", "file"],
                "level": "DEBUG",
                "propagate": False,
            },
            "uvicorn.error": {
                "handlers": ["default", "file"],
                "level": "DEBUG",
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["access", "access_file"],
                "level": "DEBUG",
                "propagate": False,
            },
            "fastapi": {
                "handlers": ["default", "file"],
                "level": "DEBUG",
                "propagate": False,
            },
        },
    }


# From my 2022 CUP Robotics work
# https://github.com/cornell-cup/c1c0-scheduler/blob/archive/grpc-impl/c1c0_scheduler/utils.py


class ReaderWriterSuite:
    """
    Standard Reader Writer
    """

    # Based on wikipedia:
    #   https://en.wikipedia.org/wiki/Readers%E2%80%93writer_lock

    g = threading.Lock()
    writer_active_con = threading.Condition(g)
    writer_active = False
    num_writers_waiting = 0
    num_readers_active = 0

    @contextlib.contextmanager
    def reader(self):
        self.acquire_reader()
        yield
        self.release_reader()

    @contextlib.contextmanager
    def writer(self):
        self.acquire_writer()
        yield
        self.release_writer()

    def acquire_reader(self):
        with self.g:
            while self.num_writers_waiting > 0 or self.writer_active:
                self.writer_active_con.wait()
            self.num_readers_active += 1

    def release_reader(self):
        with self.g:
            self.num_readers_active -= 1
            if self.num_readers_active == 0:
                self.writer_active_con.notify_all()

    def acquire_writer(self):
        with self.g:
            self.num_writers_waiting += 1
            while self.num_readers_active > 0 or self.writer_active:
                self.writer_active_con.wait()
            self.num_writers_waiting -= 1
            self.writer_active = True

    def release_writer(self):
        with self.g:
            self.writer_active = False
            self.writer_active_con.notify_all()
