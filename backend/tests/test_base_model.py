"""
基础信息模型属性测试
Feature: sports-meeting-teacher-system, Property 4: 班级年级关联一致性
Validates: Requirements 2.2
"""
import pytest
from hypothesis import given, strategies as st, settings as hyp_settings
from sqlalchemy.exc import IntegrityError

from app.models.base import Grade, Class, Student


class TestBaseModelProperties:
    """基础信息模型属性测试类"""
    
    @given(
        grade_name=st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('L', 'N'))),
        class_name=st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('L', 'N')))
    )
    @hyp_settings(max_examples=100)
    def test_class_grade_association_property(self, db_session, grade_name, class_name):
        """
        Property 4: 班级年级关联一致性
        对于任意创建的班级记录，其关联的年级ID必须指向一个存在的年级记录。
        Validates: Requirements 2.2
        """
        # 清理数据
        db_session.query(Class).delete()
        db_session.query(Grade).delete()
        db_session.commit()
        
        # 创建年级
        grade = Grade(name=grade_name, sort_order=1)
        db_session.add(grade)
        db_session.commit()
        
        # 创建班级并关联到存在的年级
        class_ = Class(name=class_name, grade_id=grade.id)
        db_session.add(class_)
        db_session.commit()
        
        # 验证关联一致性
        assert class_.grade_id == grade.id
        assert class_.grade.name == grade_name
        
        # 通过年级也能访问到班级
        assert class_ in grade.classes
    
    def test_class_invalid_grade_reference(self, db_session):
        """测试班级引用不存在的年级应该失败"""
        # 尝试创建引用不存在年级的班级
        class_ = Class(name="测试班级", grade_id=99999)
        db_session.add(class_)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
        
        db_session.rollback()
    
    def test_student_class_association(self, db_session):
        """测试学生与班级的关联"""
        # 创建年级和班级
        grade = Grade(name="一年级", sort_order=1)
        db_session.add(grade)
        db_session.commit()
        
        class_ = Class(name="1班", grade_id=grade.id)
        db_session.add(class_)
        db_session.commit()
        
        # 创建学生
        student = Student(
            class_id=class_.id,
            student_no="2024001",
            name="张三",
            gender="M"
        )
        db_session.add(student)
        db_session.commit()
        
        # 验证关联
        assert student.class_.id == class_.id
        assert student in class_.students
        
        # 通过班级可以访问年级
        assert student.class_.grade.name == "一年级"
    
    def test_student_no_uniqueness(self, db_session):
        """测试学号唯一性"""
        grade = Grade(name="一年级", sort_order=1)
        db_session.add(grade)
        db_session.commit()
        
        class_ = Class(name="1班", grade_id=grade.id)
        db_session.add(class_)
        db_session.commit()
        
        # 创建第一个学生
        student1 = Student(
            class_id=class_.id,
            student_no="2024001",
            name="张三",
            gender="M"
        )
        db_session.add(student1)
        db_session.commit()
        
        # 尝试创建相同学号的学生应该失败
        student2 = Student(
            class_id=class_.id,
            student_no="2024001",
            name="李四",
            gender="F"
        )
        db_session.add(student2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
        
        db_session.rollback()
    
    def test_cascade_delete(self, db_session):
        """测试级联删除"""
        # 创建完整的层级结构
        grade = Grade(name="一年级", sort_order=1)
        db_session.add(grade)
        db_session.commit()
        
        class_ = Class(name="1班", grade_id=grade.id)
        db_session.add(class_)
        db_session.commit()
        
        student = Student(
            class_id=class_.id,
            student_no="2024001",
            name="张三",
            gender="M"
        )
        db_session.add(student)
        db_session.commit()
        
        student_id = student.id
        class_id = class_.id
        
        # 删除年级应该级联删除班级和学生
        db_session.delete(grade)
        db_session.commit()
        
        assert db_session.query(Class).filter_by(id=class_id).first() is None
        assert db_session.query(Student).filter_by(id=student_id).first() is None
