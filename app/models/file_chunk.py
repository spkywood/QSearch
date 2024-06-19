from app.models import BaseTable

from sqlalchemy import String, Integer, Boolean, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

class FileChunk(BaseTable):
    __tablename__ = "file_chunks"

    file_id: Mapped[int] = mapped_column(Integer, ForeignKey("knowledge_files.id"), nullable=False, comment="文件ID")
    chunk_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="切片ID")
    chunk: Mapped[str] = mapped_column(String(2000), nullable=False, comment="切片文本")
    chunk_uuid: Mapped[str] = mapped_column(String(36), nullable=False, comment="向量UUID")

    file = relationship("KnowledgeFile", back_populates="chunks")
