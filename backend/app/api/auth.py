"""
认证API路由模块
实现登录、登出、修改密码等接口
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.auth_service import AuthService
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas import (
    LoginRequest,
    LoginResponse,
    PasswordChangeRequest,
    ResponseBase,
    UserInfo
)

router = APIRouter(prefix="/auth", tags=["认证管理"])


@router.post("/login", response_model=LoginResponse, summary="教师登录")
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    教师登录接口
    
    - **username**: 登录账号
    - **password**: 登录密码
    
    返回JWT访问令牌和用户信息
    """
    auth_service = AuthService(db)
    user, error = auth_service.authenticate(request.username, request.password)
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error
        )
    
    token = auth_service.create_token(user)
    
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        user=UserInfo(
            id=user.id,
            username=user.username,
            name=user.name,
            permissions=user.permissions or [],
            is_admin=user.is_admin,
            is_active=user.is_active
        )
    )


@router.post("/logout", response_model=ResponseBase, summary="退出登录")
async def logout(
    current_user: User = Depends(get_current_user)
):
    """
    退出登录接口
    
    客户端应在调用此接口后清除本地存储的令牌
    """
    # JWT是无状态的，服务端不需要做特殊处理
    # 客户端需要清除本地存储的token
    return ResponseBase(message="登出成功")


@router.put("/password", response_model=ResponseBase, summary="修改密码")
async def change_password(
    request: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    修改密码接口
    
    - **old_password**: 原密码
    - **new_password**: 新密码（至少6位）
    """
    auth_service = AuthService(db)
    success, message = auth_service.change_password(
        user=current_user,
        old_password=request.old_password,
        new_password=request.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return ResponseBase(message=message)


@router.get("/me", response_model=UserInfo, summary="获取当前用户信息")
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    获取当前登录用户信息
    """
    return UserInfo(
        id=current_user.id,
        username=current_user.username,
        name=current_user.name,
        permissions=current_user.permissions or [],
        is_admin=current_user.is_admin,
        is_active=current_user.is_active
    )
