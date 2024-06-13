#! python3
# -*- encoding: utf-8 -*-
'''
@File    :   migrate.py
@Time    :   2024/06/06 14:11:01
@Author  :   wangxh 
@Version :   1.0
@Email   :   wangxh@centn.com
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

async def migrate(action: str = 'init'):
    async with db_engine.begin() as conn:
        if action == 'init':
            await conn.run_sync(BaseTable.metadata.create_all)
            return
        if action == 'drop':
            await conn.run_sync(BaseTable.metadata.drop_all)
            return
        
        raise ValueError(f'Unsupported db action: {action}')

