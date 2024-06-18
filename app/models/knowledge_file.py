from app.models import BaseTable

from sqlalchemy import String, Integer, Boolean, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

class KnowledgeFile(BaseTable):
    __tablename__ = "knowledge_files"

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    kb_name: Mapped[str] = mapped_column(String(10), nullable=False, comment="知识库名称")
    file_name: Mapped[str] = mapped_column(String(100), nullable=False, comment="文件名称")
    file_ext: Mapped[str] = mapped_column(String(10), nullable=False, comment="文件扩展名")
    minio_url: Mapped[str] = mapped_column(String(200), nullable=False, comment="文件存储地址")
    doc_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="向量库文档ID")
    process_type: Mapped[str] = mapped_column(String(10), nullable=True, comment="处理类型")
    slice_type: Mapped[str] = mapped_column(String(10), nullable=True, comment="切片类型")
    weights: Mapped[int] = mapped_column(Integer, nullable=True, comment="权重")
    meta_data: Mapped[dict] = mapped_column(JSON, nullable=True, comment="文件元数据")
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, comment="是否已删除")
