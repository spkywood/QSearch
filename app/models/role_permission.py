#! python3
# -*- encoding: utf-8 -*-
'''
@File    : role_permission.py
@Time    : 2024/06/13 09:16:16
@Author  : longfellow
@Version : 1.0
@Email   : longfellow.wang@gmail.com
'''


from sqlalchemy import (
    Table, Column, Integer, ForeignKey
)

from app.models.base import BaseTable
from app.models.role import Role
from app.models.permission import Permission


role_permission_association = Table(
    'role_permission_association',
    BaseTable.metadata,
    Column('role_id', Integer, ForeignKey(Role.id)),
    Column('permission_id', Integer, ForeignKey(Permission.id))
)