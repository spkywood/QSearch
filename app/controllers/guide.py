#! python3
# -*- encoding: utf-8 -*-
'''
@File    : guide.py
@Time    : 2024/07/05 16:18:28
@Author  : longfellow 
@Email   : longfellow.wang@gmail.com
@Version : 1.0
@Desc    : None
'''



from typing import List
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy import select
from db.session import with_session

from app.models.guide import Guide
from app.schemas.llm import QAType

@with_session
async def add_guide(session: AsyncSession, content: str, qa_type: QAType) -> Guide:
    """
    添加引导词
    """
    guide = Guide(content=content, qa_type=qa_type)
    session.add(guide)
    session.commit()
    
    return guide



@with_session
async def query_guides(session: AsyncSession) -> List[Guide]:
    """
    获取引导词
    """
    query = await session.execute(select(Guide))
    guides = query.scalars().all()
    return guides
