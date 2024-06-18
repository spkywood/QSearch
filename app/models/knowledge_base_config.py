from app.models import BaseTable

from sqlalchemy import String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

class KnowledgeBaseConfig(BaseTable):
    __tablename__ = "knowledge_base_configs"

    kb_id: Mapped[int] = mapped_column(Integer, ForeignKey('knowledge_bases.id'), nullable=False, comment='知识库ID')
    search_mode: Mapped[str] = mapped_column(String(20), nullable=False, comment="搜索模式")
    embedding_model: Mapped[str] = mapped_column(String(20), nullable=False, comment="嵌入模型")
    process_type: Mapped[str] = mapped_column(String(20), nullable=False, comment="处理类型")
    slice_type: Mapped[str] = mapped_column(String(10), nullable=False, comment="切片类型")
    use_rerank: Mapped[bool] = mapped_column(Boolean, nullable=False, comment="是否使用rerank")
    max_count: Mapped[int] = mapped_column(Integer, default=1000, nullable=False, comment="最大数量")
    top_k: Mapped[int] = mapped_column(Integer, default=3, nullable=False, comment="topk")
    advance_query: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, comment="高级查询")

    knowledge_base = relationship("KnowledgeBase", back_populates="config")

