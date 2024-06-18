#! python3
# -*- encoding: utf-8 -*-
'''
@File    : users_controller.py
@Time    : 2024/06/11 17:22:26
@Author  : longfellow
@Version : 1.0
@Email   : longfellow.wang@gmail.com
'''



from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from db.curds import query_user, add_user, query_user_with_name
from common import logger
from db.schemas import UserCreate
from common.response import BaseResponse, ListResponse
from app.models import User
from db.schemas import Token
from app.controller import (
    get_current_user, is_root_user,
    get_password_hash,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user
)

router = APIRouter()


@router.get("/users")
async def get_users(user: User = Depends(get_current_user)):
    if not is_root_user(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource"
        )

    users = await query_user()
    return ListResponse(
        code=200,
        message="success",
        data=[str(user) for user in users]
    )

@router.get("/users/{username}")
async def get_user(
    username: str,
    user: User = Depends(get_current_user)
) -> BaseResponse:
    logger.info(f"Authenticated user: {type(user)} {user}")
    user_exists = await query_user_with_name(username)
    if not user_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return BaseResponse(
        code=200,
        message="success",
        data=str(user)
    )

@router.post("/users/create")
async def create_user(user: UserCreate):
    password = get_password_hash(user.password)
    _user = await add_user(user.name, user.email, user.phone, password)
    if _user is None:
        data=f"user {user.name} already exists"
    else:
        data=str(_user)

    return BaseResponse(
            code=200,
            message="success",
            data=data
        )

@router.post("/users/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Token:
    user: User = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.name}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
