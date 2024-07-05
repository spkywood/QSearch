#! python3
# -*- encoding: utf-8 -*-
'''
@File    : oauth.py
@Time    : 2024/07/05 09:31:25
@Author  : longfellow
@Version : 1.0
@Email   : longfellow.wang@gmail.com
'''


#! python3
# -*- encoding: utf-8 -*-
'''
@File    : oauth.py
@Time    : 2024/06/28 10:08:00
@Author  : longfellow
@Version : 1.0
@Email   : longfellow.wang@gmail.com
'''


from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidKeyError
from jose import jwt, JWTError, ExpiredSignatureError

from settings import APP_SECRET_KEY
from app.models.user import User
from app.schemas.user import JWTPayload
from app.controllers.user import query_user_with_name

# 秘钥、算法和令牌过期时间
# openssl rand -hex 32
SECRET_KEY = APP_SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 15


# 密码上下文用于哈希和验证
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# OAuth2 密码流
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 验证密码
def verify_password(plain_password: str, hashed_password: str) -> bool:
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


def create_access_token(data: JWTPayload):
    to_encode = data.model_dump().copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
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
        username: str = payload.get("username")
        if username is None:
            raise credentials_exception
    except ExpiredSignatureError:
        raise expired_exception
    except (InvalidKeyError, JWTError):
        raise credentials_exception
    
    user: User = await query_user_with_name(username)
    if user is None:
        raise credentials_exception
    return user

# 检查用户是否是 root
def is_root_user(user: User):
    # [TODO] 权限设计
    return user.name == "root"
