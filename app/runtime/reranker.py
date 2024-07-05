#! python3
# -*- encoding: utf-8 -*-
'''
@File    : reranker.py
@Time    : 2024/06/13 11:02:44
@Author  : longfellow
@Version : 1.0
@Email   : longfellow.wang@gmail.com
'''


import os
import numpy as np
from FlagEmbedding import FlagReranker
from typing import Any, List, Dict

from settings import MODEL_PATH

class Reranker:
    def __init__(self, model_name: str, device: str = None) -> None:
        model_name = os.path.join(MODEL_PATH, model_name)
        self.reranker = FlagReranker(model_name, use_fp16=False)
    
    def compute_score(self, question: str, documents: List[Dict[str, str]]) -> List[Any]:
        if len(documents) == 0:  # to avoid empty api call
            return []
        
        sentence_pairs = [(question, doc['document']) for doc in documents]

        all_scores = self.reranker.compute_score(sentence_pairs, normalize=True)
        
        sentence_scores = []
        for i, result in enumerate(all_scores):
            sentence_scores.append({
                "index": i,
                "score": result,
                "document": documents[i]['document'],
                "uuid" : documents[i]['uuid'],
                "kb_name" : documents[i]['kb_name'],
                "file_id" : documents[i]['file_id'],
                "file_name" : documents[i]['file_name'],
            })
        return sentence_scores
