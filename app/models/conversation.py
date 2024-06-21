#! python3
# -*- encoding: utf-8 -*-
'''
@File    : conversation.py
@Time    : 2024/06/17 11:11:44
@Author  : longfellow
@Version : 1.0
@Email   : longfellow.wang@gmail.com
'''


from app.models import BaseTable

from sqlalchemy import String, Integer, JSON, ForeignKey
from sqlalchemy.orm import (
    relationship, mapped_column, Mapped
)

class Conversation(BaseTable):
    __tablename__ = "conversations"

    name: Mapped[str] = mapped_column(String(255), nullable=True, default='default')
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id', ondelete='CASCADE'))

    user = relationship('User', back_populates='conversations')