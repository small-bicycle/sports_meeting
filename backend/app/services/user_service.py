"""
用户管理服务模块
实现创建账号、分配权限、启用/禁用账号等功能
"""
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session

from app.models.user import User
from app.core.security import get_password_hash, generate_initial_password


class UserService:
    """用户管理服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(
        self, 
        username: str, 
        name: str, 
        permissions: List[str] = None,
        is_admin: bool = False
    ) -> Tuple[Optional[User], str, str]:
        """
        创建新用户
        返回: (用户对象, 初始密码, 错误信息)
        """
        # 检查用户名是否已存在
        existing = self.db.query(User).filter(User.username == username).first()
        if existing:
            return None, "", "用户名已存在"
        
        # 生成初始密码
        initial_password = generate_initial_password()
        
        user = User(
            username=username,
            password_hash=get_password_hash(initial_password),
            name=name,
            permissions=permissions or [],
            is_admin=is_admin,
            is_active=True
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user, initial_password, ""
    
    def update_user(
        self,
        user_id: int,
        name: str = None,
        permissions: List[str] = None,
        is_active: bool = None
    ) -> Tuple[Optional[User], str]:
        """
        更新用户信息
        返回: (用户对象, 错误信息)
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None, "用户不存在"
        
        if name is not None:
            user.name = name
        if permissions is not None:
            user.permissions = permissions
        if is_active is not None:
            user.is_active = is_active
        
        self.db.commit()
        self.db.refresh(user)
        
        return user, ""
    
    def delete_user(self, user_id: int) -> Tuple[bool, str]:
        """
        删除用户
        返回: (是否成功, 错误信息)
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False, "用户不存在"
        
        if user.is_admin:
            # 检查是否是最后一个管理员
            admin_count = self.db.query(User).filter(User.is_admin == True).count()
            if admin_count <= 1:
                return False, "不能删除最后一个管理员账号"
        
        self.db.delete(user)
        self.db.commit()
        
        return True, ""
    
    def get_user_list(
        self,
        page: int = 1,
        page_size: int = 20,
        keyword: str = None
    ) -> Tuple[List[User], int]:
        """
        获取用户列表
        返回: (用户列表, 总数)
        """
        query = self.db.query(User)
        
        if keyword:
            query = query.filter(
                (User.username.contains(keyword)) | 
                (User.name.contains(keyword))
            )
        
        total = query.count()
        users = query.offset((page - 1) * page_size).limit(page_size).all()
        
        return users, total
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def reset_password(self, user_id: int) -> Tuple[str, str]:
        """
        重置用户密码
        返回: (新密码, 错误信息)
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return "", "用户不存在"
        
        new_password = generate_initial_password()
        user.set_password(new_password)
        user.reset_login_failures()  # 同时解锁账号
        self.db.commit()
        
        return new_password, ""
