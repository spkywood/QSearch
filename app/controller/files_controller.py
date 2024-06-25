#! python3
# -*- encoding: utf-8 -*-
'''
@File    : files_controller.py
@Time    : 2024/06/12 13:46:38
@Author  : longfellow
@Version : 1.0
@Email   : longfellow.wang@gmail.com
'''


import uuid
import json
import uvloop
import asyncio
from io import BytesIO
from datetime import datetime
from typing import List, Dict
from fastapi import APIRouter, Depends, UploadFile, File, Form
from langchain.text_splitter import RecursiveCharacterTextSplitter

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

from common import logger
from common.run_async import run_async
from common.response import BaseResponse
from common.cache import model_manager, ModelType

from app.models import User, KnowledgeFile
from app.loaders import get_text
from app.controller import get_current_user
from db.curds import add_knowledge_file, add_file_chunk, get_kb_hash_name

from app.runtime.embedding import Embedding
from db import minio_client, milvus_client, es_client

router = APIRouter()

embedding: Embedding = model_manager.load_models(
    'BAAI/bge-large-zh-v1.5', 
    device='cuda', 
    model_type=ModelType.EMBEDDING
)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500, 
    chunk_overlap=50,
    keep_separator=True,
    is_separator_regex=True,
    separators=['(?<=[。！？])']
)

async def kb_exist(kb_name: str):
    return minio_client.bucket_exists(kb_name)

async def save_files_in_threadpool(files: List[UploadFile], kb_name: str, override: bool= True): 
    def save_file(file: UploadFile, kb_name: str, override: bool=True) -> Dict:
        """
        保存文件函数
        """
        try:
            minio_client.upload_data(
                kb_name, file.filename, file.file, file.size
            )

            return dict(code=200, msg="success", data=file.filename)
        except Exception as e:
            logger.exception(f'{e}')

            return dict(code=500, msg="failure", data=file.filename)
        
    tasks = [run_async(save_file, file, kb_name, override) for file in files]
    for resp in await asyncio.gather(*tasks):
        yield resp

@router.post("/upload_docs")
async def upload_docs(
    files: List[UploadFile] = File(..., description="批量上传文件接口"),
    kb_name: str = Form(..., description="知识库名称", examples=["default"]),
    override: bool = Form(True, description="覆盖已有文件")
) -> BaseResponse:
    
    success_files = []
    failure_files = []
    async for resp in save_files_in_threadpool(files, kb_name, override):
        if resp["code"] == 200:
            success_files.append(resp["data"])
        if resp["code"] == 500:
            failure_files.append(resp["data"])

    return BaseResponse(
        code=200,
        msg = "success",
        data=[{
            "success_files" : success_files,
            "failure_files" : failure_files
        }]
    )


@router.post("/parser/docs", summary="文档解析接口")
async def doc_parsers(
    file: bytes = File(..., description="上传文件接口"),
    filename: str = Form(..., description="文件名", examples=["example.pdf"]),
    kb_name: str = Form(..., description="知识库", examples=["default"]),
    user: User = Depends(get_current_user)
) -> BaseResponse:
    hash_name = await get_kb_hash_name(kb_name, user.id)
    if hash_name is None:
        return BaseResponse(code=404, msg="failure", data="知识库不存在，请创建")
    
    file_ext = filename.split('.')[-1]
    text = get_text(file, ext=f'.{file_ext}')
    if text == '':
        return BaseResponse(code=304, msg="failure", data="文件处理异常")
    
    minio_client.upload_data(hash_name, filename, BytesIO(file), len(file))
    minio_url = minio_client.get_obj_url(hash_name, filename)

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

        vector = embedding.encode(chunk, max_length=512)[0].tolist()
        logger.info(len(vector))
        milvus_rows.append({
            "kb_name": kb_name,
            "chunk": chunk,
            "chunk_uuid": chunk_uuid,
            "vector": vector,
            "metadata": {}
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

    milvus_client.insert(hash_name, milvus_rows)
    es_client.insert(hash_name, es_rows)
  
    """
    数据库操作
    """
    return BaseResponse(
        code=200,
        msg="success",
        data=minio_url
    )

