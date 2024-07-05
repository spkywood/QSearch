#! python3
# -*- encoding: utf-8 -*-
'''
@File    : llm.py
@Time    : 2024/07/05 10:02:24
@Author  : longfellow 
@Email   : longfellow.wang@gmail.com
@Version : 1.0
@Desc    : None
'''


from enum import Enum
from pydantic import BaseModel

class QAType(Enum):
    LLM = "LLM"
    RAG = "RAG"
    TOOL = "TOOL"

class ModelType(Enum):
    EMBEDDING = "embedding"
    RERANKER = "reranker"


class ChatModel(Enum):
    QWEN = "qwen-max"
    CHATGLM = "glm-4"


class ChatSession(BaseModel):
    topic: str = "default"


class RAGQuestion(BaseModel):
    question: str
    kb_name: str
    conversation: str = None
    model: ChatModel = ChatModel.CHATGLM
    

class CoplitRequest(BaseModel):
    question: str
    conversation: str = None
    model: ChatModel = ChatModel.CHATGLM
