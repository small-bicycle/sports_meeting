"""
操作日志模型模块
"""
from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from app.models.base_model import BaseModel


class OperationLog(BaseModel):
    """操作日志模型"""
    __tablename__ = "operation_logs"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="操作人ID")
    action = Column(String(50), nullable=False, comment="操作类型")
    target_type = Column(String(50), nullable=False, comment="目标类型")
    target_id = Column(Integer, nullable=True, comment="目标ID")
    detail = Column(JSON, default=dict, comment="操作详情")
    ip_address = Column(String(50), nullable=True, comment="IP地址")
