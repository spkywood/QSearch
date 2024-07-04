#! python3
# -*- encoding: utf-8 -*-
'''
@File    : curds.py
@Time    : 2024/06/11 16:18:54
@Author  : longfellow
@Version : 1.0
@Email   : longfellow.wang@gmail.com
'''


from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_

from app.models import (
    User, KnowledgeBase, FileChunk, KnowledgeFile,
    Guide, QAType,
    Conversation
)
from db.session import with_session
from common import logger

@with_session
async def add_user(session: AsyncSession, name, email, phone, password):
    stmt = select(User).where(User.name == name)
    query = await session.execute(stmt)
    user = query.scalar_one_or_none()
    if user is None:
        user = User(name=name, email=email, phone=phone, password=password)
        session.add(user)
        await session.commit()
        return user
    else:
        logger.warning(f"user {email} already exists")
        return None


@with_session
async def query_user(session: AsyncSession, user_id:int = None) -> List[User]:
    """
    查询用户接口
    
    :param user_id: None 查询所有用户 
                    int  查询单个用户
    :return: 用户列表
    """
    if user_id is not None:
        user = await session.get(User, user_id)
        return [user] if user is not None else []
    else:
        query = await session.execute(select(User))
        users = query.scalars().all()
        return users

@with_session
async def query_user_with_email(session: AsyncSession, email: str) -> User:
    """
    查询用户接口
    
    :param email: 用户邮箱
    :return: 用户列表
    """
    query = await session.execute(select(User).where(User.email == email))
    user = query.scalar_one_or_none()
    
    return user


@with_session
async def query_user_with_name(session: AsyncSession, name: str):
    """
    登陆接口
    """
    query = await session.execute(select(User).where(User.name == name))
    user = query.scalar_one_or_none()
    
    return user


@with_session
async def add_knowledge_base(
    session: AsyncSession,
    kb_name: str, 
    hash_name:str, kb_icon: str, kb_desc: str, user_id: int
) -> KnowledgeBase:
    """
    添加知识库
    """
    kb = KnowledgeBase(name=kb_name, hash_name=hash_name, icon=kb_icon, desc=kb_desc, user_id=user_id)
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


@with_session
async def add_knowledge_file(
    session: AsyncSession,
    user_id: int,
    kb_name: str,
    file_name: str,
    file_ext: str,
    process_type: str = None,
    slice_type: str = None,
    weights: int = None,
    meta_data: dict = None
) -> KnowledgeFile:
    file = KnowledgeFile(
        user_id=user_id, 
        kb_name=kb_name, 
        file_name=file_name, 
        file_ext=file_ext,
        process_type=process_type, 
        slice_type=slice_type, 
        weights=weights, 
        meta_data=meta_data
    )

    session.add(file)
    await session.commit()

    return file


@with_session
async def add_file_chunk(
    session: AsyncSession,
    file_id: int,
    chunk_id: int,
    chunk: str,
    chunk_uuid: str
) -> FileChunk:
    """
    数据库操作，将切片写入表中
    """
    file_chunk = FileChunk(
        file_id=file_id, chunk_id=chunk_id, chunk=chunk, chunk_uuid=chunk_uuid
    )
    session.add(file_chunk)
    await session.commit()

    return file_chunk

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


@with_session
async def query_chunk_with_uuid(session: AsyncSession, chunk_uuid: str) -> FileChunk:
    # [TODO] 待优化SQL
    stmt = select(FileChunk).where(FileChunk.chunk_uuid == chunk_uuid)
    result = await session.execute(stmt)
    chunk = result.scalar_one_or_none()

    stmt = select(KnowledgeFile.file_name).where(KnowledgeFile.id == chunk.file_id)
    result = await session.execute(stmt)
    file_name = result.scalar_one_or_none()
    return {
        "chunk_id" : chunk.chunk_id,
        "file_id" : chunk.file_id,
        "chunk" : chunk.chunk,
        "file_name" : file_name,
    }

@with_session
async def query_chunk_with_id(session: AsyncSession, file_id: int , chunk_id: int) -> FileChunk:
    # [TODO] 待优化SQL
    if chunk_id < 0:
        return ""
    stmt = select(FileChunk.chunk).where(and_(FileChunk.file_id == file_id, FileChunk.chunk_id == chunk_id))
    result = await session.execute(stmt)
    text = result.scalar_one_or_none()
    return text if text else ""


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
