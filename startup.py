#! python3
# -*- encoding: utf-8 -*-
'''
@File    :   startup.py
@Time    :   2024/06/11 13:57:53
@Author  :   wangxh 
@Version :   1.0
@Email   :   wangxh@centn.com
'''


import asyncio

from db import migrate
from db.curds import add_user, query_user
from common import logger
from app import create_app

async def main():
    await migrate('drop')
    await migrate('init')
    user = await add_user("longfellow@gmail.com", "123456")
    user = await add_user("wangxh@gmail.com", "123456")
    
    users = await query_user()
    for user in users:
        print(user)

if __name__ == '__main__':
    import uvicorn
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
    # 异步 main 函数
    # import sys
    # if sys.version_info < (3, 10):
    #     loop = asyncio.get_event_loop()
    # else:
    #     try:
    #         loop = asyncio.get_running_loop()
    #     except RuntimeError:
    #         loop = asyncio.new_event_loop()
    
    # asyncio.set_event_loop(loop)
    
    # loop.run_until_complete(main())
