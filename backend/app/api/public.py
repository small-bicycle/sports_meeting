"""
公开访问API路由模块
无需认证即可访问
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.announcement_service import AnnouncementService
from app.schemas import PublicAnnouncementResponse

router = APIRouter(prefix="/public", tags=["公开访问"])


@router.get("/announcement/{share_code}", response_model=PublicAnnouncementResponse, summary="访问公示页面")
async def get_public_announcement(
    share_code: str,
    db: Session = Depends(get_db)
):
    """
    通过分享码访问公示页面（无需登录）
    
    - **share_code**: 公示分享码
    
    返回公示内容，包括：
    - event类型：项目排名
    - class类型：班级总分
    - grade类型：年级奖牌
    """
    announcement_service = AnnouncementService(db)
    data, error = announcement_service.get_announcement_by_code(share_code)
    
    if error:
        if error == "公示已结束":
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="公示已结束"
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error
        )
    
    return PublicAnnouncementResponse(
        id=data["id"],
        title=data["title"],
        content_type=data["content_type"],
        content=data["content"],
        created_at=data["created_at"]
    )
