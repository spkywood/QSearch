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

from app.models import User, KnowledgeBase
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
    # name: Mapped[str] = mapped_column(String(20), nullable=False, comment='知识库名称')
    # icon: Mapped[str] = mapped_column(String(100), nullable=False, comment='知识库图标')
    # desc: Mapped[str] = mapped_column(String(200), nullable=False, comment='知识库描述')
    # user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False, comment='用户ID')
    # group_id: Mapped[int] = mapped_column(Integer, nullable=True, comment='团队ID')
    # is_delete: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True, comment='是否删除')

    kb = KnowledgeBase(name=kb_name, icon=kb_icon, desc=kb_desc, user_id=user_id)

    return kb
