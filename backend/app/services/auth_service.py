"""
认证服务模块
实现登录验证、JWT生成、密码修改、账号锁定逻辑
"""
from datetime import timedelta
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from app.models.user import User
from app.core.security import create_access_token, verify_password, get_password_hash
from app.core.config import settings


class AuthService:
    """认证服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def authenticate(self, username: str, password: str) -> Tuple[Optional[User], Optional[str]]:
        """
        验证用户登录
        返回: (用户对象, 错误信息)
        """
        user = self.db.query(User).filter(User.username == username).first()
        
        if not user:
            return None, "账号或密码错误"
        
        if not user.is_active:
            return None, "账号已被禁用，请联系管理员"
        
        if user.is_locked():
            return None, f"账号已被锁定，请{settings.ACCOUNT_LOCK_MINUTES}分钟后重试或联系管理员"
        
        if not user.verify_password(password):
            # 记录登录失败
            locked = user.record_login_failure()
            self.db.commit()
            
            if locked:
                return None, f"登录失败次数过多，账号已被锁定{settings.ACCOUNT_LOCK_MINUTES}分钟"
            
            remaining = settings.LOGIN_FAIL_LIMIT - user.login_fail_count
            return None, f"账号或密码错误，还剩{remaining}次尝试机会"
        
        # 登录成功，重置失败计数
        user.reset_login_failures()
        self.db.commit()
        
        return user, None
    
    def create_token(self, user: User) -> str:
        """为用户创建访问令牌"""
        token_data = {
            "sub": str(user.id),
            "username": user.username,
            "is_admin": user.is_admin
        }
        return create_access_token(
            data=token_data,
            expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        )
    
    def change_password(self, user: User, old_password: str, new_password: str) -> Tuple[bool, str]:
        """
        修改密码
        返回: (是否成功, 消息)
        """
        if not user.verify_password(old_password):
            return False, "原密码错误"
        
        if len(new_password) < 6:
            return False, "新密码长度不能少于6位"
        
        if old_password == new_password:
            return False, "新密码不能与原密码相同"
        
        user.set_password(new_password)
        self.db.commit()
        
        return True, "密码修改成功"
    
    def unlock_account(self, user_id: int) -> Tuple[bool, str]:
        """解锁账号（管理员操作）"""
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return False, "用户不存在"
        
        user.reset_login_failures()
        self.db.commit()
        
        return True, "账号已解锁"
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        return self.db.query(User).filter(User.id == user_id).first()
