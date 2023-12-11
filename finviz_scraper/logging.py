from typing import Any
import logging
import os
from pathlib import Path
import warnings
from logging.handlers import RotatingFileHandler


warnings.simplefilter(action="ignore", category=FutureWarning)


log = logging.getLogger("main")
level = logging.DEBUG
log.setLevel(level)


formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")


def generate_log_dir():
    dir = "./logs"
    os.makedirs(dir, exist_ok=True)
    Path("./logs/main.log").touch()


def get_file_handler(level: Any):
    fh = RotatingFileHandler("logs/main.log", maxBytes=5000000, backupCount=3)
    fh.setLevel(level)
    fh.setFormatter(formatter)
    return fh


def get_stream_handler(level: Any):
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(formatter)
    return ch


if not len(log.handlers):
    generate_log_dir()
    fh = get_file_handler(level)
    log.addHandler(fh)

    ch = get_stream_handler(level)
    log.addHandler(ch)


def get_log() -> logging.Logger:
    return log
