#! python3
# -*- encoding: utf-8 -*-
'''
@File    : local_model.py
@Time    : 2024/06/13 11:04:18
@Author  : longfellow
@Version : 1.0
@Email   : longfellow.wang@gmail.com
'''



import os
import torch
from typing import Union
from transformers import (
    AutoTokenizer, AutoModel,
    is_torch_npu_available
)

from setting import MODEL_PATH

class LocalModel:
    def __init__(self, 
                 model_name: str = None,
                 use_fp16: bool = False,
                 device: Union[str, int] = None
    ) -> None:
        model_path = os.path.join(MODEL_PATH, model_name)

        self.tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        self.model = AutoModel.from_pretrained(model_path, trust_remote_code=True)

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