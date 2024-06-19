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

MAX_CONCURRENT_THREADS = 10

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")

APP_SECRET_KEY = os.getenv("APP_SECRET_KEY")

MODEL_PATH = os.getenv("MODEL_PATH")

APP_HOST = os.getenv("APP_HOST")

# ES
ES_HOST = os.getenv("ES_HOST")
ES_PORT = os.getenv("ES_PORT")

# MILVUS
MILVUS_HOST = os.getenv("MILVUS_HOST")
MILVUS_PORT = os.getenv("MILVUS_PORT")