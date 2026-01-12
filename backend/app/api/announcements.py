"""
公示管理API路由模块
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.announcement_service import AnnouncementService
from app.api.deps import get_current_user, require_permission
from app.models.user import User
from app.schemas import (
    AnnouncementInfo,
    AnnouncementCreate,
    AnnouncementCreateResponse,
    ResponseBase
)

router = APIRouter(prefix="/announcements", tags=["公示管理"])


@router.get("", summary="获取公示列表")
async def get_announcements(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    include_closed: bool = Query(False, description="是否包含已关闭的公示"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取公示列表
    
    - **include_closed**: 是否包含已关闭的公示
    """
    announcement_service = AnnouncementService(db)
    announcements, total = announcement_service.get_announcement_list(
        page=page,
        page_size=page_size,
        include_closed=include_closed
    )
    
    return {
        "items": [
            AnnouncementInfo(
                id=a.id,
                title=a.title,
                share_code=a.share_code,
                content_type=a.content_type,
                event_ids=a.event_ids or [],
                is_active=a.is_active,
                created_at=a.created_at,
                closed_at=a.closed_at
            ) for a in announcements
        ],
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.post("", response_model=AnnouncementCreateResponse, summary="创建公示")
async def create_announcement(
    request: AnnouncementCreate,
    req: Request,
    current_user: User = Depends(require_permission("announcement_manage")),
    db: Session = Depends(get_db)
):
    """
    创建公示
    
    - **title**: 公示标题
    - **content_type**: 内容类型
      - event: 项目排名
      - class: 班级总分
      - grade: 年级奖牌
    - **event_ids**: 包含的项目ID列表（content_type=event时使用）
    
    返回分享链接和分享码
    """
    announcement_service = AnnouncementService(db)
    announcement, error = announcement_service.create_announcement(
        title=request.title,
        content_type=request.content_type,
        event_ids=request.event_ids,
        created_by=current_user.id
    )
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    # 构建分享URL
    base_url = str(req.base_url).rstrip('/')
    share_url = announcement_service.get_share_url(announcement.id, base_url)
    
    return AnnouncementCreateResponse(
        id=announcement.id,
        share_url=share_url,
        share_code=announcement.share_code
    )


@router.get("/{announcement_id}", response_model=AnnouncementInfo, summary="获取公示详情")
async def get_announcement(
    announcement_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取公示详情
    """
    from app.models.announcement import Announcement
    announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    
    if not announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="公示不存在"
        )
    
    return AnnouncementInfo(
        id=announcement.id,
        title=announcement.title,
        share_code=announcement.share_code,
        content_type=announcement.content_type,
        event_ids=announcement.event_ids or [],
        is_active=announcement.is_active,
        created_at=announcement.created_at,
        closed_at=announcement.closed_at
    )


@router.get("/{announcement_id}/share-url", summary="获取分享链接")
async def get_share_url(
    announcement_id: int,
    req: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取公示的分享链接
    """
    announcement_service = AnnouncementService(db)
    base_url = str(req.base_url).rstrip('/')
    share_url = announcement_service.get_share_url(announcement_id, base_url)
    
    if not share_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="公示不存在"
        )
    
    return {"share_url": share_url}


@router.put("/{announcement_id}/close", response_model=ResponseBase, summary="关闭公示")
async def close_announcement(
    announcement_id: int,
    current_user: User = Depends(require_permission("announcement_manage")),
    db: Session = Depends(get_db)
):
    """
    关闭公示
    
    关闭后公示链接将失效
    """
    announcement_service = AnnouncementService(db)
    success, error = announcement_service.close_announcement(announcement_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return ResponseBase(message="公示已关闭")


@router.put("/{announcement_id}/reopen", response_model=ResponseBase, summary="重新开启公示")
async def reopen_announcement(
    announcement_id: int,
    current_user: User = Depends(require_permission("announcement_manage")),
    db: Session = Depends(get_db)
):
    """
    重新开启已关闭的公示
    """
    announcement_service = AnnouncementService(db)
    success, error = announcement_service.reopen_announcement(announcement_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return ResponseBase(message="公示已重新开启")


@router.delete("/{announcement_id}", response_model=ResponseBase, summary="删除公示")
async def delete_announcement(
    announcement_id: int,
    current_user: User = Depends(require_permission("announcement_manage")),
    db: Session = Depends(get_db)
):
    """
    删除公示
    """
    announcement_service = AnnouncementService(db)
    success, error = announcement_service.delete_announcement(announcement_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return ResponseBase(message="删除成功")
