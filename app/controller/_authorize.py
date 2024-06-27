#! python3
# -*- encoding: utf-8 -*-
'''
@File    : _authorize.py
@Time    : 2024/06/18 09:32:52
@Author  : longfellow
@Version : 1.0
@Email   : longfellow.wang@gmail.com
'''


from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Union
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidKeyError
from jose.exceptions import ExpiredSignatureError
from fastapi import Depends, HTTPException, status
from db.schemas import Token, TokenData

from app.models import User
from db.curds import query_user_with_name
from common import logger
from setting import APP_SECRET_KEY
from common.response import BaseResponse

# 秘钥、算法和令牌过期时间
# openssl rand -hex 32
SECRET_KEY = APP_SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 6000

# 密码上下文用于哈希和验证
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# OAuth2 密码流
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 验证密码
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# 获取密码的哈希值
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# 验证用户
async def authenticate_user(username: str, password: str):
    user: User = await query_user_with_name(username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证用户",
        headers={"WWW-Authenticate": "Bearer"},
    )

    expired_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail= "用户认证过期，请重新登录",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidKeyError:
        raise credentials_exception
    except ExpiredSignatureError:
        raise expired_exception
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail= "用户认证过期，请重新登录",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user: User = await query_user_with_name(username)
    if user is None:
        raise credentials_exception
    return user

# 检查用户是否是 root
def is_root_user(user: User):
    # [TODO] 权限设计
    return user.name == "root"
