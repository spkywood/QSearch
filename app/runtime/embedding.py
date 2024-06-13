#! python3
# -*- encoding: utf-8 -*-
'''
@File    : local_model.py
@Time    : 2024/06/13 10:39:47
@Author  : longfellow
@Version : 1.0
@Email   : longfellow.wang@gmail.com
'''

import torch
from typing import Any, Union, List
from app.runtime.local_model import LocalModel

class Embedding(LocalModel):
    def __init__(self, model_path: str = None, use_fp16: bool = False, device: str | int = None) -> None:
        super().__init__(model_path, use_fp16, device)

    
    @torch.no_grad()
    def encode(self,
               sentences: Union[List[str], str],
               batch_size: int = 12,
               max_length: int = 8192,
               ):
        
        encoded_input = self.tokenizer(sentences, padding=True, truncation=True, return_tensors='pt')

        model_output = self.model(**encoded_input)
        sentence_embeddings = model_output[0][:, 0]

        sentence_embeddings = torch.nn.functional.normalize(sentence_embeddings, p=2, dim=1)

        return sentence_embeddings