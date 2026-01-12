"""
数据库初始化脚本
用于创建数据库表结构和初始数据
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine, Base, SessionLocal
from app.core.security import get_password_hash


def create_tables():
    """创建所有数据库表"""
    # 导入所有模型
    from app.models.user import User
    from app.models.base import Grade, Class, Student
    from app.models.event import Event, EventGroup
    from app.models.registration import Registration
    from app.models.score import Score
    from app.models.announcement import Announcement
    from app.models.log import OperationLog
    
    print("正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成！")


def create_default_admin():
    """创建默认管理员账号"""
    from app.models.user import User
    
    db = SessionLocal()
    try:
        # 检查是否已存在管理员
        admin = db.query(User).filter(User.username == "admin").first()
        if admin:
            print("管理员账号已存在，跳过创建")
            return
        
        # 创建默认管理员
        admin = User(
            username="admin",
            password_hash=get_password_hash("admin123"),
            name="系统管理员",
            permissions=[],
            is_admin=True,
            is_active=True
        )
        db.add(admin)
        db.commit()
        print("默认管理员账号创建成功！")
        print("  账号: admin")
        print("  密码: admin123")
        print("  请登录后立即修改密码！")
    finally:
        db.close()


def create_event_templates():
    """创建预置运动项目模板"""
    from app.models.event import Event
    
    templates = [
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
    
    db = SessionLocal()
    try:
        existing = db.query(Event).count()
        if existing > 0:
            print(f"已存在 {existing} 个项目，跳过模板创建")
            return
        
        for tpl in templates:
            event = Event(
                name=tpl["name"],
                type=tpl["type"],
                unit=tpl["unit"],
                max_per_class=tpl["max_per_class"],
                max_per_student=3,  # 默认每人限报3项
                has_preliminary=tpl["has_preliminary"],
                scoring_rule={"1": 9, "2": 7, "3": 6, "4": 5, "5": 4, "6": 3, "7": 2, "8": 1}
            )
            db.add(event)
        
        db.commit()
        print(f"成功创建 {len(templates)} 个预置项目模板！")
    finally:
        db.close()


def main():
    """主函数"""
    print("=" * 50)
    print("校园运动会管理系统 - 数据库初始化")
    print("=" * 50)
    
    create_tables()
    create_default_admin()
    create_event_templates()
    
    print("=" * 50)
    print("数据库初始化完成！")
    print("=" * 50)


if __name__ == "__main__":
    main()
