#! python3
# -*- encoding: utf-8 -*-
'''
@File    : __init__.py
@Time    : 2024/07/05 14:24:55
@Author  : longfellow 
@Email   : longfellow.wang@gmail.com
@Version : 1.0
@Desc    : None
'''


from typing import List
from app.core.cache import model_manager
from app.core.singleton import Singleton
from app.runtime.reranker import Reranker
from app.runtime.embedding import Embedding
from app.schemas.llm import ModelType

from db import minio_client, milvus_client, es_client

class RAG(metaclass=Singleton):
    embedding: Embedding = model_manager.load_models(
        model='BAAI/bge-large-zh-v1.5', 
        device='cuda', 
        model_type=ModelType.EMBEDDING
    )

    reranker: Reranker = model_manager.load_models(
        model='BAAI/bge-reranker-base', 
        device='cuda', 
        model_type=ModelType.RERANKER
    )

    def __init__(self):
        pass

    def _vector_search(self, query_vector, kb_name: str, expr: str = None):
        result = milvus_client.search(kb_name, query_vector, expr=expr)
        return result
    
    def _bm25_search(self, question: str, kb_name: str):
        results = es_client.search(kb_name, question)
        return [result['_source']['chunk_uuid'] for result in results]

    def search(self, question: str, kb_name: str, expr: str = None):
        query_vector = self.embedding.encode(question)[0].tolist()

        vector_result = self._vector_search(query_vector, kb_name)
        bm25_result = self._bm25_search(question, kb_name)
    
        uuids = list(set(vector_result + bm25_result))

        return uuids
    

    def get_obj_url(self, kb_name: str, file_name: str):
        return minio_client.get_obj_url(kb_name, file_name)
    
    def postprocess(self, question: str, documents: List):
        scores = self.reranker.compute_score(question, documents)
        top = sorted(scores, key=lambda x: x['score'], reverse=True)

        return top
    
    def get_source(self, answer: str, background_knowledge: str):
        bks = [item for bk in background_knowledge.split('\n\n') if bk.strip() for item in bk.split('\n') if item.strip()]
        sentence_pairs = [(answer, kb) for kb in bks]

        all_scores = self.reranker.compute_score(sentence_pairs, normalize=True)

        # 使用sorted()函数对数组进行排序，并返回一个排序后的数组和对应的索引
        sorted_scores, sorted_indices = zip(*sorted(zip(all_scores, range(len(all_scores))), reverse=True))

        return bks[sorted_indices[0]] if len(sorted_indices) > 0 else None

rag = RAG()
