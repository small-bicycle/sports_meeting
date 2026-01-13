"""
导出服务属性测试
Feature: registration-export, Property 1: 班级列表过滤正确性
Validates: Requirements 1.1, 1.2, 1.3
"""
import pytest
from hypothesis import given, strategies as st, settings as hyp_settings, HealthCheck

from app.models.base import Grade, Class, Student
from app.models.event import Event, EventGroup
from app.models.registration import Registration
from app.services.export_service import ExportService


# ========== 测试数据生成策略 ==========

# 生成有效的中文名称
name_strategy = st.text(
    min_size=1, 
    max_size=10, 
    alphabet=st.characters(whitelist_categories=('L', 'N'))
)

# 生成性别
gender_strategy = st.sampled_from(['M', 'F'])


class TestExportServiceProperties:
    """导出服务属性测试类"""
    
    @given(
        num_grades=st.integers(min_value=1, max_value=3),
        num_classes_per_grade=st.integers(min_value=1, max_value=3),
        num_students_per_class=st.integers(min_value=0, max_value=5),
        classes_with_registrations=st.integers(min_value=0, max_value=9)
    )
    @hyp_settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_exportable_classes_filter_property(
        self, 
        db_session, 
        num_grades, 
        num_classes_per_grade, 
        num_students_per_class,
        classes_with_registrations
    ):
        """
        Feature: registration-export, Property 1: 班级列表过滤正确性
        
        *For any* 数据库中的班级集合，调用 get_exportable_classes() 返回的班级列表应该：
        - 只包含至少有一条报名记录的班级
        - 每个班级信息包含 id、name、grade_name、registration_count 字段
        - registration_count 等于该班级实际的报名记录数
        
        **Validates: Requirements 1.1, 1.2, 1.3**
        """
        # 清理数据
        db_session.query(Registration).delete()
        db_session.query(Student).delete()
        db_session.query(EventGroup).delete()
        db_session.query(Event).delete()
        db_session.query(Class).delete()
        db_session.query(Grade).delete()
        db_session.commit()
        
        # 创建测试数据
        all_classes = []
        student_counter = 0
        
        # 创建年级和班级
        for g in range(num_grades):
            grade = Grade(name=f"年级{g+1}", sort_order=g)
            db_session.add(grade)
            db_session.commit()
            
            for c in range(num_classes_per_grade):
                class_ = Class(name=f"{c+1}班", grade_id=grade.id)
                db_session.add(class_)
                db_session.commit()
                all_classes.append(class_)
                
                # 为每个班级创建学生
                for s in range(num_students_per_class):
                    student_counter += 1
                    student = Student(
                        class_id=class_.id,
                        student_no=f"STU{student_counter:05d}",
                        name=f"学生{student_counter}",
                        gender="M" if student_counter % 2 == 0 else "F"
                    )
                    db_session.add(student)
                db_session.commit()
        
        # 创建一个测试项目
        event = Event(
            name="100米跑",
            type="track",
            unit="秒",
            max_per_class=10,
            max_per_student=3
        )
        db_session.add(event)
        db_session.commit()
        
        # 为部分班级创建报名记录
        expected_registrations = {}  # class_id -> registration_count
        
        # 限制有报名的班级数量不超过实际班级数
        actual_classes_with_reg = min(classes_with_registrations, len(all_classes))
        
        for i in range(actual_classes_with_reg):
            class_ = all_classes[i]
            students = db_session.query(Student).filter(Student.class_id == class_.id).all()
            
            if students:
                # 为该班级的所有学生创建报名记录
                reg_count = 0
                for student in students:
                    registration = Registration(
                        student_id=student.id,
                        event_id=event.id
                    )
                    db_session.add(registration)
                    reg_count += 1
                
                if reg_count > 0:
                    expected_registrations[class_.id] = reg_count
        
        db_session.commit()
        
        # 调用被测方法
        service = ExportService(db_session)
        result = service.get_exportable_classes()
        
        # 验证属性1: 只包含有报名记录的班级
        result_class_ids = {item["id"] for item in result}
        expected_class_ids = set(expected_registrations.keys())
        assert result_class_ids == expected_class_ids, \
            f"返回的班级ID集合应该等于有报名记录的班级ID集合"
        
        # 验证属性2: 每个班级信息包含必要字段
        for item in result:
            assert "id" in item, "班级信息应包含id字段"
            assert "name" in item, "班级信息应包含name字段"
            assert "grade_id" in item, "班级信息应包含grade_id字段"
            assert "grade_name" in item, "班级信息应包含grade_name字段"
            assert "registration_count" in item, "班级信息应包含registration_count字段"
        
        # 验证属性3: registration_count 等于实际报名记录数
        for item in result:
            class_id = item["id"]
            expected_count = expected_registrations.get(class_id, 0)
            actual_count = item["registration_count"]
            assert actual_count == expected_count, \
                f"班级{class_id}的报名人数应为{expected_count}，实际为{actual_count}"


    @given(
        num_events=st.integers(min_value=1, max_value=3),
        num_groups_per_event=st.integers(min_value=0, max_value=3),
        num_registrations=st.integers(min_value=0, max_value=20)
    )
    @hyp_settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_group_registrations_by_event_group_property(
        self,
        db_session,
        num_events,
        num_groups_per_event,
        num_registrations
    ):
        """
        Feature: registration-export, Property 3: 组别分组正确性
        
        *For any* 班级的报名记录集合，生成的工作表内容应该：
        - 按 (项目名称, 组别名称) 分组显示
        - 每个组别区域包含组别标题行
        - 只显示有报名记录的组别
        - 无组别的报名记录归入"默认组"
        
        **Validates: Requirements 3.1, 3.2, 3.3, 3.4**
        """
        # 清理数据
        db_session.query(Registration).delete()
        db_session.query(Student).delete()
        db_session.query(EventGroup).delete()
        db_session.query(Event).delete()
        db_session.query(Class).delete()
        db_session.query(Grade).delete()
        db_session.commit()
        
        # 创建测试数据
        grade = Grade(name="测试年级", sort_order=1)
        db_session.add(grade)
        db_session.commit()
        
        class_ = Class(name="测试班级", grade_id=grade.id)
        db_session.add(class_)
        db_session.commit()
        
        # 创建项目和组别
        events = []
        all_groups = []
        for e in range(num_events):
            event = Event(
                name=f"项目{e+1}",
                type="track",
                unit="秒",
                max_per_class=10,
                max_per_student=3
            )
            db_session.add(event)
            db_session.commit()
            events.append(event)
            
            # 为每个项目创建组别
            for g in range(num_groups_per_event):
                group = EventGroup(
                    event_id=event.id,
                    name=f"组别{g+1}",
                    gender="A"
                )
                db_session.add(group)
                db_session.commit()
                all_groups.append(group)
        
        # 创建学生和报名记录
        registrations = []
        for i in range(num_registrations):
            student = Student(
                class_id=class_.id,
                student_no=f"STU{i+1:05d}",
                name=f"学生{i+1}",
                gender="M" if i % 2 == 0 else "F"
            )
            db_session.add(student)
            db_session.commit()
            
            if events:
                # 随机选择一个项目
                event = events[i % len(events)]
                
                # 随机决定是否有组别
                group = None
                if all_groups and i % 3 != 0:  # 1/3 的报名没有组别
                    # 选择属于该项目的组别
                    event_groups = [g for g in all_groups if g.event_id == event.id]
                    if event_groups:
                        group = event_groups[i % len(event_groups)]
                
                reg = Registration(
                    student_id=student.id,
                    event_id=event.id,
                    group_id=group.id if group else None
                )
                db_session.add(reg)
                registrations.append(reg)
        
        db_session.commit()
        
        # 刷新关联关系
        for reg in registrations:
            db_session.refresh(reg)
        
        # 调用被测方法
        service = ExportService(db_session)
        result = service._group_registrations_by_event_group(registrations)
        
        # 验证属性1: 按 (项目名称, 组别名称) 分组
        for key in result.keys():
            assert " - " in key, f"分组键应该包含 ' - ' 分隔符: {key}"
            parts = key.split(" - ")
            assert len(parts) == 2, f"分组键应该由项目名称和组别名称组成: {key}"
        
        # 验证属性2: 只显示有报名记录的组别
        total_regs_in_result = sum(len(regs) for regs in result.values())
        assert total_regs_in_result == len(registrations), \
            f"分组后的报名记录总数应该等于原始记录数: {total_regs_in_result} != {len(registrations)}"
        
        # 验证属性3: 无组别的报名记录归入"默认组"
        for reg in registrations:
            event_name = reg.event.name
            if reg.group is None:
                expected_key = f"{event_name} - 默认组"
                assert expected_key in result, \
                    f"无组别的报名记录应该归入默认组: {expected_key}"
                assert reg in result[expected_key], \
                    f"报名记录应该在默认组中"
            else:
                expected_key = f"{event_name} - {reg.group.name}"
                assert expected_key in result, \
                    f"有组别的报名记录应该在对应组中: {expected_key}"
                assert reg in result[expected_key], \
                    f"报名记录应该在对应组中"
        
        # 验证属性4: 组内按学号排序
        for key, regs in result.items():
            student_nos = [r.student.student_no for r in regs]
            assert student_nos == sorted(student_nos), \
                f"组 {key} 内的记录应该按学号排序"
