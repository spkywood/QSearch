#! python3
# -*- encoding: utf-8 -*-
'''
@File    : item.py
@Time    : 2024/06/11 15:58:04
@Author  : longfellow
@Version : 1.0
@Email   : longfellow.wang@gmail.com
'''

from app.models import BaseTable

from sqlalchemy.orm import relationship, mapped_column
from sqlalchemy import Integer, String, ForeignKey

class Item(BaseTable):
    __tablename__ = "items"

    title = mapped_column(String(100), index=True)
    description = mapped_column(String(200), index=True)
    owner_id = mapped_column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="items")
