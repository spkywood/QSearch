#! python3
# -*- encoding: utf-8 -*-
'''
@File    : permission.py
@Time    : 2024/06/13 09:11:03
@Author  : longfellow
@Version : 1.0
@Email   : longfellow.wang@gmail.com
'''



from app.models import BaseTable

from sqlalchemy import String, Boolean
from sqlalchemy.orm import (
    relationship, mapped_column, Mapped
)

class Permission(BaseTable):
    __tablename__ = "permissions"

    name: Mapped[str] = mapped_column(String(100), unique=True)
    
