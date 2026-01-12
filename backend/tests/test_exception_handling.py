"""
异常处理属性测试模块
Property 25: 异常处理日志记录
验证: 需求 11.7
"""
import pytest
from hypothesis import given, strategies as st, settings

from app.core.exceptions import (
    BusinessException,
    AuthenticationError,
    PermissionDeniedError,
    AccountLockedError,
    NotFoundError,
    DuplicateError,
    ReferenceExistsError,
    RegistrationDuplicateError,
    RegistrationLimitExceededError,
    ScoreDuplicateError,
    ScoreInvalidError,
    FileParseError,
    FileTypeError,
    SystemError,
    DatabaseError
)


# Feature: sports-meeting-teacher-system, Property 25: 异常处理日志记录
# Validates: Requirements 11.7

class TestExceptionHandling:
    """
    Property 25: 异常处理日志记录
    
    对于任意系统异常，必须记录错误日志并向用户返回友好的错误提示。
    """
    
    @given(
        code=st.text(min_size=1, max_size=50, alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ_"),
        message=st.text(min_size=1, max_size=200),
        status_code=st.sampled_from([400, 401, 403, 404, 500])
    )
    @settings(max_examples=100)
    def test_business_exception_has_required_fields(
        self,
        code: str,
        message: str,
        status_code: int
    ):
        """
        测试业务异常包含所有必需字段
        
        对于任意业务异常，必须包含：
        - code: 错误码
        - message: 错误消息
        - status_code: HTTP状态码
        """
        exc = BusinessException(
            code=code,
            message=message,
            status_code=status_code
        )
        
        assert exc.code == code, "错误码必须被正确设置"
        assert exc.message == message, "错误消息必须被正确设置"
        assert exc.status_code == status_code, "HTTP状态码必须被正确设置"
    
    @given(
        detail=st.dictionaries(
            keys=st.text(min_size=1, max_size=20, alphabet="abcdefghijklmnopqrstuvwxyz_"),
            values=st.one_of(
                st.text(max_size=100),
                st.integers(),
                st.booleans(),
                st.none()
            ),
            min_size=0,
            max_size=5
        )
    )
    @settings(max_examples=100)
    def test_exception_detail_preserved(self, detail: dict):
        """
        测试异常详情被完整保留
        
        对于任意异常详情，系统必须完整保留所有信息。
        """
        exc = BusinessException(
            code="TEST",
            message="Test message",
            detail=detail
        )
        
        assert exc.detail == detail, "异常详情必须被完整保留"
    
    @given(
        message=st.text(min_size=1, max_size=100)
    )
    @settings(max_examples=100)
    def test_authentication_error_returns_401(self, message: str):
        """
        测试认证错误返回401状态码
        
        对于任意认证错误，必须返回401状态码。
        """
        exc = AuthenticationError(message)
        
        assert exc.status_code == 401, "认证错误必须返回401状态码"
        assert exc.code == "AUTH_ERROR", "认证错误码必须是AUTH_ERROR"
    
    @given(
        permission=st.text(min_size=1, max_size=50, alphabet="abcdefghijklmnopqrstuvwxyz_")
    )
    @settings(max_examples=100)
    def test_permission_denied_returns_403(self, permission: str):
        """
        测试权限不足错误返回403状态码
        
        对于任意权限不足错误，必须返回403状态码。
        """
        exc = PermissionDeniedError(permission)
        
        assert exc.status_code == 403, "权限不足错误必须返回403状态码"
        assert exc.code == "PERMISSION_DENIED", "权限不足错误码必须是PERMISSION_DENIED"
        assert permission in exc.message, "错误消息必须包含所需权限"
    
    @given(
        resource=st.sampled_from(["用户", "学生", "成绩", "项目", "报名", "公示"]),
        resource_id=st.integers(min_value=1, max_value=10000)
    )
    @settings(max_examples=100)
    def test_not_found_error_returns_404(self, resource: str, resource_id: int):
        """
        测试资源不存在错误返回404状态码
        
        对于任意资源不存在错误，必须返回404状态码。
        """
        exc = NotFoundError(resource, resource_id)
        
        assert exc.status_code == 404, "资源不存在错误必须返回404状态码"
        assert exc.code == "NOT_FOUND", "资源不存在错误码必须是NOT_FOUND"
        assert resource in exc.message, "错误消息必须包含资源名称"
    
    @given(
        resource=st.sampled_from(["用户", "学生", "项目"]),
        field=st.sampled_from(["用户名", "学号", "名称"])
    )
    @settings(max_examples=100)
    def test_duplicate_error_returns_400(self, resource: str, field: str):
        """
        测试重复数据错误返回400状态码
        
        对于任意重复数据错误，必须返回400状态码。
        """
        exc = DuplicateError(resource, field)
        
        assert exc.status_code == 400, "重复数据错误必须返回400状态码"
        assert exc.code == "DUPLICATE", "重复数据错误码必须是DUPLICATE"
    
    @given(
        current=st.integers(min_value=0, max_value=100),
        limit=st.integers(min_value=1, max_value=100)
    )
    @settings(max_examples=100)
    def test_registration_limit_error_contains_limit_info(self, current: int, limit: int):
        """
        测试报名超限错误包含限制信息
        
        对于任意报名超限错误，必须包含当前数量和限制数量。
        """
        exc = RegistrationLimitExceededError("class", current, limit)
        
        assert exc.status_code == 400, "报名超限错误必须返回400状态码"
        assert exc.code == "REG_LIMIT_EXCEEDED", "报名超限错误码必须是REG_LIMIT_EXCEEDED"
        assert exc.detail["current"] == current, "必须包含当前数量"
        assert exc.detail["limit"] == limit, "必须包含限制数量"


class TestExceptionMessages:
    """
    测试异常消息的友好性
    """
    
    @given(
        exception_type=st.sampled_from([
            AuthenticationError,
            AccountLockedError,
            RegistrationDuplicateError,
            ScoreDuplicateError,
            SystemError,
            DatabaseError
        ])
    )
    @settings(max_examples=100)
    def test_default_messages_are_user_friendly(self, exception_type):
        """
        测试默认错误消息对用户友好
        
        对于任意异常类型，默认消息必须是用户可理解的中文。
        """
        exc = exception_type()
        
        # 消息不应该包含技术术语或堆栈信息
        assert "Exception" not in exc.message, "错误消息不应包含Exception"
        assert "Error" not in exc.message or exc.message.endswith("Error"), "错误消息不应包含Error（除非是类名）"
        assert "Traceback" not in exc.message, "错误消息不应包含Traceback"
        assert len(exc.message) > 0, "错误消息不应为空"
    
    @given(
        row=st.integers(min_value=1, max_value=10000),
        detail=st.text(min_size=1, max_size=100)
    )
    @settings(max_examples=100)
    def test_file_parse_error_includes_row_number(self, row: int, detail: str):
        """
        测试文件解析错误包含行号
        
        对于任意文件解析错误，如果指定了行号，消息必须包含行号信息。
        """
        exc = FileParseError(row=row, detail=detail)
        
        assert str(row) in exc.message, "错误消息必须包含行号"
        assert exc.detail["row"] == row, "详情必须包含行号"
    
    @given(
        allowed_types=st.lists(
            st.sampled_from([".xlsx", ".xls", ".csv", ".pdf"]),
            min_size=1,
            max_size=4,
            unique=True
        )
    )
    @settings(max_examples=100)
    def test_file_type_error_includes_allowed_types(self, allowed_types: list):
        """
        测试文件类型错误包含允许的类型
        
        对于任意文件类型错误，详情必须包含允许的文件类型列表。
        """
        exc = FileTypeError(allowed_types=allowed_types)
        
        assert exc.detail["allowed_types"] == allowed_types, "详情必须包含允许的文件类型"


class TestExceptionInheritance:
    """
    测试异常继承关系
    """
    
    @given(
        exception_class=st.sampled_from([
            AuthenticationError,
            PermissionDeniedError,
            AccountLockedError,
            NotFoundError,
            DuplicateError,
            ReferenceExistsError,
            RegistrationDuplicateError,
            RegistrationLimitExceededError,
            ScoreDuplicateError,
            ScoreInvalidError,
            FileParseError,
            FileTypeError,
            SystemError,
            DatabaseError
        ])
    )
    @settings(max_examples=100)
    def test_all_exceptions_inherit_from_business_exception(self, exception_class):
        """
        测试所有自定义异常继承自BusinessException
        
        对于任意自定义异常类，必须继承自BusinessException。
        """
        assert issubclass(exception_class, BusinessException), \
            f"{exception_class.__name__}必须继承自BusinessException"
    
    @given(
        exception_class=st.sampled_from([
            AuthenticationError,
            PermissionDeniedError,
            AccountLockedError,
            NotFoundError,
            DuplicateError,
            ReferenceExistsError,
            RegistrationDuplicateError,
            RegistrationLimitExceededError,
            ScoreDuplicateError,
            ScoreInvalidError,
            FileParseError,
            FileTypeError,
            SystemError,
            DatabaseError
        ])
    )
    @settings(max_examples=100)
    def test_all_exceptions_are_catchable_as_exception(self, exception_class):
        """
        测试所有自定义异常可以被Exception捕获
        
        对于任意自定义异常类，必须可以被标准Exception捕获。
        """
        assert issubclass(exception_class, Exception), \
            f"{exception_class.__name__}必须继承自Exception"
