#! python3
# -*- encoding: utf-8 -*-
'''
@File    : llm_chatglm.py
@Time    : 2024/06/12 16:40:17
@Author  : longfellow
@Version : 1.0
@Email   : longfellow.wang@gmail.com
'''



from app.runtime.llm import LLM
from common import logger

from typing import List, Dict, Union, Optional
from http import HTTPStatus
from zhipuai import ZhipuAI
import os
import json

class LLMChatGLM(LLM):
    def __init__(self, 
                 api_key: str = None, 
                 base_url: str = None, 
                 model_name: str = None
    ) -> None:
        super().__init__(api_key, base_url, model_name)
        self.client = ZhipuAI(api_key=api_key) 

    def invoke(self, 
               messages: Union[str, List[Dict[str, str]]], 
               tools : Optional[object] = None,  
               stream: bool = False
    ):
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=2000,  # 设置最大令牌数为 100
                top_p=0.7,
                temperature=0.7,
                stream=stream,
                tools=tools
            )

            message = response.choices[0].message
            return message.model_dump()
        except Exception as e:
            logger.error(e)
            return "llm server connection error."
        
    def sse_invoke(self, 
               messages: Union[str, List[Dict[str, str]]], 
               tools : Optional[object] = None,  
               stream: bool = True
    ):
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=2000,  # 设置最大令牌数为 100
                top_p=0.7,
                temperature=0.7,
                stream=stream,
                tools=tools
            )

            for chunk in response:
                delta = chunk.choices[0].delta
                yield json.dumps(delta.model_dump(), ensure_ascii=False)

        except Exception as e:
            logger.error(e)
            yield "llm server connection error."

if __name__ == "__main__":
    from setting import CHATGLM_API_KEY
    llm = LLMChatGLM(
        api_key=CHATGLM_API_KEY,
        base_url="",
        model_name="glm-4",
    )
    
    messages = [
        {'role': 'system', 'content': 'You are a helpful assistant.'},
        {'role': 'user', 'content': '请介绍一下通义千问'}
    ]

    resp = llm.invoke(messages=messages)
    for i in resp:
        print(i)

    # messages.append(resp)
    # print(json.dumps(messages, ensure_ascii=False, indent=4))

    # print('-'*20)

    # messages.append(
    #     {'role': 'user', 'content': '请介绍一下李白？'}
    # )

    exit(0)
    resp = llm.invoke(messages)

    messages.append(resp)

    print(json.dumps(messages, ensure_ascii=False, indent=4))

    print('-'*20)

    messages.append(
        {'role': 'user', 'content': '说一首最有名的诗？'}
    )
    resp = llm.invoke(messages)

    messages.append(resp)

    print(json.dumps(messages, ensure_ascii=False, indent=4))

