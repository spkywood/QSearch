#! python3
# -*- encoding: utf-8 -*-
'''
@File    : base.py
@Time    : 2024/06/11 16:12:30
@Author  : longfellow
@Version : 1.0
@Email   : longfellow.wang@gmail.com
'''


from sqlalchemy.orm import (
    Mapped,
    DeclarativeBase,
    mapped_column
)
from sqlalchemy import Integer, DateTime
from datetime import datetime

class BaseTable(DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True, 
        autoincrement=True,
        sort_order=-1
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        sort_order=100
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.now, 
        onupdate=datetime.now,
        sort_order=101
    )

    def __repr__(self):
        return str(self.to_dict())
    
    def __str__(self):
        return str(self.to_dict())
    
    def to_dict(self, alias_dict: dict = None, exclude_none=True) -> dict:
        """
        数据库模型转成字典
        Args:
            alias_dict: 字段别名字典 eg: {"id": "user_id"}, 把id名称替换成 user_id
            exclude_none: 默认排查None值
        Returns: dict
        """
        alias_dict = alias_dict or {}
        if exclude_none:
            return {
                alias_dict.get(c.name, c.name): getattr(self, c.name)
                for c in self.__table__.columns if getattr(self, c.name) is not None
            }
        else:
            return {
                alias_dict.get(c.name, c.name): getattr(self, c.name, None)
                for c in self.__table__.columns
            }