#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from loguru import logger

def start():
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")


@logger.catch
def catch():
    x = 1 / 0


if __name__ == "__main__":
    logger.add(sys.stdout, enqueue=True)
    start()
    catch()
