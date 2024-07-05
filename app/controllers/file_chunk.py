#! python3
# -*- encoding: utf-8 -*-
'''
@File    : file_chunk.py
@Time    : 2024/07/05 11:37:57
@Author  : longfellow 
@Email   : longfellow.wang@gmail.com
@Version : 1.0
@Desc    : None
'''

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import  with_session
from app.models.file_chunk import FileChunk
from app.models.knowledge_file import KnowledgeFile

@with_session
async def add_file_chunk(
    session: AsyncSession,
    file_id: int,
    chunk_id: int,
    chunk: str,
    chunk_uuid: str
) -> FileChunk:
    """
    数据库操作，将切片写入表中
    """
    file_chunk = FileChunk(
        file_id=file_id, chunk_id=chunk_id, chunk=chunk, chunk_uuid=chunk_uuid
    )
    session.add(file_chunk)
    await session.commit()

    return file_chunk

@with_session
async def query_chunk_with_uuid(session: AsyncSession, chunk_uuid: str) -> FileChunk:
    # [TODO] 待优化SQL
    stmt = select(FileChunk).where(FileChunk.chunk_uuid == chunk_uuid)
    result = await session.execute(stmt)
    chunk = result.scalar_one_or_none()

    stmt = select(KnowledgeFile.file_name).where(KnowledgeFile.id == chunk.file_id)
    result = await session.execute(stmt)
    file_name = result.scalar_one_or_none()
    return {
        "chunk_id" : chunk.chunk_id,
        "file_id" : chunk.file_id,
        "chunk" : chunk.chunk,
        "file_name" : file_name,
    }

@with_session
async def query_chunk_with_id(session: AsyncSession, file_id: int , chunk_id: int) -> FileChunk:
    # [TODO] 待优化SQL
    if chunk_id < 0:
        return ""
    stmt = select(FileChunk.chunk).where(
        and_(FileChunk.file_id == file_id, FileChunk.chunk_id == chunk_id)
    )
    result = await session.execute(stmt)
    text = result.scalar_one_or_none()
    return text if text else ""
