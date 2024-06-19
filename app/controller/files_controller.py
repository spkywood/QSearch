#! python3
# -*- encoding: utf-8 -*-
'''
@File    : files_controller.py
@Time    : 2024/06/12 13:46:38
@Author  : longfellow
@Version : 1.0
@Email   : longfellow.wang@gmail.com
'''


from typing import List, Dict
from fastapi import (
    APIRouter, Body, UploadFile, File, Form
)
import asyncio
import uvloop
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

from common.response import BaseResponse
from common.run_async import run_async
from common import logger
from db.minio_client import minio_client


router = APIRouter()

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
