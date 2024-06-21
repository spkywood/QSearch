
import re
from app.models import QAType
from typing import Optional, Union, List
from pydantic import BaseModel, EmailStr, Field, field_validator


class QAItem(BaseModel):
    model: str
    question: str
    stream: bool
    conv_uuid: str
    kb_name: List[str]

class RAGQuestion(BaseModel):
    question: str
    kb_name: str
    

class GuideCreate(BaseModel):
    content: str = Field(..., max_length=2000)
    qa_type: QAType

class KnowledgeCreate(BaseModel):
    name: str
    icon: str
    desc: str

class UserLogin(BaseModel):
    name: str
    password: str
    captcha_id: str
    captcha: str = Field(..., min_length=4, max_length=4)

    # 验证密码必须包含大写字母、小写字母和数字
    @field_validator('password')
    def validate_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('密码必须包含至少一个大写字母')
        if not re.search(r'[a-z]', v):
            raise ValueError('密码必须包含至少一个小写字母')
        if not re.search(r'\d', v):
            raise ValueError('密码必须包含至少一个数字')
        return v
    
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    password: str = Field(..., min_length=8)

    # 验证密码必须包含大写字母、小写字母和数字
    @field_validator('password')
    def validate_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('密码必须包含至少一个大写字母')
        if not re.search(r'[a-z]', v):
            raise ValueError('密码必须包含至少一个小写字母')
        if not re.search(r'\d', v):
            raise ValueError('密码必须包含至少一个数字')
        return v
    
import uuid
class ChatSession(BaseModel):
    topic: Optional[str] = "default"


class ChatHistoryRequest(BaseModel):
    uuid: uuid.UUID
    name: Optional[str] = "default"

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Union[str, None] = None

