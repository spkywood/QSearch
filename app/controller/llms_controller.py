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
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse


from common import logger
from db.schemas import ChatSession
from common.response import BaseResponse, ListResponse
from app.runtime import LLMChatGLM, LLMQwen
from setting import CHATGLM_API_KEY, QWEN_API_KEY
from tools.register import tools, dispatch_tool

chatglm = LLMChatGLM(api_key=CHATGLM_API_KEY, model_name="glm-4")
qwen = LLMQwen(api_key=QWEN_API_KEY, model_name="qwen-max")

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
async def completion(
    model: Annotated[str, Body(...)],
    question: Annotated[str, Body(...)],
    stream: Annotated[bool, Body(default=False)]
):
    """
    大语言模型问答接口
    """
    messages = [
        {'role': 'system', 'content': 'You are a helpful assistant.'},
        {'role': 'user', 'content': question}
    ]
    resp = chatglm.invoke(messages=messages)

    if stream:
        return EventSourceResponse(resp)
    else:
        return BaseResponse(
            code=200,
            message="success",
            data=resp
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
    model_response = chatglm.invoke(messages=messages, tools=tools)

    if isinstance(model_response, dict) and model_response.get('tool_calls'):
        tool_name = model_response['tool_calls'][0]['function']['name']
        kwargs = model_response['tool_calls'][0]['function']['arguments']
        
        code = 200
        result = dispatch_tool(tool_name, kwargs)
    elif isinstance(model_response, str):
        code = 500
        result = model_response
    else:
        code = 400
        result = "No tool called"

    return BaseResponse(
        code=code,
        message="success",
        data=result
    )


@router.post("/chat/sse/completions")
async def sse_completions(
    model: Annotated[str, Body(...)],
    question: Annotated[str, Body(...)],
    stream: Annotated[bool, Body(...)],
):
    messages = [
        {'role': 'system', 'content': 'You are a helpful assistant.'},
        {'role': 'user', 'content': question}
    ]
    resp = chatglm.invoke(messages=messages, stream=stream)

    return EventSourceResponse(resp)
