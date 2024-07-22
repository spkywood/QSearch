import os
import json
from app.loaders import get_text

from app.runtime.embedding import Embedding
from db import minio_client, milvus_client, es_client

from langchain.text_splitter import RecursiveCharacterTextSplitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500, 
    chunk_overlap=50,
    keep_separator=True,
    is_separator_regex=True,
    separators=['(?<=[。！？])']
)

from app.core.cache import model_manager
from app.schemas.llm import ModelType
embedding: Embedding = model_manager.load_models(
    model='BAAI/bge-large-zh-v1.5', 
    device='cuda', 
    model_type=ModelType.EMBEDDING
)

import uuid
from datetime import datetime

from app.models import User, KnowledgeFile
from app.loaders import get_text
from app.core.oauth import get_current_user
from app.controllers.knowledge_base import get_kb_hash_name
from app.controllers.file_chunk import add_file_chunk
from app.controllers.knowledge_file import add_knowledge_file

import re
def split_text(text, chunk_size=500):
    sentences = re.split('(?<=[。！？\n \n\n])', text)
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) > chunk_size:
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""
        current_chunk += sentence
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

async def main():
    kb_name = 'demo'
    FILE_PATH = '/home/wangxh/workspace/pdf2markdown/markdown'
    # FILE_PATH = '/home/wangxh/workspace/pdf2markdown/book'
    files = [os.path.join(FILE_PATH, f) for f in os.listdir(FILE_PATH)]

    for file in files:
        filename = os.path.basename(file)
        
        ext = filename.split('.')[-1]
        text = get_text(file, ext=f'.{ext}')
        # with open(file, 'r') as f:
        #     text = f.read()

        hash_name = 'yjqewsa8lex7'
        # minio_client.upload_file(hash_name, filename, file_path=file)
        # minio_url = minio_client.get_obj_url(hash_name, filename)
        # print(minio_url)

        chunks = text_splitter.split_text(text)
        # chunks = split_text(text)

        # kb_file: KnowledgeFile = await add_knowledge_file(
        #     user_id=1,
        #     kb_name=kb_name,
        #     file_name=filename,
        #     file_ext=ext
        # ) 

        milvus_rows = []
        es_rows = []
        for index, chunk in enumerate(chunks):
            file_id = 19
            chunk_uuid = uuid.uuid4().hex

            await add_file_chunk(file_id=file_id, chunk_id=index, chunk=chunk, chunk_uuid=chunk_uuid)

            if len(chunk) > 1000:
                print(len(chunk))
            vector = embedding.encode(chunk, max_length=512)[0].tolist()

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

if __name__ == "__main__":
    import sys
    import asyncio
    if sys.version_info < (3, 10):
        loop = asyncio.get_event_loop()
    else:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
    
    asyncio.set_event_loop(loop)
    
    loop.run_until_complete(main())