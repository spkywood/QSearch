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
    def __init__(self, model_name: str = None, use_fp16: bool = False, device: str | int = None) -> None:
        super().__init__(model_name, use_fp16, device)

    
    @torch.no_grad()
    def encode(self,
               sentences: Union[List[str], str],
               batch_size: int = 12,
               max_length: int = 1024,
               ):
        
        encoded_input = self.tokenizer(sentences, padding=True, truncation=True, return_tensors='pt', max_length=max_length)
        encoded_input.to(self.device)

        model_output = self.model(**encoded_input)
        sentence_embeddings = model_output[0][:, 0]

        sentence_embeddings = torch.nn.functional.normalize(sentence_embeddings, p=2, dim=1)

        return sentence_embeddings
