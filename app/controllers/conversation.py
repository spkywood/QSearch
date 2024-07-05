#! python3
# -*- encoding: utf-8 -*-
'''
@File    : conversation.py
@Time    : 2024/07/05 11:16:44
@Author  : longfellow 
@Email   : longfellow.wang@gmail.com
@Version : 1.0
@Desc    : None
'''


from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import with_session
from app.models.conversation import Conversation

@with_session
async def add_conversation(session: AsyncSession, name: str, conv_uuid: str, user_id: int) -> Conversation:
    """   
    添加会话
    """
    conversation = Conversation(name=name, conv_uuid=conv_uuid, user_id=user_id)
    session.add(conversation)
    await session.commit()
    return conversation


@with_session
async def query_conversation(session: AsyncSession, user_id: int) -> List[Conversation]:
    """
    查询用户所有会话
    """
    query = await session.execute(select(Conversation).where(Conversation.user_id == user_id))
    conversations = query.scalars().all()
    return conversations