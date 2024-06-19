#! python3
# -*- encoding: utf-8 -*-
'''
@File    :   startup.py
@Time    :   2024/06/11 13:57:53
@Author  :   wangxh 
@Version :   1.0
@Email   :   longfellow.wang@gmail.com
'''


import asyncio

from db.migrate import drop_tables, create_tables
from db.curds import add_user, query_user

async def main():
    await drop_tables()
    await create_tables()
    

if __name__ == '__main__':
    # 异步 main 函数
    import sys
    if sys.version_info < (3, 10):
        loop = asyncio.get_event_loop()
    else:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
    
    asyncio.set_event_loop(loop)
    
    loop.run_until_complete(main())
