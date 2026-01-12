"""
运动项目服务模块
实现项目CRUD、组别管理、预置模板加载
"""
from typing import List, Optional, Tuple, Dict
from sqlalchemy.orm import Session

from app.models.event import Event, EventGroup
from app.models.registration import Registration


# 预置项目模板
EVENT_TEMPLATES = [
    {"name": "100米", "type": "track", "unit": "秒", "max_per_class": 3, "has_preliminary": True},
    {"name": "200米", "type": "track", "unit": "秒", "max_per_class": 3, "has_preliminary": True},
    {"name": "400米", "type": "track", "unit": "秒", "max_per_class": 2, "has_preliminary": False},
    {"name": "800米", "type": "track", "unit": "分秒", "max_per_class": 2, "has_preliminary": False},
    {"name": "1500米", "type": "track", "unit": "分秒", "max_per_class": 2, "has_preliminary": False},
    {"name": "跳远", "type": "field", "unit": "米", "max_per_class": 3, "has_preliminary": False},
    {"name": "跳高", "type": "field", "unit": "米", "max_per_class": 2, "has_preliminary": False},
    {"name": "铅球", "type": "field", "unit": "米", "max_per_class": 2, "has_preliminary": False},
    {"name": "4x100米接力", "type": "relay", "unit": "秒", "max_per_class": 1, "has_preliminary": False},
]

# 默认计分规则
DEFAULT_SCORING_RULE = {"1": 9, "2": 7, "3": 6, "4": 5, "5": 4, "6": 3, "7": 2, "8": 1}


class EventService:
    """运动项目服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_event(
        self,
        name: str,
        type: str,
        unit: str,
        max_per_class: int = 3,
        max_per_student: int = 3,
        has_preliminary: bool = False,
        scoring_rule: Dict = None
    ) -> Tuple[Optional[Event], str]:
        """创建运动项目"""
        if type not in ("track", "field", "relay"):
            return None, "项目类型必须是track(径赛)、field(田赛)或relay(接力赛)"
        
        existing = self.db.query(Event).filter(Event.name == name).first()
        if existing:
            return None, "项目名称已存在"
        
        event = Event(
            name=name,
            type=type,
            unit=unit,
            max_per_class=max_per_class,
            max_per_student=max_per_student,
            has_preliminary=has_preliminary,
            scoring_rule=scoring_rule or DEFAULT_SCORING_RULE
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event, ""
    
    def update_event(
        self,
        event_id: int,
        name: str = None,
        type: str = None,
        unit: str = None,
        max_per_class: int = None,
        max_per_student: int = None,
        has_preliminary: bool = None,
        scoring_rule: Dict = None
    ) -> Tuple[Optional[Event], str]:
        """更新运动项目"""
        event = self.db.query(Event).filter(Event.id == event_id).first()
        if not event:
            return None, "项目不存在"
        
        if name and name != event.name:
            existing = self.db.query(Event).filter(Event.name == name).first()
            if existing:
                return None, "项目名称已存在"
            event.name = name
        
        if type:
            if type not in ("track", "field", "relay"):
                return None, "项目类型必须是track、field或relay"
            event.type = type
        
        if unit:
            event.unit = unit
        if max_per_class is not None:
            event.max_per_class = max_per_class
        if max_per_student is not None:
            event.max_per_student = max_per_student
        if has_preliminary is not None:
            event.has_preliminary = has_preliminary
        if scoring_rule is not None:
            event.scoring_rule = scoring_rule
        
        self.db.commit()
        self.db.refresh(event)
        return event, ""
    
    def delete_event(self, event_id: int) -> Tuple[bool, str, Dict[str, int]]:
        """删除运动项目"""
        event = self.db.query(Event).filter(Event.id == event_id).first()
        if not event:
            return False, "项目不存在", {}
        
        reg_count = len(event.registrations)
        if reg_count > 0:
            return False, f"该项目有{reg_count}条报名记录，请先删除报名", {
                "registrations": reg_count
            }
        
        self.db.delete(event)
        self.db.commit()
        return True, "", {}
    
    def get_event_list(self, type: str = None) -> List[Event]:
        """获取项目列表"""
        query = self.db.query(Event)
        if type:
            query = query.filter(Event.type == type)
        return query.order_by(Event.sort_order, Event.id).all()
    
    def get_event_by_id(self, event_id: int) -> Optional[Event]:
        """根据ID获取项目"""
        return self.db.query(Event).filter(Event.id == event_id).first()
    
    # ========== 组别管理 ==========
    
    def create_group(
        self,
        event_id: int,
        name: str,
        gender: str = "A",
        grade_ids: List[int] = None
    ) -> Tuple[Optional[EventGroup], str]:
        """创建项目组别"""
        event = self.db.query(Event).filter(Event.id == event_id).first()
        if not event:
            return None, "项目不存在"
        
        if gender not in ("M", "F", "A"):
            return None, "性别限制必须是M(男)、F(女)或A(不限)"
        
        group = EventGroup(
            event_id=event_id,
            name=name,
            gender=gender,
            grade_ids=grade_ids or []
        )
        self.db.add(group)
        self.db.commit()
        self.db.refresh(group)
        return group, ""
    
    def update_group(
        self,
        group_id: int,
        name: str = None,
        gender: str = None,
        grade_ids: List[int] = None
    ) -> Tuple[Optional[EventGroup], str]:
        """更新项目组别"""
        group = self.db.query(EventGroup).filter(EventGroup.id == group_id).first()
        if not group:
            return None, "组别不存在"
        
        if name:
            group.name = name
        if gender:
            if gender not in ("M", "F", "A"):
                return None, "性别限制必须是M、F或A"
            group.gender = gender
        if grade_ids is not None:
            group.grade_ids = grade_ids
        
        self.db.commit()
        self.db.refresh(group)
        return group, ""
    
    def delete_group(self, group_id: int) -> Tuple[bool, str]:
        """删除项目组别"""
        group = self.db.query(EventGroup).filter(EventGroup.id == group_id).first()
        if not group:
            return False, "组别不存在"
        
        reg_count = self.db.query(Registration).filter(Registration.group_id == group_id).count()
        if reg_count > 0:
            return False, f"该组别有{reg_count}条报名记录，请先删除报名"
        
        self.db.delete(group)
        self.db.commit()
        return True, ""
    
    # ========== 模板功能 ==========
    
    def get_templates(self) -> List[Dict]:
        """获取预置项目模板"""
        return EVENT_TEMPLATES
    
    def create_from_template(self, template_name: str) -> Tuple[Optional[Event], str]:
        """从模板创建项目"""
        template = next((t for t in EVENT_TEMPLATES if t["name"] == template_name), None)
        if not template:
            return None, "模板不存在"
        
        return self.create_event(
            name=template["name"],
            type=template["type"],
            unit=template["unit"],
            max_per_class=template["max_per_class"],
            has_preliminary=template["has_preliminary"]
        )
