#! python3
# -*- encoding: utf-8 -*-
'''
@File    : knowledge_file.py
@Time    : 2024/07/05 16:28:17
@Author  : longfellow 
@Email   : longfellow.wang@gmail.com
@Version : 1.0
@Desc    : None
'''


from sqlalchemy.ext.asyncio import AsyncSession

from db.session import with_session
from app.models.knowledge_file import KnowledgeFile

@with_session
async def add_knowledge_file(
    session: AsyncSession,
    user_id: int,
    kb_name: str,
    file_name: str,
    file_ext: str,
    process_type: str = None,
    slice_type: str = None,
    weights: int = None,
    meta_data: dict = None
) -> KnowledgeFile:
    file = KnowledgeFile(
        user_id=user_id, 
        kb_name=kb_name, 
        file_name=file_name, 
        file_ext=file_ext,
        process_type=process_type, 
        slice_type=slice_type, 
        weights=weights, 
        meta_data=meta_data
    )

    session.add(file)
    await session.commit()

    return file
