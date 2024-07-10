#! python3
# -*- encoding: utf-8 -*-
'''
@File    :   migrate.py
@Time    :   2024/06/06 14:11:01
@Author  :   wangxh 
@Version :   1.0
@Email   :   longfellow.wang@gmail.com
'''


from app.models import * # 解释器需要 import Base子类
"""
动态导入方法
MODEL_MODULES = [
    'app.models.user',
    'app.models.address',
]
for module_name in MODEL_MODULES:
    __import__(module_name)
"""


from db.database import db_engine, Base

async def create_tables():
    async with db_engine.begin() as conn:
        await conn.run_sync(BaseTable.metadata.create_all)

async def drop_tables():
    async with db_engine.begin() as conn:
        await conn.run_sync(BaseTable.metadata.drop_all)
