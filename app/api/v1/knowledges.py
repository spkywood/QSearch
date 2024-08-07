'''
@File    :   kb_controller.py
@Time    :   2024/06/18 15:26:15
@Author  :   wangxh 
@Version :   1.0
@Desc    :   None
'''

# here put the import lib
import random
import string
from fastapi import APIRouter, Depends, HTTPException, status


from app.models import User
from app.core.response import BaseResponse
from db import minio_client, es_client, milvus_client
from app.schemas.llm import KnowledgeCreate, GuideCreate
from app.core.oauth import get_current_user
from app.controllers.guide import add_guide, query_guides
from app.controllers.knowledge_base import add_knowledge_base, query_knowledge_base
from app.schemas.llm import QAType

router = APIRouter()


def hash_kb_name():
    a = ''.join(random.choices(string.ascii_lowercase, k=4))
    b = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return a+b


'''创建知识库'''
@router.post("/knowledge_base", summary="创建知识库")
async def create_kb(
    kb: KnowledgeCreate, 
    user: User = Depends(get_current_user)
) -> BaseResponse:
    """
    创建知识库: 
        minio  -> 创建bucket
        es     -> 创建index
        milvus -> 创建collection
    
        mysql  -> 写入数据库
    """
    # [TODO] 校验，知识库重名
    hash_name = hash_kb_name()
    minio_client.delete_bucket(hash_name)
    milvus_client.client.drop_collection(hash_name)
    es_client.delete_index(hash_name)

    minio_client.create_bucket(hash_name)
    es_client.create_index(hash_name)
    milvus_client.create_collection(hash_name, dim=1024)

    knowledgebase = await add_knowledge_base(kb.name, hash_name, kb.icon, kb.desc, user.id)

    return BaseResponse(
        code=200,
        msg="success",
        data={
            "name": knowledgebase.name,
            "icon": knowledgebase.icon,
            "desc": knowledgebase.desc,
        }
    )


'''获取知识库'''
@router.get("/knowledge_base", description="获取知识库", include_in_schema=False)
async def query_kb(
    user: User = Depends(get_current_user)
) -> BaseResponse:
    """
    创建知识库: 
        minio  -> 创建bucket
        es     -> 创建index
        milvus -> 创建collection
    
        mysql  -> 写入数据库
    """
    kbs = await query_knowledge_base(user.id)

    return BaseResponse(
        code=200,
        msg="success",
        data=[{
            "name": kb.name,
            "icon": kb.icon,
            "desc": kb.desc,
        } for kb in kbs]
    )

@router.get("/guides", summary="获取引导词")
async def get_guides(
    user: User = Depends(get_current_user)
) -> BaseResponse:
    """
    创建知识库: 
        minio  -> 创建bucket
        es     -> 创建index
        milvus -> 创建collection
    
        mysql  -> 写入数据库
    """
    guides = await query_guides()
    rag = [guide.content for guide in guides if guide.qa_type == QAType.RAG]
    tool = [guide.content for guide in guides if guide.qa_type == QAType.TOOL]

    rag_select = random.sample(rag, min(6, len(rag)))
    tool_select = random.sample(tool, min(4, len(tool)))
    return BaseResponse(
        code=200,
        msg="success",
        data = {
            "RAG": rag_select,
            "TOOL": tool_select
        }
    )


@router.post("/guides", summary="增加引导词")
async def get_guides(
    guide: GuideCreate,
    user: User = Depends(get_current_user)
) -> BaseResponse:
    guide = await add_guide(guide.content, guide.qa_type)

    return BaseResponse(
        code=200,
        msg="success",
        data={
            "content" : guide.content,
            "qa_type": guide.qa_type,
        }
    )
