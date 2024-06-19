from langchain.text_splitter import RecursiveCharacterTextSplitter
from fastapi import APIRouter, Depends, UploadFile, File, Form

from app.models import User
from app.loaders import get_text
from app.controller import get_current_user
from common.response import BaseResponse

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, 
    chunk_overlap=100,
    keep_separator=True,
    is_separator_regex=True,
    separators=['(?<=[。！？])']
)

router = APIRouter()

@router.post("/parsers")
async def doc_parsers(
    files: UploadFile = File(..., description="上传文件接口"),
    kb_name: str = Form(..., description="知识库", examples=["default"]),
    user: User = Depends(get_current_user)
) -> BaseResponse:
    
    
    return BaseResponse(
        code=200,
        msg="success",
        data=''
    )