"""
公示模型模块
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey, JSON
from app.models.base_model import BaseModel


class Announcement(BaseModel):
    """公示记录模型"""
    __tablename__ = "announcements"
    
    title = Column(String(200), nullable=False, comment="公示标题")
    share_code = Column(String(32), unique=True, nullable=False, index=True, comment="分享码")
    content_type = Column(Enum("event", "class", "grade", name="content_type_enum"), nullable=False, comment="内容类型")
    event_ids = Column(JSON, default=list, comment="包含的项目ID")
    is_active = Column(Boolean, default=True, comment="是否有效")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="创建人ID")
    closed_at = Column(DateTime, nullable=True, comment="关闭时间")
