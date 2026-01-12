"""
用户模型属性测试
Feature: sports-meeting-teacher-system, Property 1: 账号唯一性
Validates: Requirements 1.1
"""
import pytest
from hypothesis import given, strategies as st, settings as hyp_settings
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.core.security import get_password_hash


class TestUserModelProperties:
    """用户模型属性测试类"""
    
    @given(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'N'))))
    @hyp_settings(max_examples=100)
    def test_username_uniqueness_property(self, db_session, username):
        """
        Property 1: 账号唯一性
        对于任意创建的教师账号，系统中不应存在相同用户名的其他账号。
        Validates: Requirements 1.1
        """
        # 清理之前的数据
        db_session.query(User).delete()
        db_session.commit()
        
        # 创建第一个用户
        user1 = User(
            username=username,
            password_hash=get_password_hash("password123"),
            name="测试用户1"
        )
        db_session.add(user1)
        db_session.commit()
        
        # 尝试创建相同用户名的第二个用户应该失败
        user2 = User(
            username=username,
            password_hash=get_password_hash("password456"),
            name="测试用户2"
        )
        db_session.add(user2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
        
        db_session.rollback()
    
    def test_password_verification(self, db_session):
        """测试密码验证功能"""
        user = User(
            username="testuser",
            password_hash=get_password_hash("correct_password"),
            name="测试用户"
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.verify_password("correct_password") is True
        assert user.verify_password("wrong_password") is False
    
    def test_account_locking(self, db_session):
        """测试账号锁定功能"""
        user = User(
            username="locktest",
            password_hash=get_password_hash("password"),
            name="锁定测试"
        )
        db_session.add(user)
        db_session.commit()
        
        # 初始状态不应被锁定
        assert user.is_locked() is False
        
        # 连续失败5次后应被锁定
        for i in range(5):
            locked = user.record_login_failure()
            if i < 4:
                assert locked is False
            else:
                assert locked is True
        
        assert user.is_locked() is True
        
        # 重置后应解锁
        user.reset_login_failures()
        assert user.is_locked() is False
    
    def test_permission_check(self, db_session):
        """测试权限检查功能"""
        # 普通用户
        normal_user = User(
            username="normal",
            password_hash=get_password_hash("password"),
            name="普通用户",
            permissions=["score_manage", "registration_manage"],
            is_admin=False
        )
        
        # 管理员用户
        admin_user = User(
            username="admin",
            password_hash=get_password_hash("password"),
            name="管理员",
            is_admin=True
        )
        
        db_session.add_all([normal_user, admin_user])
        db_session.commit()
        
        # 普通用户只能访问分配的权限
        assert normal_user.has_permission("score_manage") is True
        assert normal_user.has_permission("user_manage") is False
        
        # 管理员可以访问所有权限
        assert admin_user.has_permission("score_manage") is True
        assert admin_user.has_permission("user_manage") is True
