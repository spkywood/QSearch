#! python3
# -*- encoding: utf-8 -*-
'''
@File    :   startup.py
@Time    :   2024/06/11 13:57:53
@Author  :   wangxh 
@Version :   1.0
@Email   :   longfellow.wang@gmail.com
'''


from app import create_app

if __name__ == '__main__':
    import uvicorn
    app = create_app()
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8009,
        loop="uvloop",
        http="httptools"
    )
    