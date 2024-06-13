#! python3
# -*- encoding: utf-8 -*-
'''
@File    : role.py
@Time    : 2024/06/13 09:09:16
@Author  : longfellow
@Version : 1.0
@Email   : longfellow.wang@gmail.com
'''



from app.models import BaseTable

from sqlalchemy import String, Boolean
from sqlalchemy.orm import (
    relationship, mapped_column, Mapped
)

class Role(BaseTable):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(100), unique=True)
    