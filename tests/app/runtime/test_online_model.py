from settings import QWEN_API_KEY
from app.runtime.online_model import OnlineModel

from tools.register import tools, dispatch_tool

from settings import (
    QWEN_API_KEY, QWEN_BASE_URL, QWEN_MODEL,
    CHATGLM_API_KEY, CHATGLM_BASE_URL, CHATGLM_MODEL,
    DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL
)
from app.prompt.prompt import knowledge_qa_prompt

# DEEPSEEK_API_KEY = 'sk-be68fe30c9594171bf3738e744b597e2'
# DEEPSEEK_BASE_URL = 'https://api.deepseek.com/v1'
# DEEPSEEK_MODEL = 'deepseek-chat'

LOCAL_BASE_URL = "http://192.168.1.126:9997/v1"

llm_model = OnlineModel(
    api_key=QWEN_API_KEY, 
    base_url=QWEN_BASE_URL,
    model=QWEN_MODEL
)

from app.rag import rag
from app.controllers.file_chunk import (
    query_chunk_with_id, query_chunk_with_uuid
)


async def test_rag(question: str):
    
    '''根据知识库名称获取hash_name'''
    kb_name = 'demo'
    hash_name = 'yjqewsa8lex7'

    uuids = rag.search(question, hash_name)
    
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
            "kb_name" : kb_name,
            "file_id" : file_id,
            "file_name" : chunk['file_name'],
            "document" : text,
        })

    top = rag.postprocess(question, documents)

    '''检索结果写入redis'''
    # 每次提问生成uuid
    # uuid_string = f'{question}_{time.time()}'
    # quuid = str(uuid.uuid5(uuid.NAMESPACE_OID, uuid_string))
    # qname = f'question:{user.name}'
    query_content = [{
        "file_id" : _t['file_id'],
        "file_name" : _t['file_name'],
        "chunk" : _t['document'],
        "file_url" : rag.get_obj_url(hash_name, _t['file_name']),

    } for _t in top[:3]]

    # '''检索结果写入redis'''
    # await redis.hset(qname, quuid, json.dumps(query_content, indent=4, ensure_ascii=False))

    content = '\n\n'.join([_t['file_name'] + '\n' + _t['document'] for _t in top[:3]])

    print(content)
    print('-'*20)
    prompt = knowledge_qa_prompt(content, question)
    # '''[TODO: 聊天记录]'''
    # redis_name = f'conversation:{user.name}'
    # history = await redis.hget(redis_name, conversation)
    # history: List = json.loads(history) if history is not None else []

    messages = [{'role': 'user', 'content': prompt}]

    # history.append({'role': 'user', 'content': question})

    resp = llm_model.invoke(messages)

    print(resp)
    # return resp

    # async def sse_stream():
    #     assistant = {"role": "assistant", "content": ""}
    #     for delta_content in resp:
    #         assistant['content'] += delta_content["content"]
    #         delta_content["quuid"] = quuid
    #         yield json.dumps(delta_content, ensure_ascii=False)
    #         await asyncio.sleep(0.1)

    #     '''聊天历史记录保存'''
    #     history.append(assistant)
    #     await redis.hset(redis_name, conversation, json.dumps(history))

    # return EventSourceResponse(sse_stream())

question = "在水土流失严重地区开垦种植农作物有哪些限制？"
if __name__ == '__main__':
    # test_online_model()
    # test_sse_online_model()
    # test_sse_online_model()
    # exit()
    import sys
    import asyncio
    if sys.version_info < (3, 10):
        loop = asyncio.get_event_loop()
    else:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
    
    asyncio.set_event_loop(loop)
    
    loop.run_until_complete(test_rag(question))


# question = "小浪底水库历史上最大入库流量是多少？"
# messages = [
#     {'role': 'system', 'content': '不要假设或猜测传入函数的参数值。如果用户的描述不明确，请要求用户提供必要信息'},
#     {'role': 'user', 'content': question},
# ]

# import json
# from typing import Dict, Callable
# from logger import logger
# from tools.tools_template import MESSAGE_TEMPLATE, GENERATR_TEMPLATE
# '''时间参数模板'''
# from tools.constants import get_date_range

# model_response = llm_model.invoke(messages=messages, tools=tools)

# tool_name = model_response['tool_calls'][0]['function']['name']
# kwargs = model_response['tool_calls'][0]['function']['arguments']
# kwargs: Dict = json.loads(kwargs)

# if tool_name == 'get_realtime_water_condition':
#     fmt = '%Y-%m-%d 00:00:00'
#     end_fmt = '%Y-%m-%d 00:00:00'
#     kwargs = get_date_range(kwargs, question, fmt, end_fmt)
# if tool_name == 'get_water_rain':
#     fmt = '%Y-%m-%d 00:00:00'
#     end_fmt = '%Y-%m-%d 23:59:59'
#     kwargs = get_date_range(kwargs, question, fmt, end_fmt)
# if tool_name == 'get_history_features':
#     if "近五年" in question or "近5年" in question:
#         kwargs.update({'start_year': 2020, 'end_year': 2024})
#     if "历史" in question:
#         kwargs.update({'start_year': 2000, 'end_year': 2024})
            
# logger.info(f"{question} {tool_name} {kwargs}")
# try:
#     result = dispatch_tool(tool_name, kwargs)
# except Exception as e:
#     logger.error(f'dispatch_tool error:{e}')

# generate_template: Callable = GENERATR_TEMPLATE.get(tool_name)
# resp = generate_template(data=result)
# # messages.append(response.choices[0].message.model_dump()) 

# '''根据函数调用结果和用户问题，返回生成回复'''
# question = resp + '\n\n' + question
# messages = [
#     {'role': 'system', 'content': '根据下面函数生成的图表结果，请根据用户问题生成回复，要求回复简洁明了，不要重复用户问题'},
#     {'role': 'user', 'content': question},
# ]


# model_response = llm_model.invoke(messages=messages)

# print(model_response)

exit()

print(json.dumps(tools, ensure_ascii=False, indent=4))
model_response = model.invoke(messages=messages, tools=tools)

'''同步接口'''
def test_online_model():
    response = llm_model.invoke(messages)
    print(response['content'])

def test_sse_online_model():
    response = llm_model.sse_invoke(messages)
    for item in response:
        print(item['content'])


'''异步接口'''
async def async_test_online_model():
    response = await llm_model.ainvoke(messages)
    print(response)

async def async_test_sse_online_model():
    response = llm_model.asse_invoke(messages)
    async for item in response:
        print(item)

if __name__ == '__main__':
    test_online_model()
    # test_sse_online_model()
    # import asyncio
    # test_sse_online_model()
    # exit()
    # import sys
    # if sys.version_info < (3, 10):
    #     loop = asyncio.get_event_loop()
    # else:
    #     try:
    #         loop = asyncio.get_running_loop()
    #     except RuntimeError:
    #         loop = asyncio.new_event_loop()
    
    # asyncio.set_event_loop(loop)
    
    # loop.run_until_complete(async_test_sse_online_model())
