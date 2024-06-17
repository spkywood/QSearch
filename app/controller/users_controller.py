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
from fastapi import APIRouter, Depends, HTTPException, status

from db.curds import query_user, add_user, query_user_with_name
from common import logger
from db.schemas import UserCreate, UserLogin
from common.response import BaseResponse, ListResponse
from app.models import User
from db.schemas import Token, TokenData

router = APIRouter()

from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Optional, Union
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidKeyError


# 秘钥、算法和令牌过期时间
SECRET_KEY = "3322b42f3a0bb1120ab796880d9492c50197a350adfb0bd01ded297a3a2ad104"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

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
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        logger.info(f"{username}")
    except InvalidKeyError:
        raise credentials_exception
    
    user: User = await query_user_with_name(username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/users/")
async def get_users():
    users = await query_user()
    return ListResponse(
        code=200,
        message="success",
        data=[str(user) for user in users]
    )

@router.get("/users/{username}")
async def get_user(
    username: str = Depends(get_current_active_user)
) -> BaseResponse:
    logger.info(f"{type(username)} {username}")
    return BaseResponse(
        code=200,
        message="success",
        data=str(username)
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
