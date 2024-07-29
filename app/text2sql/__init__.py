#! python3
# -*- encoding: utf-8 -*-
'''
@File    : __init__.py
@Time    : 2024/07/29 11:43:01
@Author  : longfellow 
@Email   : longfellow.wang@gmail.com
@Version : 1.0
@Desc    : None
'''


import pandas as pd
from openai import OpenAI
from vanna.base import VannaBase
from vanna.qdrant import Qdrant_VectorStore

class MilvusVectorDB:
    def add_ddl(self, ddl:str, **kwargs) -> str:
        pass

    def add_document(self, doc:str, **kwargs) -> str:
        pass

    def add_question_sql(self, question:str, sql: str, **kwargs) -> str:
        pass

    def get_related_ddl(self, question:str, **kwargs) -> list:
        pass

    def get_related_document(self, question:str, **kwargs) -> list:
        pass

    def get_similar_question_sql(self, question:str, **kwargs) -> list:
        pass

    def get_training_data(self, **kwargs) -> pd.DataFrame:
        pass


    def remove_training_data(self, **kwargs) -> bool:
        pass

class CVanna(MilvusVectorDB, OpenAI):
    def __init__(self, config=None):
        MilvusVectorDB.__init__(self, config)
        OpenAI.__init__(self, base_url='', api_key='')


vn = CVanna(config={})