#! python3
# -*- encoding: utf-8 -*-
'''
@File    : database.py
@Time    : 2024/06/11 15:06:10
@Author  : longfellow
@Version : 1.0
@Email   : longfellow.wang@gmail.com
'''


from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base
from setting import SQLALCHEMY_DATABASE_URI

db_engine = create_async_engine(
    SQLALCHEMY_DATABASE_URI, echo=False, future=True,
    pool_pre_ping=True,  # 检查连接是否有效
    pool_recycle=3600    # 每小时回收连接
)

SessionLocal = async_sessionmaker(
    db_engine, expire_on_commit=False, class_=AsyncSession
)

Base = declarative_base()