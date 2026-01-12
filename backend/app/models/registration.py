"""
报名模型模块
"""
from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base_model import BaseModel


class Registration(BaseModel):
    """报名记录模型"""
    __tablename__ = "registrations"
    __table_args__ = (
        UniqueConstraint("student_id", "event_id", name="uq_student_event"),
    )
    
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, comment="学生ID")
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False, comment="项目ID")
    group_id = Column(Integer, ForeignKey("event_groups.id"), nullable=True, comment="组别ID")
    lane_no = Column(Integer, nullable=True, comment="道次/序号")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="创建人ID")
    
    # 关联关系
    student = relationship("Student", back_populates="registrations")
    event = relationship("Event", back_populates="registrations")
    group = relationship("EventGroup", back_populates="registrations")
    scores = relationship("Score", back_populates="registration", cascade="all, delete-orphan")
