#! python3
# -*- encoding: utf-8 -*-
'''
@File    : es.py
@Time    : 2024/06/13 17:13:39
@Author  : longfellow
@Version : 1.0
@Email   : longfellow.wang@gmail.com
'''


from elasticsearch import Elasticsearch, helpers

from common.singleton import Singleton

class ESClient(metaclass=Singleton):
    def __init__(self) -> None:
        pass