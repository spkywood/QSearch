#! python3
# -*- encoding: utf-8 -*-
'''
@File    : knowledge_base.py
@Time    : 2024/07/05 11:36:19
@Author  : longfellow 
@Email   : longfellow.wang@gmail.com
@Version : 1.0
@Desc    : None
'''


from typing import List
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import with_session
from app.models.knowledge_base import KnowledgeBase

@with_session
async def add_knowledge_base(
    session: AsyncSession,
    kb_name: str, 
    hash_name:str, 
    kb_icon: str, 
    kb_desc: str, 
    user_id: int
) -> KnowledgeBase:
    """
    添加知识库
    """
    kb = KnowledgeBase(
        name=kb_name, hash_name=hash_name, icon=kb_icon, desc=kb_desc, user_id=user_id)
    session.add(kb)
    await session.commit()
    
    return kb

@with_session
async def query_knowledge_base(session: AsyncSession, user_id: int) -> List[KnowledgeBase]:
    """
    查询知识库
    """
    query = await session.execute(select(KnowledgeBase).where(KnowledgeBase.user_id == user_id))
    kbs = query.scalars().all()
    
    return kbs

@with_session
async def get_kb_hash_name(session: AsyncSession, kb_name: str , user_id: int) -> str:
    """
    查询知识库hash_name
    """
    query = await session.execute(
        select(KnowledgeBase.hash_name).where(
            and_(KnowledgeBase.name == kb_name, KnowledgeBase.user_id == user_id)
        )
    )
    hash_name = query.scalar_one_or_none()
    
    return hash_name

