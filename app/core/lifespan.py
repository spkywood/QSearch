#! python3
# -*- encoding: utf-8 -*-
'''
@File    : lifespan.py
@Time    : 2024/07/05 10:32:31
@Author  : longfellow 
@Email   : longfellow.wang@gmail.com
@Version : 1.0
@Desc    : None
'''


from fastapi import FastAPI
from typing import Any, TypedDict
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from app.runtime.online_model import OnlineModel
from settings import (
    QWEN_API_KEY, QWEN_BASE_URL, QWEN_MODEL,
    CHATGLM_API_KEY, CHATGLM_BASE_URL, CHATGLM_MODEL,
    DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL
)


class State(TypedDict):
    chatglm: OnlineModel
    qwen: OnlineModel


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[State]:
    qwen = OnlineModel(api_key=QWEN_API_KEY, base_url=QWEN_BASE_URL, model=QWEN_MODEL)
    chatglm = OnlineModel(api_key=CHATGLM_API_KEY, base_url=CHATGLM_BASE_URL, model=CHATGLM_MODEL)
    state: State = {'chatglm': chatglm, 'qwen': qwen}

    yield state
