#! python3
# -*- encoding: utf-8 -*-
'''
@File    : user_org_role.py
@Time    : 2024/06/13 17:56:50
@Author  : longfellow
@Version : 1.0
@Email   : longfellow.wang@gmail.com
'''


from sqlalchemy import (
    Table, Column, Integer, ForeignKey
)

from app.models.base import BaseTable
from app.models import User, Origanization, Role


user_org_role = Table(
    'user_org_role',
    BaseTable.metadata,
    Column('user_id', Integer, ForeignKey(User.id)),
    Column('org_id', Integer, ForeignKey(Origanization.id)),
    Column('role_id', Integer, ForeignKey(Role.id))
)