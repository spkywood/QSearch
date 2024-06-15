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

from db import migrate
from db.curds import add_user, query_user

async def main():
    await migrate('drop')
    await migrate('init')
    # name, email, phone, password
    user = await add_user("user1", "test1@abc.com", "13161997860", "123456")
    user = await add_user("user2", "test2@abc.com", "13161997861", "123456")
    user = await add_user("user3", "test3@abc.com", "13161997862", "123456")
    user = await add_user("user4", "test4@abc.com", "13161997863", "123456")
    user = await add_user("user5", "test5@abc.com", "13161997864", "123456")
    user = await add_user("user6", "test6@abc.com", "13161997865", "123456")
    
    users = await query_user()
    for user in users:
        print(user)

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
