#! python3
# -*- encoding: utf-8 -*-
'''
@File    : llms_controller.py
@Time    : 2024/06/12 18:03:36
@Author  : longfellow
@Version : 1.0
@Email   : longfellow.wang@gmail.com
'''


from typing import Annotated
from fastapi import APIRouter, Body

from common import logger
from db.schemas import ChatSession
from common.response import BaseResponse, ListResponse
from app.runtime import LLMChatGLM, LLMQwen
from setting import CHATGLM_API_KEY, QWEN_API_KEY
from tools.register import tools, dispatch_tool

chatglm = LLMChatGLM(
    api_key=CHATGLM_API_KEY,
    model_name="glm-4",
)

qwen = LLMQwen(
    api_key=QWEN_API_KEY,
    model_name="qwen-max",
)

router = APIRouter()

@router.post("/chat/sessions")
async def create_chat(chat_sess: ChatSession):
    return BaseResponse(
        code=200,
        message="success",
        data={
            "mask" : {
                "name" : chat_sess.topic,
                "modelConfig" : {
                    "max_tokens" : 2000,
                    "model" : "glm-4",
                    "temperature" : 8.0,
                }
            }
        }
    )

@router.post("/chat/completions")
async def completion(model: Annotated[str, Body(...)],
                     question: Annotated[str, Body(...)],):
    
    messages = [
        {'role': 'system', 'content': 'You are a helpful assistant.'},
        {'role': 'user', 'content': question}
    ]
    resp = chatglm.invoke(messages=messages)

    result = None
    logger.info(resp)
    for i in resp:
        logger.info(i)
        result = i

    return BaseResponse(
        code=200,
        message="success",
        data=result
    )

@router.post("/chat/tools")
async def chat_with_tools(
    model: Annotated[str, Body(...)],
    question: Annotated[str, Body(...)],
):
    messages = [
        {'role': 'system', 'content': '不要假设或猜测传入函数的参数值。如果用户的描述不明确，请要求用户提供必要信息'},
        {'role': 'user', 'content': question}
    ]
    resp = chatglm.invoke(messages=messages, tools=tools)

    model_response = None
    for i in resp:
        logger.info(i)
        model_response = i

    if model_response.tool_calls:
        tool_name = model_response['tool_calls'][0]['function']['name']
        kwargs = model_response['tool_calls'][0]['function']['arguments']
        result = dispatch_tool(tool_name, kwargs)
    else:
        result = "No tool called"

    return BaseResponse(
        code=200,
        message="success",
        data=result
    )
