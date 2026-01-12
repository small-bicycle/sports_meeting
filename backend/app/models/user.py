"""
用户模型模块
"""
from datetime import datetime, timedelta
from sqlalchemy import Column, String, Boolean, Integer, DateTime, JSON
from app.models.base_model import BaseModel
from app.core.security import verify_password, get_password_hash
from app.core.config import settings


class User(BaseModel):
    """教师用户模型"""
    __tablename__ = "users"
    
    username = Column(String(50), unique=True, nullable=False, index=True, comment="登录账号")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    name = Column(String(50), nullable=False, comment="姓名")
    permissions = Column(JSON, default=list, comment="权限列表")
    is_admin = Column(Boolean, default=False, comment="是否管理员")
    is_active = Column(Boolean, default=True, comment="是否启用")
    login_fail_count = Column(Integer, default=0, comment="登录失败次数")
    locked_until = Column(DateTime, nullable=True, comment="锁定截止时间")
    
    def verify_password(self, password: str) -> bool:
        """验证密码"""
        return verify_password(password, self.password_hash)
    
    def set_password(self, password: str) -> None:
        """设置密码"""
        self.password_hash = get_password_hash(password)
    
    def is_locked(self) -> bool:
        """检查账号是否被锁定"""
        if self.locked_until is None:
            return False
        return datetime.utcnow() < self.locked_until
    
    def record_login_failure(self) -> bool:
        """记录登录失败，返回是否需要锁定"""
        self.login_fail_count += 1
        if self.login_fail_count >= settings.LOGIN_FAIL_LIMIT:
            self.locked_until = datetime.utcnow() + timedelta(minutes=settings.ACCOUNT_LOCK_MINUTES)
            return True
        return False
    
    def reset_login_failures(self) -> None:
        """重置登录失败计数"""
        self.login_fail_count = 0
        self.locked_until = None
    
    def has_permission(self, permission: str) -> bool:
        """检查是否有指定权限"""
        if self.is_admin:
            return True
        return permission in (self.permissions or [])
