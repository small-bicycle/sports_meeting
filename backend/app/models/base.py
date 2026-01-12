"""
基础信息模型模块
包含年级、班级、学生模型
"""
from sqlalchemy import Column, String, Integer, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base_model import BaseModel


class Grade(BaseModel):
    """年级模型"""
    __tablename__ = "grades"
    
    name = Column(String(50), nullable=False, comment="年级名称")
    sort_order = Column(Integer, default=0, comment="排序序号")
    
    # 关联关系
    classes = relationship("Class", back_populates="grade", cascade="all, delete-orphan")


class Class(BaseModel):
    """班级模型"""
    __tablename__ = "classes"
    
    grade_id = Column(Integer, ForeignKey("grades.id"), nullable=False, comment="所属年级ID")
    name = Column(String(50), nullable=False, comment="班级名称")
    
    # 关联关系
    grade = relationship("Grade", back_populates="classes")
    students = relationship("Student", back_populates="class_", cascade="all, delete-orphan")


class Student(BaseModel):
    """学生模型"""
    __tablename__ = "students"
    
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False, comment="所属班级ID")
    student_no = Column(String(20), unique=True, nullable=False, index=True, comment="学号")
    name = Column(String(50), nullable=False, comment="姓名")
    gender = Column(Enum("M", "F", name="gender_enum"), nullable=False, comment="性别")
    
    # 关联关系
    class_ = relationship("Class", back_populates="students")
    registrations = relationship("Registration", back_populates="student", cascade="all, delete-orphan")
