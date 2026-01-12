"""
成绩模型模块
"""
from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from app.models.base_model import BaseModel


class Score(BaseModel):
    """成绩记录模型"""
    __tablename__ = "scores"
    
    registration_id = Column(Integer, ForeignKey("registrations.id"), nullable=False, comment="报名ID")
    value = Column(DECIMAL(10, 3), nullable=False, comment="成绩值")
    round = Column(Enum("preliminary", "final", name="round_enum"), default="final", comment="轮次")
    rank = Column(Integer, nullable=True, comment="排名")
    points = Column(Integer, default=0, comment="得分")
    is_valid = Column(Boolean, default=True, comment="是否有效")
    invalid_reason = Column(String(200), nullable=True, comment="作废原因")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="录入人ID")
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="修改人ID")
    update_reason = Column(String(200), nullable=True, comment="修改原因")
    
    # 关联关系
    registration = relationship("Registration", back_populates="scores")
