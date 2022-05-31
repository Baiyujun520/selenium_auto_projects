# coding=utf-8

import time
import os
import sys
import logging
from logging.handlers import RotatingFileHandler

from config import conf


def get_logger():
    datefmt = "[%Y-%m-%d %H:%M:%S]"
    fmt = "%(asctime)s- %(funcName)s (%(filename)s):%(lineno)s -[%(levelname)s] %(message)s"
    formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)

    date = time.strftime("%Y-%m-%d", time.localtime(time.time()))
    log_name = date + "_pytest_execution"
    file_name = os.path.join(os.path.dirname(os.path.dirname(__file__)), "log", log_name + ".log")

    logger_handler = logging.getLogger(log_name)
    logger_handler.setLevel(logging.DEBUG)

    for handler in logger_handler.handlers:
        logger_handler.removeHandler(handler)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(fmt=formatter)
    stream_handler.setLevel(conf.common.LogConfig.logLevel.upper())

    file_handler = RotatingFileHandler(filename=file_name, maxBytes=10 * 1024 * 1024, backupCount=0)
    file_handler.setLevel(conf.common.LogConfig.logFileLevel.upper())
    file_handler.setFormatter(fmt=formatter)

    logger_handler.addHandler(stream_handler)
    logger_handler.addHandler(file_handler)

    mark = "\n" + "*" * 200 + "\n"
    start_str = "Start executing......."
    logger_handler.debug(start_str + mark)
    return logger_handler


logger = get_logger()
