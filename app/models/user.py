#! python3
# -*- encoding: utf-8 -*-
'''
@File    : user.py
@Time    : 2024/06/11 15:57:20
@Author  : longfellow
@Version : 1.0
@Email   : longfellow.wang@gmail.com
'''


from app.models import BaseTable

from sqlalchemy import String, Boolean
from sqlalchemy.orm import (
    relationship, mapped_column, Mapped
)

class User(BaseTable):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(100), unique=True)
    email: Mapped[str] = mapped_column(String(100), nullable=True)
    phone: Mapped[str] = mapped_column(String(100), nullable=True)
    password: Mapped[str] = mapped_column(String(500))

    knowledge_bases = relationship("KnowledgeBase", back_populates="user")

    conversations = relationship("Conversation", back_populates="user")
