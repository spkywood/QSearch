#! python3
# -*- encoding: utf-8 -*-
'''
@File    : logger.py
@Time    : 2024/06/11 16:37:37
@Author  : longfellow
@Version : 1.0
@Email   : longfellow.wang@gmail.com
'''


import sys

def Logger():
    from loguru import logger
    logger.add(
        sys.stderr,
        format="{time} {level} {message}",
        filter="my_module", level="INFO",
    )
    logger.add(
        "log/runtime_{time}.log",
        rotation='00:00', retention='7 days',
    )

    return logger

logger = Logger()