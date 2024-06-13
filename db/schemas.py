from pydantic import BaseModel, EmailStr, Field, field_validator
import re
from typing import Annotated


# class ItemBase(BaseModel):
#     title: str
#     description: str | None = None


# class ItemCreate(ItemBase):
#     pass


# class Item(ItemBase):
#     id: int
#     owner_id: int

#     class Config:
#         orm_mode = True

class UserCreate(BaseModel):
    email: EmailStr
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
    
class ChatSession(BaseModel):
    user_name: str
    topic: str