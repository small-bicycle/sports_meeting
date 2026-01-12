"""
报名管理服务模块
实现报名创建、查重检测、限制校验、批量导入
"""
from typing import List, Optional, Tuple, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func
from openpyxl import load_workbook
from io import BytesIO

from app.models.registration import Registration
from app.models.base import Student, Class
from app.models.event import Event, EventGroup


class RegistrationService:
    """报名管理服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def check_duplicate(self, student_id: int, event_id: int) -> Tuple[bool, Optional[Registration]]:
        """
        检查是否重复报名
        返回: (是否重复, 已存在的报名记录)
        """
        existing = self.db.query(Registration).filter(
            Registration.student_id == student_id,
            Registration.event_id == event_id
        ).first()
        return existing is not None, existing
    
    def check_class_limit(self, class_id: int, event_id: int) -> Tuple[bool, int, int]:
        """
        检查班级报名人数限制
        返回: (是否超限, 当前人数, 限制人数)
        """
        event = self.db.query(Event).filter(Event.id == event_id).first()
        if not event:
            return True, 0, 0
        
        # 统计该班级在该项目的报名人数
        current_count = self.db.query(Registration).join(Student).filter(
            Student.class_id == class_id,
            Registration.event_id == event_id
        ).count()
        
        return current_count >= event.max_per_class, current_count, event.max_per_class
    
    def check_student_limit(self, student_id: int) -> Tuple[bool, int, int]:
        """
        检查学生报名项目数限制
        返回: (是否超限, 当前项目数, 限制数)
        """
        # 获取任意一个项目的限制（假设所有项目限制相同）
        event = self.db.query(Event).first()
        max_per_student = event.max_per_student if event else 3
        
        current_count = self.db.query(Registration).filter(
            Registration.student_id == student_id
        ).count()
        
        return current_count >= max_per_student, current_count, max_per_student
    
    def create_registration(
        self,
        student_id: int,
        event_id: int,
        group_id: int = None,
        created_by: int = None
    ) -> Tuple[Optional[Registration], str]:
        """创建报名记录"""
        # 检查学生是否存在
        student = self.db.query(Student).filter(Student.id == student_id).first()
        if not student:
            return None, "学生不存在"
        
        # 检查项目是否存在
        event = self.db.query(Event).filter(Event.id == event_id).first()
        if not event:
            return None, "项目不存在"
        
        # 检查重复报名
        is_duplicate, existing = self.check_duplicate(student_id, event_id)
        if is_duplicate:
            return None, "该学生已报名此项目"
        
        # 检查班级人数限制
        is_over_class_limit, current, limit = self.check_class_limit(student.class_id, event_id)
        if is_over_class_limit:
            return None, f"该班级报名人数已达上限({limit}人)"
        
        # 检查个人项目数限制
        is_over_student_limit, current, limit = self.check_student_limit(student_id)
        if is_over_student_limit:
            return None, f"该学生报名项目数已达上限({limit}项)"
        
        # 检查组别
        if group_id:
            group = self.db.query(EventGroup).filter(EventGroup.id == group_id).first()
            if not group or group.event_id != event_id:
                return None, "组别不存在或不属于该项目"
            
            # 检查性别限制
            if group.gender != "A" and group.gender != student.gender:
                return None, "该组别不允许该性别参加"
            
            # 检查年级限制
            if group.grade_ids and student.class_.grade_id not in group.grade_ids:
                return None, "该组别不允许该年级参加"
        
        registration = Registration(
            student_id=student_id,
            event_id=event_id,
            group_id=group_id,
            created_by=created_by
        )
        self.db.add(registration)
        self.db.commit()
        self.db.refresh(registration)
        return registration, ""
    
    def delete_registration(self, registration_id: int) -> Tuple[bool, str]:
        """取消报名"""
        registration = self.db.query(Registration).filter(Registration.id == registration_id).first()
        if not registration:
            return False, "报名记录不存在"
        
        # 检查是否有成绩记录
        if registration.scores:
            return False, "该报名已有成绩记录，不能取消"
        
        self.db.delete(registration)
        self.db.commit()
        return True, ""
    
    def get_registration_list(
        self,
        page: int = 1,
        page_size: int = 20,
        event_id: int = None,
        class_id: int = None,
        grade_id: int = None,
        student_id: int = None
    ) -> Tuple[List[Registration], int]:
        """获取报名列表"""
        query = self.db.query(Registration).join(Student).join(Class)
        
        if event_id:
            query = query.filter(Registration.event_id == event_id)
        if class_id:
            query = query.filter(Student.class_id == class_id)
        if grade_id:
            query = query.filter(Class.grade_id == grade_id)
        if student_id:
            query = query.filter(Registration.student_id == student_id)
        
        total = query.count()
        registrations = query.offset((page - 1) * page_size).limit(page_size).all()
        
        return registrations, total
    
    def update_lane_no(self, registration_id: int, lane_no: int) -> Tuple[bool, str]:
        """更新道次/序号"""
        registration = self.db.query(Registration).filter(Registration.id == registration_id).first()
        if not registration:
            return False, "报名记录不存在"
        
        registration.lane_no = lane_no
        self.db.commit()
        return True, ""
    
    def import_registrations(self, file_content: bytes, created_by: int = None) -> Tuple[int, int, List[str]]:
        """
        批量导入报名
        Excel格式: 学号, 项目名称, 组别名称(可选)
        返回: (成功数, 失败数, 错误列表)
        """
        success_count = 0
        fail_count = 0
        errors = []
        
        try:
            wb = load_workbook(BytesIO(file_content))
            ws = wb.active
            
            for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                if not row[0]:
                    continue
                
                try:
                    student_no = str(row[0]).strip()
                    event_name = str(row[1]).strip()
                    group_name = str(row[2]).strip() if len(row) > 2 and row[2] else None
                    
                    # 查找学生
                    student = self.db.query(Student).filter(Student.student_no == student_no).first()
                    if not student:
                        errors.append(f"第{row_idx}行: 学号'{student_no}'不存在")
                        fail_count += 1
                        continue
                    
                    # 查找项目
                    event = self.db.query(Event).filter(Event.name == event_name).first()
                    if not event:
                        errors.append(f"第{row_idx}行: 项目'{event_name}'不存在")
                        fail_count += 1
                        continue
                    
                    # 查找组别
                    group_id = None
                    if group_name:
                        group = self.db.query(EventGroup).filter(
                            EventGroup.event_id == event.id,
                            EventGroup.name == group_name
                        ).first()
                        if group:
                            group_id = group.id
                    
                    # 创建报名
                    registration, error = self.create_registration(
                        student_id=student.id,
                        event_id=event.id,
                        group_id=group_id,
                        created_by=created_by
                    )
                    
                    if error:
                        errors.append(f"第{row_idx}行: {error}")
                        fail_count += 1
                    else:
                        success_count += 1
                        
                except Exception as e:
                    errors.append(f"第{row_idx}行: {str(e)}")
                    fail_count += 1
            
            self.db.commit()
            
        except Exception as e:
            errors.append(f"文件解析错误: {str(e)}")
        
        return success_count, fail_count, errors
