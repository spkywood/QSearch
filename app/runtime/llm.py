#! python3
# -*- encoding: utf-8 -*-
'''
@File    : base_llm.py
@Time    : 2024/06/12 14:54:31
@Author  : longfellow
@Version : 1.0
@Email   : longfellow.wang@gmail.com
'''


from typing import Optional, List, Dict, Union
from abc import ABC, abstractmethod

class LLM(ABC):
    def __init__(self, 
                 api_key: str = None, 
                 base_url: str = None, 
                 model_name: str = None
    ) -> None:
        super().__init__()

        self.api_key = api_key
        self.base_url = base_url
        self.model_name = model_name

    @abstractmethod
    def invoke(self, 
               messages: Union[str, List[Dict[str, str]]], 
               tools : Optional[object] = None,  
               stream: bool = False
    ):
        raise NotImplementedError