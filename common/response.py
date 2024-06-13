#! python3
# -*- encoding: utf-8 -*-
'''
@File    : response.py
@Time    : 2024/06/12 10:15:10
@Author  : longfellow
@Version : 1.0
@Email   : longfellow.wang@gmail.com
'''


from typing import List, Any
from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    code: int = Field(200, description="API status code")
    msg: str = Field("success", description="API status message")
    data: Any = Field(None, description="API data")

    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "msg": "success",
                "data": "Some data"
            }
        }

class ListResponse(BaseResponse):
    data: List[str] = Field(..., description="List of names")

    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "msg": "success",
                "data": ["doc1.docx", "doc2.pdf", "doc3.txt"],
            }
        }
