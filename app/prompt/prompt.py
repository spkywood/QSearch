from langchain.prompts import PromptTemplate

qa_prompt = """<指令>根据从文档中节选的背景信息，简洁和专业的来回答问题。如果无法从中得到答案，请说 “根据已知信息无法回答该问题”。不允许在答案中添加编造成分，答案请使用中文。</指令>
<已知信息>{context}</已知信息>
<问题>{question}</问题>"""

def knowledge_qa_prompt(context, question) -> str:
    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=qa_prompt
    )
    return prompt.format(context=context, question=question)

function_args_parser = """
<指令>你是个python编程高手，请你根据给出的函数描述信息、参数信息，以及一段文本，请返回函数的请求参数。格式要求和参数信息一致。</指令>

# 函数描述信息
{tool_def}

# 文本
{question}

# 注意事项
1. 请严格按照函数描述信息中的参数格式返回参数。
2. 如果文本中无法获取参数，请返回空字典。
3. 返回的参数格式为json
4. 出现上一周，首先计算今天是今年的第几周，然后计算上一周startDate和endDate，返回格式为json
5. 出现过去一周，首先计算今天的时间，然后计算过去一周startDate和endDate，返回格式为json
6. 出现2024.6.12号前后，则意味着2024.6.12号前后各三天，计算startDate和endDate，返回格式为json

# 回复格式
请求json格式回复，字段为函数描述信息中的参数

** 不要返回任何json格式之外的内容 ，包括```json ```这个格式，不要试图扩写**
"""

def preprocess_prompt(tool_def, question) -> str:
    prompt = PromptTemplate(
        input_variables=["tool_def", "question"],
        template=function_args_parser
    )
    return prompt.format(tool_def=tool_def, question=question)
