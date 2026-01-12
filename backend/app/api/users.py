"""
用户管理API路由模块
实现教师账号的CRUD操作
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.user_service import UserService
from app.services.auth_service import AuthService
from app.api.deps import get_admin_user
from app.models.user import User
from app.schemas import (
    UserInfo,
    UserCreate,
    UserCreateResponse,
    UserUpdate,
    ResponseBase,
    PaginatedResponse
)

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.get("", summary="获取教师列表")
async def get_users(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    keyword: str = Query(None, description="搜索关键词（用户名或姓名）"),
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    获取教师列表（需要管理员权限）
    
    - **page**: 页码，从1开始
    - **page_size**: 每页数量，最大100
    - **keyword**: 搜索关键词，可搜索用户名或姓名
    """
    user_service = UserService(db)
    users, total = user_service.get_user_list(
        page=page,
        page_size=page_size,
        keyword=keyword
    )
    
    return {
        "items": [
            UserInfo(
                id=u.id,
                username=u.username,
                name=u.name,
                permissions=u.permissions or [],
                is_admin=u.is_admin,
                is_active=u.is_active
            ) for u in users
        ],
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.post("", response_model=UserCreateResponse, summary="创建教师账号")
async def create_user(
    request: UserCreate,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    创建教师账号（需要管理员权限）
    
    - **username**: 登录账号（唯一）
    - **name**: 教师姓名
    - **permissions**: 权限列表
    - **is_admin**: 是否管理员
    
    返回创建的账号信息和初始密码
    """
    user_service = UserService(db)
    user, initial_password, error = user_service.create_user(
        username=request.username,
        name=request.name,
        permissions=request.permissions,
        is_admin=request.is_admin
    )
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return UserCreateResponse(
        id=user.id,
        username=user.username,
        initial_password=initial_password
    )


@router.get("/{user_id}", response_model=UserInfo, summary="获取教师详情")
async def get_user(
    user_id: int,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    获取教师详情（需要管理员权限）
    """
    user_service = UserService(db)
    user = user_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return UserInfo(
        id=user.id,
        username=user.username,
        name=user.name,
        permissions=user.permissions or [],
        is_admin=user.is_admin,
        is_active=user.is_active
    )


@router.put("/{user_id}", response_model=UserInfo, summary="更新教师信息")
async def update_user(
    user_id: int,
    request: UserUpdate,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    更新教师信息（需要管理员权限）
    
    - **name**: 教师姓名
    - **permissions**: 权限列表
    - **is_active**: 是否启用
    """
    user_service = UserService(db)
    user, error = user_service.update_user(
        user_id=user_id,
        name=request.name,
        permissions=request.permissions,
        is_active=request.is_active
    )
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return UserInfo(
        id=user.id,
        username=user.username,
        name=user.name,
        permissions=user.permissions or [],
        is_admin=user.is_admin,
        is_active=user.is_active
    )


@router.delete("/{user_id}", response_model=ResponseBase, summary="删除教师账号")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    删除教师账号（需要管理员权限）
    
    注意：不能删除最后一个管理员账号
    """
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己的账号"
        )
    
    user_service = UserService(db)
    success, error = user_service.delete_user(user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return ResponseBase(message="删除成功")


@router.post("/{user_id}/reset-password", summary="重置教师密码")
async def reset_password(
    user_id: int,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    重置教师密码（需要管理员权限）
    
    返回新的初始密码
    """
    user_service = UserService(db)
    new_password, error = user_service.reset_password(user_id)
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return {"new_password": new_password}


@router.post("/{user_id}/unlock", response_model=ResponseBase, summary="解锁教师账号")
async def unlock_user(
    user_id: int,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    解锁教师账号（需要管理员权限）
    
    用于解锁因登录失败次数过多而被锁定的账号
    """
    auth_service = AuthService(db)
    success, message = auth_service.unlock_account(user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return ResponseBase(message=message)
