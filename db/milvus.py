#! python3
# -*- encoding: utf-8 -*-
'''
@File    : milvus.py
@Time    : 2024/06/13 16:54:09
@Author  : longfellow
@Version : 1.0
@Email   : longfellow.wang@gmail.com
'''


from typing import List, Dict
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
from common import logger

class MilvusStore(metaclass=Singleton):
    """
    Milvus 存储 查询
    """

    @staticmethod
    def create_schema(dim: int = 1024) -> CollectionSchema:
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="kb_name", dtype=DataType.VARCHAR, max_length=100, is_partition_key=True),
            FieldSchema(name="chunk_text", dtype=DataType.VARCHAR, max_length=20000),
            FieldSchema(name="chunk_uuid", dtype=DataType.VARCHAR, max_length=100),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=dim),
            FieldSchema(name="metadata", dtype=DataType.JSON)
        ]

        return CollectionSchema(fields=fields, description="Chunk Vector Collection.")
    
    def __init__(self, host, port) -> None:
        self.client = MilvusClient(f"http://{host}:{port}")
        connections.connect(host=host, port=port)

    def has_collection(self, collection_name) -> bool:
        return self.client.has_collection(collection_name)
    
    def get_collection(self, collection_name) -> Collection:
        has = self.client.has_collection(collection_name)
        if has:
            # connections.connect()
            return Collection(collection_name)
        else:
            raise MilvusException(
                code=404, message=f"Collection {collection_name} already exists")

    def list_collections(self) -> List[str]:
        return self.client.list_collections()

    def create_collection(self, collection_name, dim, metric_type="L2"):
        has = self.client.has_collection(collection_name)
        if has:
            logger.info(f"Collection {collection_name} already exists")
            # raise MilvusException(
            #     code=510, message=f"Collection {collection_name} already exists")
        else: 
            schema = MilvusStore.create_schema(dim)
            index_params = self.client.prepare_index_params("embedding", metric_type=metric_type)

            return self.client.create_collection(collection_name, schema=schema, index_params=index_params)

    def insert(self, collection_name: str, entities: List):
        if not self.has_collection(collection_name):
            raise MilvusException(
                code=404, message=f"Collection {collection_name} does not exist"
            )
        self.client.insert(collection_name, entities)

    def insert_entities_with_collection(self, collection: Collection, entities: List):
        collection.insert(entities)

    def query_entities(self, collection_name: str, filter: str, top_k: int) -> List[Dict]:
        if not self.has_collection(collection_name):
            raise MilvusException(
                code=404, message=f"Collection {collection_name} does not exist"
            )
        
        
        return self.client.query(collection_name, filter=filter, top_k=top_k)
    
    """
    TODO: 布尔表达式
        https://www.milvus-io.com/boolean
    """
    def search(self, collection_name: str, 
               query_embedding: List,
               top_k: int = 3,
               expr: str = None,
               consistency_level: str = "Eventually") -> List[Dict]:
        if not self.has_collection(collection_name):
            raise MilvusException(
                code=404, message=f"Collection {collection_name} does not exist"
            )

        collection = self.get_collection(collection_name)
        collection.load()
        search_param = {
            "expr": expr,
            "data": [query_embedding],
            "anns_field": "embedding",
            "param": {"metric_type": "L2", "params": {"nprobe": 10}},
            "limit": top_k,
            "output_fields": ["uuid"],
            "consistency_level": consistency_level
        }
        logger.info("search..." if expr is None else "hybrid search...")
        
        results = collection.search(**search_param)
        return [r.to_dict().get("entity").get("uuid") for result in results for r in result]
