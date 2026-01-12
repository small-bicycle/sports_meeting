"""
操作日志API路由模块
"""
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_admin_user
from app.models.user import User
from app.models.log import OperationLog

router = APIRouter(prefix="/logs", tags=["操作日志"])


@router.get("", summary="获取操作日志列表")
async def get_logs(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    user_id: int = Query(None, description="按操作人筛选"),
    action: str = Query(None, description="按操作类型筛选"),
    target_type: str = Query(None, description="按目标类型筛选"),
    start_date: datetime = Query(None, description="开始时间"),
    end_date: datetime = Query(None, description="结束时间"),
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    获取操作日志列表（需要管理员权限）
    
    支持多条件筛选：
    - **user_id**: 按操作人筛选
    - **action**: 按操作类型筛选（create/update/delete/login等）
    - **target_type**: 按目标类型筛选（user/student/score等）
    - **start_date**: 开始时间
    - **end_date**: 结束时间
    """
    query = db.query(OperationLog)
    
    if user_id:
        query = query.filter(OperationLog.user_id == user_id)
    if action:
        query = query.filter(OperationLog.action == action)
    if target_type:
        query = query.filter(OperationLog.target_type == target_type)
    if start_date:
        query = query.filter(OperationLog.created_at >= start_date)
    if end_date:
        query = query.filter(OperationLog.created_at <= end_date)
    
    # 按时间倒序
    query = query.order_by(OperationLog.created_at.desc())
    
    total = query.count()
    logs = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "items": [
            {
                "id": log.id,
                "user_id": log.user_id,
                "action": log.action,
                "target_type": log.target_type,
                "target_id": log.target_id,
                "detail": log.detail,
                "ip_address": log.ip_address,
                "created_at": log.created_at.isoformat() if log.created_at else None
            } for log in logs
        ],
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/actions", summary="获取操作类型列表")
async def get_action_types(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    获取所有操作类型（用于筛选）
    """
    actions = db.query(OperationLog.action).distinct().all()
    return {"actions": [a[0] for a in actions]}


@router.get("/target-types", summary="获取目标类型列表")
async def get_target_types(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    获取所有目标类型（用于筛选）
    """
    types = db.query(OperationLog.target_type).distinct().all()
    return {"target_types": [t[0] for t in types]}
