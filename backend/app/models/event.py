"""
运动项目模型模块
"""
from sqlalchemy import Column, String, Integer, Boolean, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.models.base_model import BaseModel


class Event(BaseModel):
    """运动项目模型"""
    __tablename__ = "events"
    
    name = Column(String(100), nullable=False, comment="项目名称")
    type = Column(Enum("track", "field", "relay", name="event_type_enum"), nullable=False, comment="类型")
    unit = Column(String(20), nullable=False, comment="成绩单位")
    max_per_class = Column(Integer, default=3, comment="每班限报人数")
    max_per_student = Column(Integer, default=3, comment="每人限报项目数")
    has_preliminary = Column(Boolean, default=False, comment="是否有预赛")
    scoring_rule = Column(JSON, default=dict, comment="计分规则")
    sort_order = Column(Integer, default=0, comment="排序序号")
    
    # 关联关系
    groups = relationship("EventGroup", back_populates="event", cascade="all, delete-orphan")
    registrations = relationship("Registration", back_populates="event", cascade="all, delete-orphan")


class EventGroup(BaseModel):
    """项目组别模型"""
    __tablename__ = "event_groups"
    
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False, comment="所属项目ID")
    name = Column(String(50), nullable=False, comment="组别名称")
    gender = Column(Enum("M", "F", "A", name="group_gender_enum"), default="A", comment="性别限制")
    grade_ids = Column(JSON, default=list, comment="适用年级ID列表")
    
    # 关联关系
    event = relationship("Event", back_populates="groups")
    registrations = relationship("Registration", back_populates="group")
