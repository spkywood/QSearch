#! python3
# -*- encoding: utf-8 -*-
'''
@File    :   configs.py
@Time    :   2024/06/06 13:50:04
@Author  :   wangxh 
@Version :   1.0
@Email   :   longfellow.wang@gmail.com
'''

import os
import dotenv

dotenv.load_dotenv()

VERSION = "0.0.1"

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = os.getenv("MYSQL_PORT")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

QWEN_API_KEY = os.getenv("QWEN_API_KEY")
CHATGLM_API_KEY = os.getenv("CHATGLM_API_KEY")

SQLALCHEMY_DATABASE_URI = f'mysql+aiomysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}'
