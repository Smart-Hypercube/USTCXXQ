# coding=utf-8

import logging

from .config import init_logging

logger = logging.getLogger("console logger")
init_logging(logger=logger)
