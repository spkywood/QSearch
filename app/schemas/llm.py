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
from pydantic import BaseModel, Field


class AudioRequest(BaseModel):
    text: str = Field(..., description="需要语音合成的文本")
    temperature: int = Field(0.3, min=0.00001, max=1, description="Audio temperature")
    top_P: int = Field(0.7, min=0.1, max=0.9, description="top_P")
    top_K: int = Field(20, min=1, max=20, description="top_K")
    audio_seed: int = Field(42, min=0, max=100000000, description="audio_seed")
    text_seed: int = Field(42, min=0, max=100000000, description="text_seed")

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


# class ChatRequest(BaseModel):
#     question: str
#     conversation: str = None
#     model: ChatModel = ChatModel.CHATGLM

class ChatRequest(BaseModel):
    question: str
    kb_name: str
    conversation: str = None
    model: ChatModel = ChatModel.CHATGLM
    # model: ChatModel = ChatModel.QWEN

class HLContent(BaseModel):
    quuid: str
    answer: str

# class CoplitRequest(BaseModel):
#     question: str
#     conversation: str = None
#     model: ChatModel = ChatModel.CHATGLM


class GuideCreate(BaseModel):
    content: str = Field(..., max_length=2000)
    qa_type: QAType

class KnowledgeCreate(BaseModel):
    name: str
    icon: str
    desc: str