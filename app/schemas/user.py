#! python3
# -*- encoding: utf-8 -*-
'''
@File    : schemas.py
@Time    : 2024/07/04 16:06:05
@Author  : longfellow
@Version : 1.0
@Email   : longfellow.wang@gmail.com
'''


import re
from datetime import datetime
from fastapi import HTTPException, status
from pydantic import BaseModel, field_validator


class JWTPayload(BaseModel):
    user_id: int
    username: str
    exp: datetime


class LoginRequest(BaseModel):
    name: str
    password: str
    captcha_id: str
    captcha: str

    # 验证密码必须包含大写字母、小写字母和数字
    @field_validator('password')
    def validate_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='密码必须包含至少一个大写字母',
            )
        if not re.search(r'[a-z]', v):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='密码必须包含至少一个小写字母',
            )
        if not re.search(r'\d', v):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='密码必须包含至少一个数字',
            )
        return v

    @field_validator('captcha')
    def validate_captcha(cls, v):
        if len(v) != 4:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='验证码长度错误',
            )
        return v