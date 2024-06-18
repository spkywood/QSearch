'''
@File    :   kb_controller.py
@Time    :   2024/06/18 15:26:15
@Author  :   wangxh 
@Version :   1.0
@Desc    :   None
'''

# here put the import lib
import random
from fastapi import APIRouter, Depends, HTTPException, status


from common.response import BaseResponse
from app.models import User
from db.schemas import Token, KnowledgeCreate, GuideCreate
from db.curds import add_knowledge_base, query_guides, add_guide
from app.controller import (
    get_current_user, is_root_user,
    get_password_hash,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user
)

router = APIRouter()


@router.post("/create_kb", description="创建知识库")
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
    knowledgebase = await add_knowledge_base(kb.name, kb.icon, kb.desc, user.id)

    return BaseResponse(
        code=200,
        msg="success",
        data={
            "name": knowledgebase.name,
            "icon": knowledgebase.icon,
            "desc": knowledgebase.desc,
        }
    )

@router.get("/guides", description="获取引导词")
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

    if (len(guides) > 9):
         guides = random.sample(guides, 9)

    return BaseResponse(
        code=200,
        msg="success",
        data=[
            {
                "content" : guide.content,
                "qa_type": guide.qa_type,
            } for guide in guides
        ]
    )


@router.post("/guides", description="增加引导词")
async def get_guides(
    guide: GuideCreate,
    user: User = Depends(get_current_user)
) -> BaseResponse:
    """
    创建知识库: 
        minio  -> 创建bucket
        es     -> 创建index
        milvus -> 创建collection
    
        mysql  -> 写入数据库
    """
    
    guide = await add_guide(guide.content, guide.qa_type)

    return BaseResponse(
        code=200,
        msg="success",
        data={
            "content" : guide.content,
            "qa_type": guide.qa_type,
        }
    )
