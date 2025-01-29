"""
logging handling module to create custom and particular loggers.
"""

import os
import logging
import datetime
from typing import Literal
from colorlog.formatter import ColoredFormatter
from configparser import ConfigParser

LogLevelType = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] | None

DEFAULT_LOG_LEVEL: LogLevelType = "INFO"


class ColorfulFormatter(ColoredFormatter):
    pass


def get_logger(
    name: str = "worldmodel-app",
    log_level: LogLevelType = DEFAULT_LOG_LEVEL,
):
    # create logger
    logger = logging.getLogger(name=name)

    # set log level
    if log_level is not None:
        logger.setLevel(log_level)

    # Disable propagation to avoid duplicate logs
    # logger.propagate = False

    # Remove all existing handlers before adding the custom one
    if logger.hasHandlers():
        logger.handlers.clear()

    # set logger handler and formatting
    console_handler = logging.StreamHandler()
    formatter = ColorfulFormatter(
        fmt="{log_color}{levelname} : {asctime} - {light_yellow}{name}{reset} : {message}{reset}",
        style="{",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Read path from CONFIG
    config = ConfigParser()
    config.read('config.ini')
    log_dir = config.get('logging', 'log_dir', fallback='LOGS')

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file_name = os.path.join(log_dir, f"app-log-{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}")

    file_handler = logging.FileHandler(log_file_name)
    file_handler.setFormatter(
        logging.Formatter(fmt="%(levelname)s : %(asctime)s - %(name)s - %(message)s")
    )
    logger.addHandler(file_handler)

    return logger
