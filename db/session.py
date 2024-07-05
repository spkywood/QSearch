#! python3
# -*- encoding: utf-8 -*-
'''
@File    : session.py
@Time    : 2024/06/06 13:51:41
@Author  : longfellow
@Version : 1.0
@Email   : longfellow.wang@gmail.com
'''


from functools import wraps
from contextlib import asynccontextmanager

from logger import logger
from db.database import SessionLocal

@asynccontextmanager
async def session_scope():
    async with SessionLocal() as session:
        async with session.begin():
            yield session

def with_session(func):
    """
    数据库操作装饰器
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        async with session_scope() as session:
            return await func(session, *args, **kwargs)
    
    return wrapper
