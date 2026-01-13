"""
运动项目服务模块
实现项目CRUD、组别管理、预置模板加载
"""
from typing import List, Optional, Tuple, Dict
from sqlalchemy.orm import Session

from app.models.event import Event, EventGroup
from app.models.registration import Registration


# 预置项目模板 - 按运动会标准分类
# is_team: 是否为团体项目
EVENT_TEMPLATES = [
    # ========== 径赛 ==========
    # 短距离跑
    {"name": "50米", "type": "track", "category": "短距离跑", "unit": "秒", "max_per_class": 3, "has_preliminary": True, "is_team": False},
    {"name": "60米", "type": "track", "category": "短距离跑", "unit": "秒", "max_per_class": 3, "has_preliminary": True, "is_team": False},
    {"name": "100米", "type": "track", "category": "短距离跑", "unit": "秒", "max_per_class": 3, "has_preliminary": True, "is_team": False},
    {"name": "200米", "type": "track", "category": "短距离跑", "unit": "秒", "max_per_class": 3, "has_preliminary": True, "is_team": False},
    {"name": "400米", "type": "track", "category": "短距离跑", "unit": "秒", "max_per_class": 2, "has_preliminary": True, "is_team": False},
    # 中距离跑
    {"name": "800米", "type": "track", "category": "中距离跑", "unit": "分秒", "max_per_class": 2, "has_preliminary": False, "is_team": False},
    {"name": "1000米", "type": "track", "category": "中距离跑", "unit": "分秒", "max_per_class": 2, "has_preliminary": False, "is_team": False},
    {"name": "1500米", "type": "track", "category": "中距离跑", "unit": "分秒", "max_per_class": 2, "has_preliminary": False, "is_team": False},
    {"name": "3000米", "type": "track", "category": "中距离跑", "unit": "分秒", "max_per_class": 2, "has_preliminary": False, "is_team": False},
    # 接力跑
    {"name": "4X100米接力", "type": "track", "category": "接力跑", "unit": "秒", "max_per_class": 1, "has_preliminary": False, "is_team": True},
    {"name": "4X200米接力", "type": "track", "category": "接力跑", "unit": "秒", "max_per_class": 1, "has_preliminary": False, "is_team": True},
    {"name": "4X400米接力", "type": "track", "category": "接力跑", "unit": "分秒", "max_per_class": 1, "has_preliminary": False, "is_team": True},
    {"name": "50米迎面接力", "type": "track", "category": "接力跑", "unit": "秒", "max_per_class": 1, "has_preliminary": False, "is_team": True},
    # 跨栏跑
    {"name": "100米栏", "type": "track", "category": "跨栏跑", "unit": "秒", "max_per_class": 2, "has_preliminary": True, "is_team": False},
    {"name": "110米栏", "type": "track", "category": "跨栏跑", "unit": "秒", "max_per_class": 2, "has_preliminary": True, "is_team": False},
    # 趣味（径赛类）
    {"name": "二人三足", "type": "track", "category": "趣味", "unit": "秒", "max_per_class": 2, "has_preliminary": False, "is_team": True},
    {"name": "推铁环", "type": "track", "category": "趣味", "unit": "秒", "max_per_class": 2, "has_preliminary": False, "is_team": False},
    # 游泳
    {"name": "蛙泳", "type": "track", "category": "游泳", "unit": "秒", "max_per_class": 2, "has_preliminary": True, "is_team": False},
    {"name": "自由泳", "type": "track", "category": "游泳", "unit": "秒", "max_per_class": 2, "has_preliminary": True, "is_team": False},
    {"name": "蝶泳", "type": "track", "category": "游泳", "unit": "秒", "max_per_class": 2, "has_preliminary": True, "is_team": False},
    {"name": "仰泳", "type": "track", "category": "游泳", "unit": "秒", "max_per_class": 2, "has_preliminary": True, "is_team": False},
    # 跳绳
    {"name": "30秒单摇跳", "type": "track", "category": "跳绳", "unit": "次", "max_per_class": 3, "has_preliminary": False, "is_team": False},
    {"name": "4X30秒单摇接力", "type": "track", "category": "跳绳", "unit": "次", "max_per_class": 1, "has_preliminary": False, "is_team": True},
    {"name": "2X30秒双摇跳", "type": "track", "category": "跳绳", "unit": "次", "max_per_class": 2, "has_preliminary": False, "is_team": True},
    {"name": "1X60秒交互绳", "type": "track", "category": "跳绳", "unit": "次", "max_per_class": 1, "has_preliminary": False, "is_team": True},
    
    # ========== 田赛 ==========
    # 投掷
    {"name": "铅球", "type": "field", "category": "投掷", "unit": "米", "max_per_class": 2, "has_preliminary": False, "is_team": False},
    {"name": "垒球", "type": "field", "category": "投掷", "unit": "米", "max_per_class": 2, "has_preliminary": False, "is_team": False},
    {"name": "实心球", "type": "field", "category": "投掷", "unit": "米", "max_per_class": 3, "has_preliminary": False, "is_team": False},
    {"name": "铁饼", "type": "field", "category": "投掷", "unit": "米", "max_per_class": 2, "has_preliminary": False, "is_team": False},
    {"name": "链球", "type": "field", "category": "投掷", "unit": "米", "max_per_class": 2, "has_preliminary": False, "is_team": False},
    {"name": "标枪", "type": "field", "category": "投掷", "unit": "米", "max_per_class": 2, "has_preliminary": False, "is_team": False},
    # 跳跃
    {"name": "跳高", "type": "field", "category": "跳跃", "unit": "米", "max_per_class": 2, "has_preliminary": False, "is_team": False},
    {"name": "跳远", "type": "field", "category": "跳跃", "unit": "米", "max_per_class": 3, "has_preliminary": False, "is_team": False},
    {"name": "立定跳远", "type": "field", "category": "跳跃", "unit": "米", "max_per_class": 3, "has_preliminary": False, "is_team": False},
    {"name": "三级跳远", "type": "field", "category": "跳跃", "unit": "米", "max_per_class": 2, "has_preliminary": False, "is_team": False},
    {"name": "跳绳", "type": "field", "category": "跳跃", "unit": "次", "max_per_class": 3, "has_preliminary": False, "is_team": False},
    # 趣味（田赛类）
    {"name": "掷沙包", "type": "field", "category": "趣味", "unit": "米", "max_per_class": 3, "has_preliminary": False, "is_team": False},
    {"name": "拔河", "type": "field", "category": "趣味", "unit": "胜负", "max_per_class": 1, "has_preliminary": False, "is_team": True},
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
        category: str = None,
        max_per_class: int = 3,
        max_per_student: int = 3,
        has_preliminary: bool = False,
        scoring_rule: Dict = None
    ) -> Tuple[Optional[Event], str]:
        """创建运动项目"""
        if type not in ("track", "field"):
            return None, "项目类型必须是track(径赛)或field(田赛)"
        
        existing = self.db.query(Event).filter(Event.name == name).first()
        if existing:
            return None, "项目名称已存在"
        
        event = Event(
            name=name,
            type=type,
            unit=unit,
            category=category,
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
        category: str = None,
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
            if type not in ("track", "field"):
                return None, "项目类型必须是track或field"
            event.type = type
        
        if category is not None:
            event.category = category
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
        """从模板创建项目，并自动创建默认组别"""
        template = next((t for t in EVENT_TEMPLATES if t["name"] == template_name), None)
        if not template:
            return None, "模板不存在"
        
        event, error = self.create_event(
            name=template["name"],
            type=template["type"],
            unit=template["unit"],
            category=template.get("category"),
            max_per_class=template["max_per_class"],
            has_preliminary=template["has_preliminary"]
        )
        
        if error:
            return None, error
        
        # 自动创建默认组别
        is_team = template.get("is_team", False)
        if is_team:
            # 团体项目：只创建一个"团体组"
            self.create_group(event_id=event.id, name="团体组", gender="A", grade_ids=[])
        else:
            # 个人项目：创建男子组和女子组
            self.create_group(event_id=event.id, name="男子组", gender="M", grade_ids=[])
            self.create_group(event_id=event.id, name="女子组", gender="F", grade_ids=[])
        
        # 刷新获取完整数据
        self.db.refresh(event)
        return event, ""
    
    def batch_create_from_templates(self, template_names: List[str]) -> Tuple[int, int, List[str]]:
        """批量从模板创建项目
        
        Returns:
            (成功数, 失败数, 错误信息列表)
        """
        success_count = 0
        fail_count = 0
        errors = []
        
        for name in template_names:
            event, error = self.create_from_template(name)
            if error:
                fail_count += 1
                errors.append(f"{name}: {error}")
            else:
                success_count += 1
        
        return success_count, fail_count, errors
    
    def delete_all_events(self) -> Tuple[int, str]:
        """删除所有项目（包括组别）
        
        Returns:
            (删除数量, 错误信息)
        """
        # 检查是否有报名记录
        reg_count = self.db.query(Registration).count()
        if reg_count > 0:
            return 0, f"存在{reg_count}条报名记录，请先清除所有报名数据"
        
        # 删除所有项目（组别会级联删除）
        count = self.db.query(Event).count()
        self.db.query(Event).delete()
        self.db.commit()
        
        # 重置自增ID（MySQL语法）
        from sqlalchemy import text
        self.db.execute(text("ALTER TABLE events AUTO_INCREMENT = 1"))
        self.db.execute(text("ALTER TABLE event_groups AUTO_INCREMENT = 1"))
        self.db.commit()
        
        return count, ""
