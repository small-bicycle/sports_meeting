"""
认证服务属性测试
Feature: sports-meeting-teacher-system
Property 2: 权限访问控制
Property 3: 密码修改验证
Validates: Requirements 1.2, 1.3, 1.4
"""
import pytest
from hypothesis import given, strategies as st, settings as hyp_settings

from app.models.user import User
from app.services.auth_service import AuthService
from app.core.security import get_password_hash


class TestAuthServiceProperties:
    """认证服务属性测试类"""
    
    @given(
        password=st.text(min_size=6, max_size=20, alphabet=st.characters(whitelist_categories=('L', 'N')))
    )
    @hyp_settings(max_examples=100)
    def test_password_change_requires_correct_old_password(self, db_session, password):
        """
        Property 3: 密码修改验证
        对于任意密码修改请求，只有当提供的原密码与当前密码匹配时，修改才能成功。
        Validates: Requirements 1.4
        """
        # 清理数据
        db_session.query(User).delete()
        db_session.commit()
        
        # 创建用户
        user = User(
            username="testuser",
            password_hash=get_password_hash(password),
            name="测试用户"
        )
        db_session.add(user)
        db_session.commit()
        
        auth_service = AuthService(db_session)
        
        # 使用错误的原密码应该失败
        success, msg = auth_service.change_password(user, "wrong_password", "new_password123")
        assert success is False
        assert "原密码错误" in msg
        
        # 使用正确的原密码应该成功
        success, msg = auth_service.change_password(user, password, "new_password123")
        assert success is True
        
        # 验证新密码生效
        assert user.verify_password("new_password123") is True
        assert user.verify_password(password) is False
    
    def test_permission_access_control(self, db_session):
        """
        Property 2: 权限访问控制
        对于任意已登录的教师用户和任意功能模块，用户只能访问其权限列表中包含的功能模块。
        Validates: Requirements 1.2, 1.3
        """
        # 创建有特定权限的用户
        user = User(
            username="teacher1",
            password_hash=get_password_hash("password123"),
            name="教师1",
            permissions=["score_manage", "registration_manage"],
            is_admin=False
        )
        db_session.add(user)
        db_session.commit()
        
        # 验证权限检查
        assert user.has_permission("score_manage") is True
        assert user.has_permission("registration_manage") is True
        assert user.has_permission("user_manage") is False
        assert user.has_permission("export_data") is False
    
    def test_admin_has_all_permissions(self, db_session):
        """测试管理员拥有所有权限"""
        admin = User(
            username="admin",
            password_hash=get_password_hash("admin123"),
            name="管理员",
            is_admin=True
        )
        db_session.add(admin)
        db_session.commit()
        
        # 管理员应该拥有所有权限
        assert admin.has_permission("score_manage") is True
        assert admin.has_permission("user_manage") is True
        assert admin.has_permission("any_permission") is True
    
    def test_login_failure_lockout(self, db_session):
        """测试登录失败锁定机制"""
        user = User(
            username="locktest",
            password_hash=get_password_hash("correct_password"),
            name="锁定测试"
        )
        db_session.add(user)
        db_session.commit()
        
        auth_service = AuthService(db_session)
        
        # 连续5次错误登录
        for i in range(5):
            result, error = auth_service.authenticate("locktest", "wrong_password")
            assert result is None
        
        # 第6次即使密码正确也应该被锁定
        result, error = auth_service.authenticate("locktest", "correct_password")
        assert result is None
        assert "锁定" in error
    
    def test_successful_login_resets_failure_count(self, db_session):
        """测试成功登录重置失败计数"""
        user = User(
            username="resettest",
            password_hash=get_password_hash("correct_password"),
            name="重置测试"
        )
        db_session.add(user)
        db_session.commit()
        
        auth_service = AuthService(db_session)
        
        # 先失败几次
        for i in range(3):
            auth_service.authenticate("resettest", "wrong_password")
        
        assert user.login_fail_count == 3
        
        # 成功登录
        result, error = auth_service.authenticate("resettest", "correct_password")
        assert result is not None
        assert user.login_fail_count == 0
