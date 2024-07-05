#! python3
# -*- encoding: utf-8 -*-
'''
@File    : llm_qwen.py
@Time    : 2024/06/12 14:59:32
@Author  : longfellow
@Version : 1.0
@Email   : longfellow.wang@gmail.com
'''


from app.runtime.llm import LLM

from typing import List, Dict, Union, Optional
from http import HTTPStatus
import dashscope
import os
import json

class LLMQwen(LLM):
    def __init__(self, 
                 api_key: str = None, 
                 base_url: str = None, 
                 model_name: str = None
    ) -> None:
        super().__init__(api_key, base_url, model_name)

    def invoke(self, 
               messages: Union[str, List[Dict[str, str]]], 
               tools : Optional[object] = None,  
               stream: bool = False
    ):
        response = dashscope.Generation.call(
            model=self.model_name,
            api_key=self.api_key,
            messages=messages,
            result_format='message',  # 将返回结果格式设置为 message
            max_tokens=2000,  # 设置最大令牌数为 100
            top_p=0.7,
            temperature=0.7,
            stream=stream,
            tools=tools,
            incremental_output=True if stream else False  # 增量式流式输出
        )

        if stream:
            for resp in response:
                if resp["status_code"] == 200:
                    if choices := resp['output']['choices']:
                        yield choices[0].message
        else:
            if response.status_code == HTTPStatus.OK:
                yield response['output']['choices'][0].message
            else:
                yield None

if __name__ == "__main__":
    from settings import QWEN_API_KEY
    llm = LLMQwen(
        api_key=QWEN_API_KEY,
        model_name="qwen-max",
    )
    
    messages = [
        {'role': 'system', 'content': 'You are a helpful assistant.'},
        {'role': 'user', 'content': '请介绍一下通义千问'}
    ]

    resp = llm.invoke(messages=messages, stream=False)
    for res in resp:
        print(res)

    exit()
    messages.append(resp)
    print(json.dumps(messages, ensure_ascii=False, indent=4))

    print('-'*20)

    messages.append(
        {'role': 'user', 'content': '请介绍一下李白？'}
    )
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

