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

from app.core.singleton import Singleton
from logger import logger
class ESClient(metaclass=Singleton):
    mappings = {
        "mappings": {
            "properties": {
                "kb_name": {"type": "keyword"},
                "file_name": {"type": "keyword"},
                "chunk_id": {"type": "integer"},
                "chunk_uuid": {"type": "keyword"},
                "chunk": {"type": "text", "analyzer": "standard"},
                "metadata": {
                    "type": "text",
                    "fields": {
                        "keyword": {"type": "keyword", "ignore_above": 256}
                    }
                },
                "created_at": {"type": "date"}
            }
        }
    }

    def __init__(self, host='localhost', port='9200', scroll='2m', size = 3) -> None:
        self.scroll = scroll
        self.size = size
        self.es = Elasticsearch(f"http://{host}:{port}")

    def create_index(self, index_name: str):
        if not self.es.indices.exists(index=index_name):
            self.es.indices.create(index=index_name, body=ESClient.mappings)
        else:
            logger.info(f"Index '{index_name}' already exists.")


    def insert(self, index_name, chunks):
        def gendata(chunks):
            for chunk in chunks:
                yield {
                    "_index": index_name,
                    "_source": chunk
                }
        
        helpers.bulk(self.es, gendata(chunks=chunks))

    def search(self, index_name, query):
        response = self.es.search(
            index=index_name,
            body={
                "query": {
                    "match": {
                        "chunk": query
                    }
                },
                "size": self.size
            },
            scroll=self.scroll
        )
        
        self.es.clear_scroll(body={"scroll_id": response['_scroll_id']})
        return response['hits']['hits']

    # 删除索引
    def delete_index(self, index_name):
        try:
            if self.es.indices.exists(index=index_name):
                self.es.indices.delete(index=index_name)
                logger.info(f"Index '{index_name}' deleted successfully.")
            else:
                logger.info(f"Index '{index_name}' does not exist.")
        except Exception as e:
            logger.info(f"Failed to delete index '{index_name}': {e}")

from settings import ES_HOST, ES_PORT

es_client = ESClient(host=ES_HOST, port=ES_PORT)
