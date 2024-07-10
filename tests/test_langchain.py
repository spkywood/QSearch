from typing import List
from langchain_core.tools import tool

@tool
def search(query: str) -> List[str]:
    """Call to surf the web."""
    if 'sf' in query.lower() or 'san francisco' in query.lower():
        return ['It is 60 degrees and foggy.']
    else:
        return ['It is 90 degrees and foggy.']

tools = [search]

print(tools)

exit()
from langchain_core.runnables import (
    RunnableBranch,
    RunnableLambda,
    RunnableParallel,
    RunnablePassthrough,
)
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts.prompt import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import Tuple, List, Optional
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
import os
from langchain_community.graphs import Neo4jGraph
# from langchain.document_loaders import WikipediaLoader
# from langchain.document_loaders import Docx2txtLoader
# from langchain.text_splitter import TokenTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_community.llms.openai import OpenAIChat
from langchain_openai import OpenAIEmbeddings
# from yfiles_jupyter_graphs import GraphWidget
from langchain_experimental.graph_transformers import LLMGraphTransformer
from neo4j import GraphDatabase
from langchain_community.vectorstores import Neo4jVector
from langchain_community.vectorstores.neo4j_vector import remove_lucene_chars
from langchain_core.runnables import ConfigurableField, RunnableParallel, RunnablePassthrough

# from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatOpenAI
# from app.loaders import get_text

os.environ["NEO4J_URI"] = "bolt://localhost:7687"
os.environ["NEO4J_USERNAME"] = "neo4j"
os.environ["NEO4J_PASSWORD"] = "centN_2024"

graph = Neo4jGraph()

# raw_text = get_text('/home/wangxh/Documents/rag_demo/节约用水条例.docx', ext='.docx')

# with open('/home/wangxh/Documents/rag_demo/节约用水条例.txt', 'w') as f:
#     f.write(raw_text)

raw_documents = TextLoader('/home/wangxh/Documents/rag_demo/节约用水条例.txt').load()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500, 
    chunk_overlap=50,
    keep_separator=True,
    is_separator_regex=True,
    separators=['(?<=[。！？])']
)
documents = text_splitter.split_documents(raw_documents)

llm = ChatOpenAI(
    api_key='sk-bba06887e3ec4ab6ac6ba2144d7e7b68',
    base_url='https://dashscope.aliyuncs.com/compatible-mode/v1',
    model_name='qwen-max'
)

llm_transformer = LLMGraphTransformer(llm=llm)

graph_documents = llm_transformer.convert_to_graph_documents(documents)

graph.add_graph_documents(
    graph_documents=graph_documents,
    include_source=True,
    baseEntityLabel=True
)

from langchain_community.embeddings import HuggingFaceBgeEmbeddings

embeddings = HuggingFaceBgeEmbeddings(
    model_name='/home/wangxh/model/BAAI/bge-large-zh-v1.5',
    model_kwargs={'device': 'cuda'},
)

vector_index = Neo4jVector.from_existing_graph(
    embeddings,
    search_type="hybrid",
    node_label="Document",
    text_node_properties=["text"],
    embedding_node_property="embedding"
)

graph.query(
    "CREATE FULLTEXT INDEX entity IF NOT EXISTS FOR (e:__Entity__) ON EACH [e.id]")

# Extract entities from text
class Entities(BaseModel):
    """Identifying information about entities."""

    names: List[str] = Field(
        ...,
        description="文中出现的所有个人、组织、商业、规章、法律等实体",
    )

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "你是一个有用的助手，从文本中提取个人、组织、商业、规章、法律等实体。",
        ),
        (
            "human",
            "使用给定的格式从以下内容中提取信息"
            "输入: {question}",
        ),
    ]
)

print(llm.with_structured_output(Entities))

# entity_chain = prompt | llm.with_structured_output(Entities)

exit()
en1 = entity_chain.invoke({"question": "节水规划包括哪些方面？"}).names


def generate_full_text_query(input: str) -> str:
    """
    Generate a full-text search query for a given input string.

    This function constructs a query string suitable for a full-text search.
    It processes the input string by splitting it into words and appending a
    similarity threshold (~2 changed characters) to each word, then combines
    them using the AND operator. Useful for mapping entities from user questions
    to database values, and allows for some misspelings.
    """
    full_text_query = ""
    words = [el for el in remove_lucene_chars(input).split() if el]
    for word in words[:-1]:
        full_text_query += f" {word}~2 AND"
    full_text_query += f" {words[-1]}~2"
    return full_text_query.strip()


# Fulltext index query
def structured_retriever(question: str) -> str:
    """
    Collects the neighborhood of entities mentioned
    in the question
    """
    result = ""
    entities = entity_chain.invoke({"question": question})
    for entity in entities.names:
        response = graph.query(
            """CALL db.index.fulltext.queryNodes('entity', $query, {limit:2})
            YIELD node,score
            CALL {
              WITH node
              MATCH (node)-[r:!MENTIONS]->(neighbor)
              RETURN node.id + ' - ' + type(r) + ' -> ' + neighbor.id AS output
              UNION ALL
              WITH node
              MATCH (node)<-[r:!MENTIONS]-(neighbor)
              RETURN neighbor.id + ' - ' + type(r) + ' -> ' +  node.id AS output
            }
            RETURN output LIMIT 50
            """,
            {"query": generate_full_text_query(entity)},
        )
        result += "\n".join([el['output'] for el in response])
    return result

print(structured_retriever("Who is Elizabeth I?"))

def retriever(question: str):
    print(f"Search query: {question}")
    structured_data = structured_retriever(question)
    unstructured_data = [el.page_content for el in vector_index.similarity_search(question)]
    final_data = f"""Structured data:
{structured_data}
Unstructured data:
{"#Document ". join(unstructured_data)}
    """
    return final_data


# Condense a chat history and follow-up question into a standalone question
_template = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question,
in its original language.
Chat History:
{chat_history}
Follow Up Input: {question}
Standalone question:"""  # noqa: E501
CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(_template)

def _format_chat_history(chat_history: List[Tuple[str, str]]) -> List:
    buffer = []
    for human, ai in chat_history:
        buffer.append(HumanMessage(content=human))
        buffer.append(AIMessage(content=ai))
    return buffer

_search_query = RunnableBranch(
    # If input includes chat_history, we condense it with the follow-up question
    (
        RunnableLambda(lambda x: bool(x.get("chat_history"))).with_config(
            run_name="HasChatHistoryCheck"
        ),  # Condense follow-up question and chat into a standalone_question
        RunnablePassthrough.assign(
            chat_history=lambda x: _format_chat_history(x["chat_history"])
        )
        | CONDENSE_QUESTION_PROMPT
        | ChatOpenAI(temperature=0)
        | StrOutputParser(),
    ),
    # Else, we have no chat history, so just pass through the question
    RunnableLambda(lambda x : x["question"]),
)


template = """Answer the question based only on the following context:
{context}

Question: {question}
Use natural language and be concise.
Answer:"""
prompt = ChatPromptTemplate.from_template(template)

chain = (
    RunnableParallel(
        {
            "context": _search_query | retriever,
            "question": RunnablePassthrough(),
        }
    )
    | prompt
    | llm
    | StrOutputParser()
)

chain.invoke({"question": "Which house did Elizabeth I belong to?"})

chain.invoke(
    {
        "question": "When was she born?",
        "chat_history": [("Which house did Elizabeth I belong to?", "House Of Tudor")],
    }
)
