#! python3
# -*- encoding: utf-8 -*-
'''
@File    : milvus.py
@Time    : 2024/06/13 16:54:09
@Author  : longfellow
@Version : 1.0
@Email   : longfellow.wang@gmail.com
'''


from typing import List
from pymilvus import (
    connections,
    DataType,
    Collection,
    FieldSchema,
    MilvusClient,
    MilvusException,
    CollectionSchema,
)
from common.singleton import Singleton

class Milvus(metaclass=Singleton):
    """
    Milvus 存储 查询
    """

    @staticmethod
    def create_schema(dim: int = 1024) -> CollectionSchema:
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="kb_name", dtype=DataType.VARCHAR, max_length=100, is_partition_key=True),
            FieldSchema(name="chunk", dtype=DataType.VARCHAR, max_length=20000),
            FieldSchema(name="chunk_uuid", dtype=DataType.VARCHAR, max_length=100),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=dim),
            FieldSchema(name="metadata", dtype=DataType.JSON)
        ]

        return CollectionSchema(fields=fields, description="Chunk Vector Collection.")
    
    def __init__(self, host: str = "localhost", port: int = 19530):
        self.client = MilvusClient(f"http://{host}:{port}")
        connections.connect(host=host, port=port)
    
    def create_collection(self, collection_name: str, dim: int, metric_type: str = "L2") -> Collection:
        schema = Milvus.create_schema(dim)

        index_params = self.client.prepare_index_params(
            "vector", metric_type=metric_type, index_type="IVF_FLAT", nlist=1024
        )

        return self.client.create_collection(collection_name, schema, index_params=index_params)
    
    def insert(self, collection_name: str, entities: List) -> int:
        pass

    def search(self, collection_name: str, query_vector: List,
               top_k:int = 3, kb_names: List[str] = None,
               expr:str = None,
               consistency_level:str = "Eventually",) -> List[str]:
        pass