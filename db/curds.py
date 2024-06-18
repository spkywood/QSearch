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

from app.models import User, KnowledgeBase, FileChunk, KnowledgeFile
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
    kb_name: str, kb_icon: str, kb_desc: str, user_id: int
) -> KnowledgeBase:
    """
    添加知识库
    """
    kb = KnowledgeBase(name=kb_name, icon=kb_icon, desc=kb_desc, user_id=user_id)
    session.add(kb)
    await session.commit()
    
    return kb

@with_session
async def add_knowledge_file(
    session: AsyncSession,
    user_id: int,
    kb_name: str,
    file_name: str,
    file_ext: str,
    minio_url: str,
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
        minio_url=minio_url, 
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
    text: str,
    chunk_uuid: str
) -> FileChunk:
    """
    数据库操作，将切片写入表中
    """
    file_chunk = FileChunk(
        file_id=file_id, chunk_id=chunk_id, text=text, chunk_uuid=chunk_uuid
    )
    session.add(file_chunk)
    await session.commit()

    return file_chunk