# from redis.asyncio import Redis
# from setting import REDIS_HOST, REDIS_PORT

# import json
# import asyncio

# redis = Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# async def get_redis():
#     # redis_name = 'conversation:test'
#     # key = '6c1029a1-231a-59b3-9458-9f7b0261d942'
#     # a = await redis.hget(redis_name, key)
#     # a = json.loads(a)
#     # print(a)

    
#     context = await redis.hget('question:test', '01de7279-7f12-56df-bf12-7ac4dea86e06')
#     a = json.loads(context)
#     print(context)

# if __name__ == '__main__':
#     # 异步 main 函数
#     import sys
#     if sys.version_info < (3, 10):
#         loop = asyncio.get_event_loop()
#     else:
#         try:
#             loop = asyncio.get_running_loop()
#         except RuntimeError:
#             loop = asyncio.new_event_loop()
    
#     asyncio.set_event_loop(loop)
    
#     loop.run_until_complete(get_redis())