#! python3
# -*- encoding: utf-8 -*-
'''
@File    : llms.py
@Time    : 2024/07/05 09:44:42
@Author  : longfellow 
@Email   : longfellow.wang@gmail.com
@Version : 1.0
@Desc    : None
'''


import uuid
import json
import time
import asyncio
from typing import cast, List, Callable, Dict
from app.runtime.online_model import OnlineModel
from fastapi import APIRouter, Depends, Request
from sse_starlette.sse import EventSourceResponse
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from app.models.user import User
from app.models.conversation import Conversation
from app.core.response import BaseResponse
from app.schemas.llm import (
    ChatSession, RAGQuestion, 
    CoplitRequest, ChatModel,
)
from db.redis_client import redis

from logger import logger
from app.core.oauth import get_current_user
from app.controllers.conversation import add_conversation
from app.controllers.knowledge_base import get_kb_hash_name
from app.controllers.file_chunk import (
    query_chunk_with_id, query_chunk_with_uuid
)

from app.rag import rag
from app.prompt.prompt import knowledge_qa_prompt
from tools.register import tools, dispatch_tool
from tools.tools_template import MESSAGE_TEMPLATE, GENERATR_TEMPLATE

router = APIRouter()


'''创建会话'''
@router.post("/chat/sessions", summary="创建会话", include_in_schema=True)
async def create_chat(
    item: ChatSession,
    user: User = Depends(get_current_user)
) -> BaseResponse:
    uuid_string = f'{user.name}_{item.topic}_{time.time()}'
    redis_name = f'conversation:{user.name}'
    conv_uuid = str(uuid.uuid5(uuid.NAMESPACE_OID, uuid_string))
    
    await redis.hset(redis_name, conv_uuid, json.dumps([]))

    # 写入conversation表中
    conv: Conversation = await add_conversation(name=item.topic, conv_uuid=conv_uuid, user_id=user.id)

    return BaseResponse(
        code=200,
        msg="success",
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

def get_model(request: Request, model: ChatModel) -> OnlineModel:
    if model == ChatModel.CHATGLM:
        llm_model = request.state.chatglm
    else:
        llm_model = request.state.qwen

    llm_model = cast(OnlineModel, llm_model)
    
    return llm_model

'''知识库RAG检索问答'''
@router.post("/sse/chat/knowledge", summary="知识库检索问答RAG，流式输出")
async def chat_with_knowledge(
    request: Request,
    item: RAGQuestion,
    user: User = Depends(get_current_user)
) -> BaseResponse:
    llm_model = get_model(request, item.model)
    
    '''根据知识库名称获取hash_name'''
    hash_name = await get_kb_hash_name(item.kb_name, user.id)

    if hash_name is None:
        return BaseResponse(code=404, msg="知识库不存在", data=None)

    uuids = rag.search(item.question, hash_name)
    
    documents = []
    for _uuid in uuids:
        chunk = await query_chunk_with_uuid(_uuid)

        file_id = chunk['file_id']
        chunk_id = chunk['chunk_id']

        text = chunk['chunk']
        prev_text = await query_chunk_with_id(file_id=file_id, chunk_id=chunk_id-1)
        next_text = await query_chunk_with_id(file_id=file_id, chunk_id=chunk_id+1)

        #############
        ### 删除overlap部分字符串
        ##############
        l1_l2_overlap = min(len(prev_text), len(text))
        l2_l3_overlap = min(len(text), len(next_text))

        over1_str = ""
        over2_str = ""
        for i in range(l1_l2_overlap, 0, -1):
            if prev_text[-i:] == text[:i]:
                over1_str = text[:i]
        
        for i in range(l2_l3_overlap, 0, -1):
            if text[-i:] == next_text[:i]:
                over2_str = next_text[:i]
        
        text = text.replace(over1_str, "")
        next_text = next_text.replace(over2_str, "")

        text = prev_text.strip() + chunk['chunk'].strip() + next_text.strip()
    
        documents.append({
            "uuid" : _uuid,
            "kb_name" : item.kb_name,
            "file_id" : file_id,
            "file_name" : chunk['file_name'],
            "document" : text,
        })

    top = rag.postprocess(item.question, documents)

    '''检索结果写入redis'''
    # 每次提问生成uuid
    uuid_string = f'{item.question}_{time.time()}'
    quuid = str(uuid.uuid5(uuid.NAMESPACE_OID, uuid_string))
    qname = f'question:{user.name}'
    query_content = [{
        "file_id" : _t['file_id'],
        "file_name" : _t['file_name'],
        "chunk" : _t['document'],
        "file_url" : rag.get_obj_url(hash_name, _t['file_name']),

    } for _t in top[:3]]

    '''检索结果写入redis'''
    await redis.hset(qname, quuid, json.dumps(query_content, indent=4, ensure_ascii=False))

    prompt = knowledge_qa_prompt(top[0]['document'], item.question)
    '''[TODO: 聊天记录]'''
    redis_name = f'conversation:{user.name}'
    history = await redis.hget(redis_name, item.conversation)
    history: List = json.loads(history)

    messages = [{'role': 'user', 'content': prompt}]

    history.append({'role': 'user', 'content': item.question})

    resp = llm_model.sse_invoke(messages)

    async def sse_stream():
        assistant = {"role": "assistant", "content": ""}
        for delta_content in resp:
            assistant['content'] += delta_content["content"]
            delta_content["quuid"] = quuid
            yield json.dumps(delta_content, ensure_ascii=False)
            await asyncio.sleep(0.1)

        '''聊天历史记录保存'''
        history.append(assistant)
        await redis.hset(redis_name, item.conversation, json.dumps(history))

    return EventSourceResponse(sse_stream())


'''RAG检索结果'''
@router.get("/rag/content", summary="获取检索结果")
async def get_rag_content(
    quuid: str,
    user: User = Depends(get_current_user)
) -> BaseResponse:
    '''获取RAG检索内容'''
    context = await redis.hget(f'question:{user.name}', quuid)
    if context is None:
        return BaseResponse(code=404, msg="服务器内容丢失", data=None)
    return BaseResponse(code=200, msg="success", data=json.loads(context))



'''工具调用'''
@router.post("/sse/chat-tools", summary="软件助手问答", include_in_schema=True)
async def sse_chat_with_tools(
    request: Request,
    item: CoplitRequest,
    user: User = Depends(get_current_user)
) -> EventSourceResponse:
    llm_model = get_model(request, item.model)

    messages = [
        {'role': 'system', 'content': '不要假设或猜测传入函数的参数值。如果用户的描述不明确，请要求用户提供必要信息'},
        {'role': 'user', 'content': item.question}
    ]

    model_response = llm_model.invoke(messages=messages, tools=tools)

    '''工具未注册，或未能匹配工具'''
    if model_response['tool_calls'] is None:
        return BaseResponse(
            code=400, 
            msg=model_response['content'], 
            data=None
        )

    tool_name = model_response['tool_calls'][0]['function']['name']
    kwargs = model_response['tool_calls'][0]['function']['arguments']
    kwargs: Dict = json.loads(kwargs)

    '''时间参数模板'''
    from tools.constants import get_date_range

    if tool_name == 'get_realtime_water_condition':
        fmt = '%Y-%m-%d 00:00:00'
        end_fmt = '%Y-%m-%d 00:00:00'
        kwargs = get_date_range(kwargs, item.question, fmt, end_fmt)
    if tool_name == 'get_water_rain':
        fmt = '%Y-%m-%d 00:00:00'
        end_fmt = '%Y-%m-%d 23:59:59'
        kwargs = get_date_range(kwargs, item.question, fmt, end_fmt)
            
    logger.info(f"{item.question} {tool_name} {kwargs}")
    try:
        result = dispatch_tool(tool_name, kwargs)
    except Exception as e:
        logger.error(f'dispatch_tool error:{e}')
        return BaseResponse(
            code=500, 
            msg=str(e), 
            data=None
        )

    '''tools/tools_template.py中定义返回模板，根据模板生成回复'''
    generate_template: Callable = GENERATR_TEMPLATE.get(tool_name)
    resp = generate_template(data=result)
    '''检索结果写入redis'''
    # 每次提问生成uuid
    uuid_string = f'{item.question}_{time.time()}'
    quuid = str(uuid.uuid5(uuid.NAMESPACE_OID, uuid_string))
    qname = f'chat-tools:{user.name}'  # qname = f'chat-tools:test'

    await redis.hset(qname, quuid, resp)
    '''检索结果写入redis'''
    
    if tool_name in ['get_water_rain', 'get_position']:
        import jieba
        tmp = item.question.replace('查询', '').replace('有什么', '').replace('?', '').replace('？', '')
        tmp += "结果如下:"

        words = jieba.cut(tmp, cut_all=False)
        words = [word for word in words]
        def sse_stream():
            for word in words:
                yield json.dumps({"content": word, "role": "assistant", "tool_calls": None, "quuid": quuid}, ensure_ascii=False) 
                time.sleep(0.1)

        return EventSourceResponse(sse_stream())
    

    '''根据函数调用结果和用户问题，返回生成回复'''
    question = resp + '\n\n' + item.question
    messages = [
        {'role': 'system', 'content': '根据问题和函数调用的结果，生成对应回复'},
        {'role': 'user', 'content': question},
    ]

    redis_name = f'conversation:{user.name}'
    history = await redis.hget(redis_name, item.conversation)
    history: List = json.loads(history)
    history.append({'role': 'user', 'content': item.question})

    resp = llm_model.sse_invoke(messages)


    async def sse_stream():
        assistant = {"role": "assistant", "content": ""}
        for delta_content in resp:
            assistant['content'] += delta_content["content"]
            delta_content["quuid"] = quuid
            yield json.dumps(delta_content, ensure_ascii=False)
            await asyncio.sleep(0.1)

        '''聊天历史记录保存'''
        history.append(assistant)
        await redis.hset(redis_name, item.conversation, json.dumps(history))


    return EventSourceResponse(sse_stream())


@router.get("/tools/content", summary="获取软件助手生成结果")
async def get_tool_content(
    quuid: str,
    user: User = Depends(get_current_user)
) -> BaseResponse:
    '''根据知识库名称获取hash_name'''
    context = await redis.hget(f'chat-tools:{user.name}', quuid)
    if context is None:
        return BaseResponse(code=404, msg="知识库不存在", data=None)
    return BaseResponse(
        code=200, 
        msg="success", 
        data=json.loads(context)
    )
