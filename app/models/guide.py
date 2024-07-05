'''
@File    :   guide.py
@Time    :   2024/06/18 13:26:30
@Author  :   wangxh 
@Version :   1.0
@Desc    :   None
'''


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
from app.schemas.llm import QAType
import enum

from sqlalchemy import String, Boolean, Enum
from sqlalchemy.orm import (
    relationship, mapped_column, Mapped
)

class Guide(BaseTable):
    __tablename__ = "guides"

    content: Mapped[str] = mapped_column(String(2000))
    qa_type: Mapped[QAType] = mapped_column(Enum(QAType), nullable=False, default=QAType.LLM)
