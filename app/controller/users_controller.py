#! python3
# -*- encoding: utf-8 -*-
'''
@File    : users_controller.py
@Time    : 2024/06/11 17:22:26
@Author  : longfellow
@Version : 1.0
@Email   : longfellow.wang@gmail.com
'''


from pydantic import EmailStr
from fastapi import APIRouter, Body

from db.curds import query_user, add_user, query_user_with_email
from common import logger
from db.schemas import UserCreate
from common.response import BaseResponse, ListResponse


router = APIRouter()

@router.get("/users/")
async def get_users():
    users = await query_user()
    return ListResponse(
        code=200,
        message="success",
        data=[str(user) for user in users]
    )

@router.get("/users/{user_id}")
async def get_user(user_id: int):
    users = await query_user(user_id)
    logger.info(users)
    return ListResponse(
        code=200,
        message="success",
        data=[str(user) for user in users]
    )

@router.post("/users/create")
async def create_user(user: UserCreate):
    user = await add_user(user.email, user.password)
    if user is None:
        data=f"user {user.email} already exists"
    else:
        data=str(user)

    return BaseResponse(
            code=200,
            message="success",
            data=data
        )

@router.post("/users/login")
async def login(email: EmailStr, password: str):
    user = await query_user_with_email(email=email)
    if user is None:
        data=f"user {email} not exists"
    else:
        pass