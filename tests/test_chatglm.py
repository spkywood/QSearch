# from app.runtime.llm_chatglm import LLMChatGLM
# from tools.register import tools, dispatch_tool, _TOOL_HOOKS

# from setting import CHATGLM_API_KEY, QWEN_API_KEY

# # 创建一个ChatGLM实例
# chatglm = LLMChatGLM(api_key=CHATGLM_API_KEY, model_name="glm-4")

# import json

# async def test_chatglm(question):
#     messages = [
#         {'role': 'system', 'content': '不要假设或猜测传入函数的参数值。如果用户的描述不明确，请要求用户提供必要信息'},
#         {'role': 'user', 'content': question}
#     ]

#     model_response = chatglm.invoke(messages=messages, tools=tools)
#     print(model_response)
#     exit()
#     func_name = model_response['tool_calls'][0].get('function').get('name')
#     func_args = model_response.get('tool_calls')[0].get('function').get('arguments')
#     result = dispatch_tool(func_name, func_args)
#     # for model_message in model_response:
#     #     model_message = json.loads(model_message)
#     #     # print(type(model_message))
#     #     print(model_message)
#     #     # func_name = model_message['tool_calls'][0]
#     #     # print(func_name)
#     #     # func_args = model_message.get('tool_calls')[0].get('function').get('arguments')
#     #     # dispatch_tool(func_name, func_args)
#     # return None
#     print('--------------', result)

# async def main():
#     # question = "最近七天，小浪底水库水情情况如何"
#     question = "明天北京到上海机票多少钱"
#     response = await test_chatglm(question)


# if __name__ == '__main__':
#     import asyncio
#     import sys
#     if sys.version_info < (3, 10):
#         loop = asyncio.get_event_loop()
#     else:
#         try:
#             loop = asyncio.get_running_loop()
#         except RuntimeError:
#             loop = asyncio.new_event_loop()
    
#     asyncio.set_event_loop(loop)
    
#     loop.run_until_complete(main())
     