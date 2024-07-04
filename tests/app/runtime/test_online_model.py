from setting import QWEN_API_KEY
from app.runtime.online_model import OnlineModel
model = OnlineModel(QWEN_API_KEY, base_url='https://dashscope.aliyuncs.com/compatible-mode/v1')

messages = [
    {'role': 'system', 'content': 'You are a helpful assistant.'},
    {'role': 'user', 'content': '四大发明是哪些？分别有谁发明？'},
]

'''同步接口'''
def test_online_model():
    response = model.invoke(messages)
    print(response)

def test_sse_online_model():
    response = model.sse_invoke(messages)
    for item in response:
        print(item)


'''异步接口'''
async def async_test_online_model():
    response = await model.ainvoke(messages)
    print(response)

async def async_test_sse_online_model():
    response = model.asse_invoke(messages)
    async for item in response:
        print(item)

if __name__ == '__main__':
    import asyncio
    # test_sse_online_model()
    # exit()
    import sys
    if sys.version_info < (3, 10):
        loop = asyncio.get_event_loop()
    else:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
    
    asyncio.set_event_loop(loop)
    
    loop.run_until_complete(async_test_sse_online_model())