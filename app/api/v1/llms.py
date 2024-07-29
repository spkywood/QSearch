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
    ChatModel, 
    ChatRequest, 
    ChatSession, 
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


from settings import (
    QWEN_API_KEY, QWEN_BASE_URL, QWEN_MODEL,
    CHATGLM_API_KEY, CHATGLM_BASE_URL, CHATGLM_MODEL,
    DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL
)

qwen_model = OnlineModel(
    api_key=QWEN_API_KEY, 
    base_url= QWEN_BASE_URL,
    model=QWEN_MODEL
)

glm_model = OnlineModel(
    api_key=CHATGLM_API_KEY, 
    base_url= CHATGLM_BASE_URL,
    model=CHATGLM_MODEL
)



def get_model(request: Request, model: ChatModel) -> OnlineModel:
    logger.info(f"model == ChatModel.CHATGLM {model == ChatModel.CHATGLM}")
    if model == ChatModel.CHATGLM:
        logger.info(f"get model {model}")
        # llm_model = request.state.chatglm
        return glm_model
    else:
        logger.info(f"get model {model}")
        # llm_model = request.state.qwen
        return qwen_model

    llm_model = cast(OnlineModel, llm_model)
    logger.info(f"calling model: {llm_model.model}")
    
    return llm_model

@router.post("/sse/chat/completions", summary="对话接口，流式输出")
async def chat_with_llm(
    request: Request,
    item: ChatRequest,
    user: User = Depends(get_current_user)
):
    llm_model = get_model(request, item.model)
    logger.info(f"calling model: {llm_model.model}")

    '''[TODO: 聊天记录]'''
    redis_name = f'conversation:{user.name}'
    history = await redis.hget(redis_name, item.conversation)
    history: List = json.loads(history) if history is not None else []

    messages = [{'role': 'user', 'content': item.question}]
    history.append({'role': 'user', 'content': item.question})

    resp = llm_model.sse_invoke(messages)

    async def sse_stream():
        assistant = {"role": "assistant", "content": ""}
        for delta_content in resp:
            assistant['content'] += delta_content["content"]
            yield json.dumps(delta_content, ensure_ascii=False)
            await asyncio.sleep(0.05)

        '''聊天历史记录保存'''
        history.append(assistant)
        await redis.hset(redis_name, item.conversation, json.dumps(history))

    return EventSourceResponse(sse_stream())

from celery_app import highlight_content

async def error_stream(code: int, msg: str):
    yield json.dumps({"code" : code, "msg" : msg, "data" : None}, ensure_ascii=False)

'''知识库RAG检索问答'''
@router.post("/sse/chat/knowledge", summary="知识库检索问答RAG，流式输出")
async def chat_with_knowledge(
    request: Request,
    item: ChatRequest,
    user: User = Depends(get_current_user)
) -> BaseResponse:
    logger.info(f"chat with knowledge: {item.conversation} {item.question} {user.name}")
    llm_model = get_model(request, item.model)
    logger.info(f"calling model: {llm_model.model}")
    
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

    content = '\n\n'.join([_t['file_name'] + '\n' + _t['document'] for _t in top[:3]])

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

    prompt = knowledge_qa_prompt(content, item.question)
    '''[TODO: 聊天记录]'''
    redis_name = f'conversation:{user.name}'
    history = await redis.hget(redis_name, item.conversation)
    history: List = json.loads(history) if history is not None else []

    messages = [{'role': 'user', 'content': prompt}]

    history.append({'role': 'user', 'content': item.question})

    resp = llm_model.sse_invoke(messages)

    async def sse_stream():
        assistant = {"role": "assistant", "content": ""}
        for delta_content in resp:
            assistant['content'] += delta_content["content"]
            delta_content["quuid"] = quuid
            yield json.dumps(delta_content, ensure_ascii=False)
            await asyncio.sleep(0.05)

        '''聊天历史记录保存'''
        history.append(assistant)
        await redis.hset(redis_name, item.conversation, json.dumps(history))

        '''文本高亮'''
        highlight_content.delay(user.name, quuid, assistant['content'])

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

ennm = ['龙羊峡', '刘家峡', '青铜峡', '海勃湾', '万家寨', '龙口', '三门峡', '小浪底', '西霞院', '河口村', '故县', '陆浑', '东平湖']
rules = ['降雨', '降水', '等值', '分布特征', '位置', '在哪里', '经纬度']

'''工具调用'''
@router.post("/sse/chat-tools", summary="软件助手问答", include_in_schema=True)
async def sse_chat_with_tools(
    request: Request,
    item: ChatRequest,
    user: User = Depends(get_current_user)
) -> EventSourceResponse:
    logger.info(f"chat with knowledge: {item.conversation} {item.question} {user.name}")
    
    llm_model = get_model(request, item.model)
    logger.info(f"calling model: {llm_model.model}")

    messages = [
        {'role': 'system', 'content': '不要假设或猜测传入函数的参数值。如果用户的描述不明确，请要求用户提供必要信息'},
        {'role': 'user', 'content': item.question}
    ]
    model_response = llm_model.sse_invoke(messages=messages, tools=tools)

    tool_name = None
    kwargs = ''
    for data in model_response:
        logger.info(f"model response: {data}")
        if data['content'] is not None and data['content'] != '':
            logger.info(f'{item.question} 未能找到工具调用 请调用RAG助手')
            return BaseResponse(
                code=40000, 
                msg='工具未注册，或未能匹配工具', 
                data=None
            )
        if data['tool_calls'] is not None:
            tool_call = data['tool_calls'][0]
            if tool_call['function']['name']:
                tool_name = tool_call['function']['name']
            if tool_call['function']['arguments']:
                kwargs += tool_call['function']['arguments']

    if tool_name is None:
        return BaseResponse(
            code=40000, 
            msg='工具未注册，或未能匹配工具', 
            data=None
        )

    try:
        logger.info(f'{item.question} 调用工具 {tool_name} 参数 {kwargs}')
        kwargs: Dict = json.loads(kwargs) if kwargs != '' else {}
    except:
        return BaseResponse(code=40000, msg='参数解析错误', data=None)

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
    if tool_name == 'get_history_features':
        if "近五年" in item.question or "近5年" in item.question:
            kwargs.update({'start_year': 2020, 'end_year': 2024})
        if "历史" in item.question:
            kwargs.update({'start_year': 2000, 'end_year': 2024})
            
    logger.info(f"{item.question} {tool_name} {kwargs}")
    try:
        result = dispatch_tool(tool_name, kwargs)
    except Exception as e:
        logger.error(f'dispatch_tool error:{e}')
        return BaseResponse(
            code=500, 
            msg='服务器内部异常', 
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
                time.sleep(0.05)

        return EventSourceResponse(sse_stream())
    

    '''根据函数调用结果和用户问题，返回生成回复'''
    question = resp + '\n\n' + item.question
    messages = [
        {'role': 'system', 'content': '根据下面函数生成的图表结果，请根据用户问题生成回复，要求回复简洁明了，不要重复用户问题'},
        {'role': 'user', 'content': question},
    ]

    redis_name = f'conversation:{user.name}'
    history = await redis.hget(redis_name, item.conversation)
    history: List = json.loads(history) if history is not None else []
    history.append({'role': 'user', 'content': item.question})

    resp = llm_model.sse_invoke(messages)


    async def sse_stream():
        assistant = {"role": "assistant", "content": ""}
        for delta_content in resp:
            assistant['content'] += delta_content["content"]
            delta_content["quuid"] = quuid
            yield json.dumps(delta_content, ensure_ascii=False)
            await asyncio.sleep(0.05)

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
