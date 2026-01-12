"""
中间件模块
包含操作日志记录、异常处理等中间件
"""
import json
import traceback
from typing import Callable, Optional
from datetime import datetime
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import decode_access_token
from app.models.log import OperationLog


# 需要记录日志的操作
LOG_OPERATIONS = {
    # 用户管理
    ("POST", "/api/users"): ("create", "user"),
    ("PUT", "/api/users/"): ("update", "user"),
    ("DELETE", "/api/users/"): ("delete", "user"),
    ("POST", "/api/users/", "/reset-password"): ("reset_password", "user"),
    ("POST", "/api/users/", "/unlock"): ("unlock", "user"),
    
    # 年级管理
    ("POST", "/api/grades"): ("create", "grade"),
    ("PUT", "/api/grades/"): ("update", "grade"),
    ("DELETE", "/api/grades/"): ("delete", "grade"),
    
    # 班级管理
    ("POST", "/api/classes"): ("create", "class"),
    ("PUT", "/api/classes/"): ("update", "class"),
    ("DELETE", "/api/classes/"): ("delete", "class"),
    
    # 学生管理
    ("POST", "/api/students"): ("create", "student"),
    ("PUT", "/api/students/"): ("update", "student"),
    ("DELETE", "/api/students/"): ("delete", "student"),
    ("POST", "/api/students/import"): ("import", "student"),
    
    # 项目管理
    ("POST", "/api/events"): ("create", "event"),
    ("PUT", "/api/events/"): ("update", "event"),
    ("DELETE", "/api/events/"): ("delete", "event"),
    ("POST", "/api/events/", "/groups"): ("create", "event_group"),
    ("PUT", "/api/events/groups/"): ("update", "event_group"),
    ("DELETE", "/api/events/groups/"): ("delete", "event_group"),
    
    # 报名管理
    ("POST", "/api/registrations"): ("create", "registration"),
    ("DELETE", "/api/registrations/"): ("delete", "registration"),
    ("POST", "/api/registrations/import"): ("import", "registration"),
    
    # 成绩管理
    ("POST", "/api/scores"): ("create", "score"),
    ("PUT", "/api/scores/"): ("update", "score"),
    ("PUT", "/api/scores/", "/invalidate"): ("invalidate", "score"),
    ("POST", "/api/scores/import"): ("import", "score"),
    
    # 公示管理
    ("POST", "/api/announcements"): ("create", "announcement"),
    ("PUT", "/api/announcements/", "/close"): ("close", "announcement"),
    ("PUT", "/api/announcements/", "/reopen"): ("reopen", "announcement"),
    ("DELETE", "/api/announcements/"): ("delete", "announcement"),
    
    # 统计管理
    ("PUT", "/api/statistics/scoring-rules"): ("update", "scoring_rules"),
    ("POST", "/api/statistics/recalculate"): ("recalculate", "rankings"),
    
    # 认证
    ("POST", "/api/auth/login"): ("login", "auth"),
    ("POST", "/api/auth/logout"): ("logout", "auth"),
    ("PUT", "/api/auth/password"): ("change_password", "auth"),
}


def get_operation_info(method: str, path: str) -> Optional[tuple]:
    """
    根据请求方法和路径获取操作信息
    返回: (action, target_type) 或 None
    """
    # 精确匹配
    key = (method, path)
    if key in LOG_OPERATIONS:
        return LOG_OPERATIONS[key]
    
    # 前缀匹配（处理带ID的路径）
    for key, info in LOG_OPERATIONS.items():
        if len(key) == 2:
            m, p = key
            if m == method:
                if isinstance(p, str) and path.startswith(p):
                    return info
        elif len(key) == 3:
            # 处理类似 /api/users/{id}/reset-password 的路径
            m, prefix, suffix = key
            if m == method and path.startswith(prefix) and path.endswith(suffix):
                return info
    
    return None


def extract_target_id(path: str) -> Optional[int]:
    """从路径中提取目标ID"""
    parts = path.split('/')
    for part in parts:
        if part.isdigit():
            return int(part)
    return None


def get_user_id_from_token(request: Request) -> Optional[int]:
    """从请求头中获取用户ID"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    token = auth_header[7:]
    payload = decode_access_token(token)
    if payload and "sub" in payload:
        return int(payload["sub"])
    return None


def get_client_ip(request: Request) -> str:
    """获取客户端IP"""
    # 尝试从X-Forwarded-For获取（代理情况）
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    # 直接获取客户端IP
    if request.client:
        return request.client.host
    
    return "unknown"


class OperationLogMiddleware(BaseHTTPMiddleware):
    """操作日志记录中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 获取操作信息
        method = request.method
        path = request.url.path
        
        operation_info = get_operation_info(method, path)
        
        # 如果不是需要记录的操作，直接执行
        if not operation_info:
            return await call_next(request)
        
        action, target_type = operation_info
        
        # 执行请求（不再预读取body，避免兼容性问题）
        response = await call_next(request)
        
        # 只记录成功的操作（2xx状态码）
        if 200 <= response.status_code < 300:
            try:
                # 获取用户ID
                user_id = get_user_id_from_token(request)
                
                # 获取目标ID
                target_id = extract_target_id(path)
                
                # 获取客户端IP
                ip_address = get_client_ip(request)
                
                # 构建详情（简化版，不记录请求体）
                detail = {
                    "method": method,
                    "path": path
                }
                
                # 记录日志
                db = SessionLocal()
                try:
                    log = OperationLog(
                        user_id=user_id,
                        action=action,
                        target_type=target_type,
                        target_id=target_id,
                        detail=detail,
                        ip_address=ip_address
                    )
                    db.add(log)
                    db.commit()
                finally:
                    db.close()
                    
            except Exception as e:
                # 日志记录失败不影响正常响应
                print(f"Failed to log operation: {e}")
        
        return response


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    """全局异常处理中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except Exception as e:
            # 记录错误日志
            error_detail = {
                "path": request.url.path,
                "method": request.method,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            
            # 记录到数据库
            try:
                user_id = get_user_id_from_token(request)
                ip_address = get_client_ip(request)
                
                db = SessionLocal()
                try:
                    log = OperationLog(
                        user_id=user_id,
                        action="error",
                        target_type="system",
                        target_id=None,
                        detail=error_detail,
                        ip_address=ip_address
                    )
                    db.add(log)
                    db.commit()
                finally:
                    db.close()
            except Exception:
                pass
            
            # 打印到控制台
            print(f"Unhandled exception: {e}")
            print(traceback.format_exc())
            
            # 返回友好的错误响应
            return JSONResponse(
                status_code=500,
                content={
                    "error": "系统异常，请联系管理员",
                    "detail": str(e) if request.app.debug else None
                }
            )
