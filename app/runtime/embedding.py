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
import os
import torch
from typing import Union
from transformers import (
    AutoTokenizer, AutoModel,
    is_torch_npu_available
)

from settings import MODEL_PATH

class Embedding:
    def __init__(self, model_name: str = None, use_fp16: bool = False, device: str | int = None) -> None:
        self.num_gpus = 1
        
        self.model_path = os.path.join(MODEL_PATH, model_name)

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, trust_remote_code=True)
        self.model = AutoModel.from_pretrained(self.model_path, trust_remote_code=True)

        if device and isinstance(device, str):
            self.device = torch.device(device)
            if device == 'cpu':
                use_fp16 = False
        else:
            if torch.cuda.is_available():
                if device is not None:
                    self.device = torch.device(f"cuda:{device}")
                else:
                    self.device = torch.device("cuda")
            elif torch.backends.mps.is_available():
                self.device = torch.device("mps")
            elif is_torch_npu_available():
                self.device = torch.device("npu")
            else:
                self.device = torch.device("cpu")
                use_fp16 = False
            
        if use_fp16:
            self.model.half()
        
        self.model = self.model.to(self.device)
        self.model.eval()
    
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

    @torch.no_grad()
    def embed(self,
        sentence: str,
        batch_size: int = 12,
        max_length: int = 1024,
    ):
        return self.encode([sentence], batch_size, max_length)[0]