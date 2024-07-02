from jose import jwt
from pydantic import BaseModel, Field
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Union, Optional
from fastapi.security import OAuth2
from jwt.exceptions import InvalidKeyError
from jose.exceptions import ExpiredSignatureError
from fastapi import Depends, HTTPException, status, Request
from fastapi.openapi.models import OAuthFlows 

from loguru import logger


class OAuth2Password(OAuth2):
    def __init__(self, tokenUrl: str, scheme_name: Optional[str] = None, scopes: Optional[dict] = None, auto_error: bool = True):
        if not scopes:
            scopes = {}
        flows = OAuthFlows(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)
    
    async def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.headers.get("Authorization")
        if not authorization:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        
        # Extract token without "Bearer" prefix
        return authorization    

# 秘钥、算法和令牌过期时间
# openssl rand -hex 32
SECRET_KEY = "3322b42f3a0bb1120ab796880d9492c50197a350adfb0bd01ded297a3a2ad104"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30

AUTH_DICT = {
    "test" : "8f5ad4b447f0e23a2f47154481ec8187"
}

# 密码上下文用于哈希和验证
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# OAuth2 密码流
oauth2_scheme = OAuth2Password(tokenUrl="token")

# 验证密码
def verify_password(plain_password, hashed_password):
    return plain_password == hashed_password

# 验证用户
async def authenticate(accessKey: str, secretKey: str):
    value: str = AUTH_DICT.get(accessKey)
    if not value:
        return False
    if not verify_password(value, secretKey):
        return False
    return value

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_secret_key(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    expired_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail= "Token expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        accessKey: str = payload.get("sub")
        if accessKey is None:
            raise credentials_exception
    except InvalidKeyError:
        raise credentials_exception
    except ExpiredSignatureError:
        raise expired_exception
    
    secretKey = AUTH_DICT.get(accessKey)
    if secretKey is None:
        raise credentials_exception
    return secretKey
