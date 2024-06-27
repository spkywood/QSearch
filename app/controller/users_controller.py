#! python3
# -*- encoding: utf-8 -*-
'''
@File    : users_controller.py
@Time    : 2024/06/11 17:22:26
@Author  : longfellow
@Version : 1.0
@Email   : longfellow.wang@gmail.com
'''



import io
import base64
import random
import string
from datetime import timedelta
# from redis.asyncio import Redis
from captcha.image import ImageCaptcha
from fastapi import APIRouter, Depends, HTTPException, status


from common import logger
from db.schemas import UserCreate, UserLogin
from common.response import BaseResponse, ListResponse
from app.models import User
from db.schemas import Token
from db.curds import (
    query_user, add_user, query_user_with_name
)
from app.controller import (
    get_current_user, is_root_user,
    get_password_hash,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user
)
from db.redis_client import redis
# from setting import REDIS_HOST, REDIS_PORT

router = APIRouter()

# redis = Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def generate_captcha_text(length=4):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

@router.get("/captcha", summary="获取图片验证码")
async def get_captcha() -> BaseResponse:
    captcha_text = generate_captcha_text()
    captcha_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
    await redis.setex(captcha_id, 60, captcha_text)  # Captcha valid for 1 minutes
    # width=120, height=45, font_sizes=(30, 40, 42)
    image = ImageCaptcha().generate_image(captcha_text) 
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return BaseResponse(
        code=200,
        message="success",
        data={"captcha_id": captcha_id, "captcha_image": image_base64}
    )


@router.get("/users", description="获取所有用户信息", include_in_schema=False)
async def get_users(user: User = Depends(get_current_user)):
    if not is_root_user(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限"
        )

    users = await query_user()
    return ListResponse(
        code=200,
        message="success",
        data=[str(user) for user in users]
    )

@router.get("/users/{username}", summary="获取用户信息", include_in_schema=False)
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

@router.post("/users/create", summary="创建用户", include_in_schema=False)
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

@router.post("/users/login", summary="用户登录", include_in_schema=True)
async def login(
    user_login: UserLogin,
) -> BaseResponse:
    captcha_text: str = await redis.get(user_login.captcha_id)
    if not captcha_text or captcha_text.lower() != user_login.captcha.lower():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码输入错误",
        )

    user: User = await authenticate_user(user_login.name, user_login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.name}, expires_delta=access_token_expires
    )

    return BaseResponse(
        code=200,
        message="success",
        data = {
            "name" : user.name,
            "access_token": access_token,
            "token_type": "bearer",
        }
    )
