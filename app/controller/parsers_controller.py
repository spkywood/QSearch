import uuid
import json
from io import BytesIO
from datetime import datetime
from fastapi import APIRouter, Depends, UploadFile, File, Form
from langchain.text_splitter import RecursiveCharacterTextSplitter

from common import logger
from app.models import User
from app.loaders import get_text
from app.models import KnowledgeFile, FileChunk
from common.response import BaseResponse
from app.controller import get_current_user
from db.curds import add_knowledge_file, add_file_chunk

from app.runtime.embedding import Embedding
from db import minio_client, milvus_client, es_client
from common.cache import model_manager, ModelType

embedding: Embedding = model_manager.load_models(
    'BAAI/bge-large-zh-v1.5', 
    device='cuda', 
    model_type=ModelType.EMBEDDING
)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, 
    chunk_overlap=100,
    keep_separator=True,
    is_separator_regex=True,
    separators=['(?<=[。！？])']
)

router = APIRouter()

async def kb_exist(kb_name: str):
    return minio_client.bucket_exists(kb_name)

@router.post("/parser/docs")
async def doc_parsers(
    file: bytes = File(..., description="上传文件接口"),
    filename: str = Form(..., description="文件名", examples=["example.pdf"]),
    kb_name: str = Form(..., description="知识库", examples=["default"]),
    user: User = Depends(get_current_user)
) -> BaseResponse:
    if not await kb_exist(kb_name):
        return BaseResponse(code=404, msg="failure", data="知识库不存在，请创建")
    
    file_ext = filename.split('.')[-1]
    text = get_text(file, ext=f'.{file_ext}')
    if text == '':
        return BaseResponse(code=304, msg="failure", data="文件处理异常")
    
    minio_client.upload_data(kb_name, filename, BytesIO(file), len(file))
    minio_url = minio_client.get_obj_url(kb_name, filename)

    chunks = text_splitter.split_text(text)
    
    kb_file: KnowledgeFile = await add_knowledge_file(
        user_id=user.id,
        kb_name=kb_name,
        file_name=filename,
        file_ext=file_ext
    ) 

    milvus_rows = []
    es_rows = []
    for index, chunk in enumerate(chunks):
        file_id = kb_file.id
        chunk_uuid = uuid.uuid4().hex

        await add_file_chunk(file_id=file_id, chunk_id=index, chunk=chunk, chunk_uuid=chunk_uuid)

        milvus_rows.append({
            "kb_name": kb_name,
            "chunk": chunk,
            "uuid": chunk_uuid,
            "vector": embedding.encode(chunk, max_length=512).tolist(),
            "meta_data": {}
        })

        es_rows.append({
            "kb_name": kb_name,
            "file_name": filename,
            "chunk_id": index,
            "chunk_uuid": chunk_uuid,
            "chunk": chunk, 
            "metadata": json.dumps({}),
            "created_at": datetime.now()
        })

    milvus_client.insert(kb_name, milvus_rows)
    es_client.insert(kb_name, es_rows)
  
    """
    数据库操作
    """
    return BaseResponse(
        code=200,
        msg="success",
        data=minio_url
    )
