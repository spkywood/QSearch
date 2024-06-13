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
from app.runtime import LLMChatGLM
from setting import CHATGLM_API_KEY

llm = LLMChatGLM(
    api_key=CHATGLM_API_KEY,
    base_url="",
    model_name="glm-4",
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
    resp = llm.invoke(messages=messages)

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