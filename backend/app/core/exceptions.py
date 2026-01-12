"""
自定义异常模块
定义业务异常和错误码
"""
from typing import Optional, Dict, Any


class BusinessException(Exception):
    """业务异常基类"""
    
    def __init__(
        self,
        code: str,
        message: str,
        detail: Optional[Dict[str, Any]] = None,
        status_code: int = 400
    ):
        self.code = code
        self.message = message
        self.detail = detail
        self.status_code = status_code
        super().__init__(message)


# ========== 认证相关异常 ==========

class AuthenticationError(BusinessException):
    """认证错误"""
    def __init__(self, message: str = "认证失败"):
        super().__init__(
            code="AUTH_ERROR",
            message=message,
            status_code=401
        )


class PermissionDeniedError(BusinessException):
    """权限不足"""
    def __init__(self, permission: str = None):
        message = f"需要权限: {permission}" if permission else "权限不足"
        super().__init__(
            code="PERMISSION_DENIED",
            message=message,
            detail={"required_permission": permission} if permission else None,
            status_code=403
        )


class AccountLockedError(BusinessException):
    """账号锁定"""
    def __init__(self, unlock_time: str = None):
        super().__init__(
            code="ACCOUNT_LOCKED",
            message="账号已被锁定",
            detail={"unlock_time": unlock_time} if unlock_time else None,
            status_code=403
        )


# ========== 数据相关异常 ==========

class NotFoundError(BusinessException):
    """资源不存在"""
    def __init__(self, resource: str, resource_id: Any = None):
        message = f"{resource}不存在"
        super().__init__(
            code="NOT_FOUND",
            message=message,
            detail={"resource": resource, "id": resource_id},
            status_code=404
        )


class DuplicateError(BusinessException):
    """重复数据"""
    def __init__(self, resource: str, field: str = None):
        message = f"{resource}已存在"
        if field:
            message = f"{resource}的{field}已存在"
        super().__init__(
            code="DUPLICATE",
            message=message,
            detail={"resource": resource, "field": field},
            status_code=400
        )


class ReferenceExistsError(BusinessException):
    """存在关联数据"""
    def __init__(self, resource: str, references: Dict[str, int]):
        message = f"{resource}存在关联数据，无法删除"
        super().__init__(
            code="REF_EXISTS",
            message=message,
            detail={"references": references},
            status_code=400
        )


# ========== 报名相关异常 ==========

class RegistrationDuplicateError(BusinessException):
    """重复报名"""
    def __init__(self, student_name: str = None, event_name: str = None):
        message = "该学生已报名此项目"
        super().__init__(
            code="REG_DUPLICATE",
            message=message,
            detail={"student": student_name, "event": event_name},
            status_code=400
        )


class RegistrationLimitExceededError(BusinessException):
    """报名超限"""
    def __init__(self, limit_type: str, current: int, limit: int):
        if limit_type == "class":
            message = f"该班级报名人数已达上限({limit}人)"
        else:
            message = f"该学生报名项目数已达上限({limit}项)"
        super().__init__(
            code="REG_LIMIT_EXCEEDED",
            message=message,
            detail={"limit_type": limit_type, "current": current, "limit": limit},
            status_code=400
        )


# ========== 成绩相关异常 ==========

class ScoreDuplicateError(BusinessException):
    """成绩重复"""
    def __init__(self, existing_score_id: int = None):
        super().__init__(
            code="SCORE_DUPLICATE",
            message="该轮次已有成绩记录",
            detail={"existing_score_id": existing_score_id},
            status_code=400
        )


class ScoreInvalidError(BusinessException):
    """成绩无效"""
    def __init__(self, reason: str):
        super().__init__(
            code="SCORE_INVALID",
            message=f"成绩无效: {reason}",
            status_code=400
        )


# ========== 文件相关异常 ==========

class FileParseError(BusinessException):
    """文件解析错误"""
    def __init__(self, row: int = None, detail: str = None):
        message = "文件解析错误"
        if row:
            message = f"第{row}行解析错误"
        if detail:
            message = f"{message}: {detail}"
        super().__init__(
            code="FILE_PARSE_ERROR",
            message=message,
            detail={"row": row, "error": detail},
            status_code=400
        )


class FileTypeError(BusinessException):
    """文件类型错误"""
    def __init__(self, allowed_types: list = None):
        message = "不支持的文件类型"
        super().__init__(
            code="FILE_TYPE_ERROR",
            message=message,
            detail={"allowed_types": allowed_types},
            status_code=400
        )


# ========== 系统异常 ==========

class SystemError(BusinessException):
    """系统错误"""
    def __init__(self, message: str = "系统异常，请联系管理员"):
        super().__init__(
            code="SYSTEM_ERROR",
            message=message,
            status_code=500
        )


class DatabaseError(BusinessException):
    """数据库错误"""
    def __init__(self, message: str = "数据库操作失败"):
        super().__init__(
            code="DB_ERROR",
            message=message,
            status_code=500
        )
