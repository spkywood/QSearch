#! python3
# -*- encoding: utf-8 -*-
'''
@File    : llms_controller.py
@Time    : 2024/06/12 18:03:36
@Author  : longfellow
@Version : 1.0
@Email   : longfellow.wang@gmail.com
'''


from typing import Annotated, List, Dict
from fastapi import APIRouter, Body, Depends
from sse_starlette.sse import EventSourceResponse
import json
import uuid
from time import time
from common import logger
from app.models import User
from app.controller import get_current_user
from db.schemas import ChatSession, RAGQuestion, QAItem, ChatHistoryRequest
from common.response import BaseResponse
from app.runtime import LLMChatGLM, LLMQwen
from setting import CHATGLM_API_KEY, QWEN_API_KEY
from tools.register import tools, dispatch_tool
from app.models import Conversation

from db.curds import (
    query_chunk_with_uuid, 
    query_chunk_with_id,
    add_conversation,
    query_conversation,
    get_kb_hash_name,
)
chatglm = LLMChatGLM(api_key=CHATGLM_API_KEY, model_name="glm-4")
qwen = LLMQwen(api_key=QWEN_API_KEY, model_name="qwen-max")

router = APIRouter()

# [TODO] 封装redis
from app.controller.users_controller import redis 


'''创建会话'''
@router.post("/chat/sessions", summary="创建会话")
async def create_chat(
    chat_session: ChatSession,
    user: User = Depends(get_current_user)
) -> BaseResponse:
    """
    创建会话，在内存中和redis中创建user.name, chat_session.topic
    redis hset name:conversation_{user.name} key:{chat_session.topic}
    """
    uuid_string = f'{user.name}_{chat_session.topic}_{time()}'
    redis_name = f'conversation:{user.name}'
    conv_uuid = str(uuid.uuid5(uuid.NAMESPACE_OID, uuid_string))
    messages = []
    
    await redis.hset(redis_name, conv_uuid, json.dumps(messages))

    # 写入conversation表中
    conv: Conversation = await add_conversation(name=chat_session, conv_uuid=conv_uuid, user_id=user.id)

    return BaseResponse(
        code=200,
        message="success",
        data={
            "mask" : {
                "conversation": {
                    "id": conv.conv_uuid,
                    "name": conv.name,
                },
                "modelConfig" : {
                    "max_tokens" : 2000,
                    "model" : "glm-4",
                    "temperature" : 0.7,
                }
            }
        }
    )



'''获取用户所有会话'''
@router.get("/chat/sessions", summary="获取用户会话列表")
async def get_chat_sessions(
    user: User = Depends(get_current_user)
) -> BaseResponse:
    convs: List[Conversation] = await query_conversation(user_id=user.id)

    return BaseResponse(
        code=200,
        message="success",
        data=[
            {
                "id": conv.conv_uuid,
                "name": conv.name,
            } for conv in convs
        ]
    )



@router.post("/chat/history", summary="获取历史对话记录")
async def get_chat_history(
    item: ChatHistoryRequest,
    user: User = Depends(get_current_user)
) -> BaseResponse:
    """
    创建会话，在内存中和redis中创建user.name, chat_session.topic
    redis hset name:conversation_{user.name} key:{chat_session.topic}
    """
    redis_name = f'conversation:{user.name}'

    history = await redis.hget(redis_name, item.uuid)
    return BaseResponse(
        code=200,
        message="success",
        data=history
    )

@router.post("/chat/completions", summary="大语言模型问答接口")
async def completion(
    item: QAItem,
    # user: User = Depends(get_current_user)
):
    """
    大语言模型问答接口
    """
    messages = [
        {'role': 'system', 'content': 'You are a helpful assistant.'},
        {'role': 'user', 'content': item.question}
    ]
    resp: Dict = chatglm.invoke(messages=messages)
    
    return BaseResponse(
        code=200,
        message="success",
        data=resp
    )

@router.post("/sse/chat/completions", summary="大语言模型问答接口，流式输出")
async def sse_completion(
    model: Annotated[str, Body(...)],
    question: Annotated[str, Body(...)],
    stream: Annotated[bool, Body(...)]
):
    """
    大语言模型问答接口
    """
    messages = [
        {'role': 'system', 'content': 'You are a helpful assistant.'},
        {'role': 'user', 'content': question}
    ]

    return EventSourceResponse(chatglm.sse_invoke(messages=messages))
  
from app.runtime.embedding import Embedding
from app.runtime.reranker import Reranker
from db import minio_client, milvus_client, es_client
from common.cache import model_manager, ModelType

from common.prompt import knowledge_qa_prompt

embedding: Embedding = model_manager.load_models(
    'BAAI/bge-large-zh-v1.5', 
    device='cuda', 
    model_type=ModelType.EMBEDDING
)

reranker: Reranker = model_manager.load_models(
    'BAAI/bge-reranker-base', 
    device='cuda', 
    model_type=ModelType.RERANKER
)

def vector_search(query_vector, kb_name: str, expr: str = None):
    result = milvus_client.search(kb_name, query_vector, expr=expr)
    return result
    
def bm25_search(question: str, kb_name: str):
    results = es_client.search(kb_name, question)
    return [result['_source']['chunk_uuid'] for result in results]

@router.post("/sse/chat/knowledge")
async def chat_with_knowledge(
    item: RAGQuestion,
    user: User = Depends(get_current_user)
) -> BaseResponse:
    """根据知识库名称获取hash_name"""
    hash_name = await get_kb_hash_name(item.kb_name, user.id)
    if hash_name is None:
        return BaseResponse(code=404, msg="failure", data="知识库不存在")

    query_vector = embedding.encode(item.question)[0].tolist()

    vector_result = vector_search(query_vector, hash_name)
    bm25_result = bm25_search(item.question, hash_name)
    
    uuids = list(set(vector_result + bm25_result))

    knowledges = []
    for uuid in uuids:
        chunk = await query_chunk_with_uuid(uuid)

        file_id = chunk['file_id']
        chunk_id = chunk['chunk_id']
        prev_text = await query_chunk_with_id(file_id=file_id, chunk_id=chunk_id-1)
        next_text = await query_chunk_with_id(file_id=file_id, chunk_id=chunk_id+1)
        
        text = prev_text.strip() + chunk['chunk'].strip() + next_text.strip()
        # knowledges.append(text)
        knowledges.append({
            "uuid" : uuid,
            "kb_name" : item.kb_name,
            "file_name" : chunk['file_name'],
            "document" : text,
        })
    # [TODO] 
    # 1. 检查用户是否具有访问知识库的权限

    scores = reranker.compute_score(item.question, knowledges)
    top = sorted(scores, key=lambda x: x['score'], reverse=True)

    prompt = knowledge_qa_prompt(top[0]['document'], item.question)
    
    messages = [
        {'role': 'system', 'content': '你是一个知识库问答助手，回答用户的问题。如果知识库中没有答案，请回答“我不知道”。'},
        {'role': 'user', 'content': prompt}
    ]

    return EventSourceResponse(chatglm.sse_invoke(messages=messages))

    return BaseResponse(code=200, message="success", data=top[0])

@router.post("/chat/tools")
async def chat_with_tools(
    model: Annotated[str, Body(...)],
    question: Annotated[str, Body(...)]
):
    messages = [
        {'role': 'system', 'content': '不要假设或猜测传入函数的参数值。如果用户的描述不明确，请要求用户提供必要信息'},
        {'role': 'user', 'content': question}
    ]
    
    model_response = chatglm.invoke(messages=messages, tools=tools, stream=stream)

    if isinstance(model_response, dict) and model_response.get('tool_calls'):
        tool_name = model_response['tool_calls'][0]['function']['name']
        kwargs = model_response['tool_calls'][0]['function']['arguments']
        
        code = 200
        result = dispatch_tool(tool_name, kwargs)
    if isinstance(model_response, str):
        code = 500
        result = model_response

    return BaseResponse(
        code=code,
        message="success",
        data=result
    )

@router.post("/sse/chat/tools")
async def sse_chat_with_tools(
    model: Annotated[str, Body(...)],
    question: Annotated[str, Body(...)],
    stream: Annotated[bool, Body(...)],
):
    messages = [
        {'role': 'system', 'content': '不要假设或猜测传入函数的参数值。如果用户的描述不明确，请要求用户提供必要信息'},
        {'role': 'user', 'content': question}
    ]
    
    model_response = chatglm.sse_invoke(messages=messages, tools=tools)

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
