"""
公示服务模块
实现公示创建、分享链接生成、公示关闭
"""
from typing import List, Optional, Tuple, Dict
from datetime import datetime
import secrets
from sqlalchemy.orm import Session

from app.models.announcement import Announcement
from app.services.statistics_service import StatisticsService


class AnnouncementService:
    """公示服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.stats_service = StatisticsService(db)
    
    def create_announcement(
        self,
        title: str,
        content_type: str,
        event_ids: List[int] = None,
        created_by: int = None
    ) -> Tuple[Optional[Announcement], str]:
        """
        创建公示
        content_type: event(项目排名), class(班级总分), grade(年级奖牌)
        """
        if content_type not in ("event", "class", "grade"):
            return None, "内容类型必须是event、class或grade"
        
        # 生成唯一分享码
        share_code = secrets.token_urlsafe(16)
        
        announcement = Announcement(
            title=title,
            share_code=share_code,
            content_type=content_type,
            event_ids=event_ids or [],
            is_active=True,
            created_by=created_by
        )
        
        self.db.add(announcement)
        self.db.commit()
        self.db.refresh(announcement)
        
        return announcement, ""
    
    def close_announcement(self, announcement_id: int) -> Tuple[bool, str]:
        """关闭公示"""
        announcement = self.db.query(Announcement).filter(
            Announcement.id == announcement_id
        ).first()
        
        if not announcement:
            return False, "公示不存在"
        
        if not announcement.is_active:
            return False, "公示已关闭"
        
        announcement.is_active = False
        announcement.closed_at = datetime.utcnow()
        self.db.commit()
        
        return True, ""
    
    def reopen_announcement(self, announcement_id: int) -> Tuple[bool, str]:
        """重新开启公示"""
        announcement = self.db.query(Announcement).filter(
            Announcement.id == announcement_id
        ).first()
        
        if not announcement:
            return False, "公示不存在"
        
        announcement.is_active = True
        announcement.closed_at = None
        self.db.commit()
        
        return True, ""
    
    def get_announcement_list(
        self,
        page: int = 1,
        page_size: int = 20,
        include_closed: bool = False
    ) -> Tuple[List[Announcement], int]:
        """获取公示列表"""
        query = self.db.query(Announcement)
        
        if not include_closed:
            query = query.filter(Announcement.is_active == True)
        
        query = query.order_by(Announcement.created_at.desc())
        
        total = query.count()
        announcements = query.offset((page - 1) * page_size).limit(page_size).all()
        
        return announcements, total
    
    def get_announcement_by_code(self, share_code: str) -> Tuple[Optional[Dict], str]:
        """
        根据分享码获取公示内容（公开访问）
        返回: (公示数据, 错误信息)
        """
        announcement = self.db.query(Announcement).filter(
            Announcement.share_code == share_code
        ).first()
        
        if not announcement:
            return None, "公示不存在"
        
        if not announcement.is_active:
            return None, "公示已结束"
        
        # 获取公示内容
        content = self._get_announcement_content(announcement)
        
        return {
            "id": announcement.id,
            "title": announcement.title,
            "content_type": announcement.content_type,
            "content": content,
            "created_at": announcement.created_at.isoformat() if announcement.created_at else None
        }, ""
    
    def _get_announcement_content(self, announcement: Announcement) -> Dict:
        """获取公示内容数据"""
        if announcement.content_type == "event":
            # 项目排名
            rankings = {}
            for event_id in announcement.event_ids:
                rankings[event_id] = self.stats_service.get_event_ranking(event_id)
            return {"event_rankings": rankings}
        
        elif announcement.content_type == "class":
            # 班级总分
            return {"class_total": self.stats_service.get_class_total()}
        
        elif announcement.content_type == "grade":
            # 年级奖牌
            return {"grade_medals": self.stats_service.get_grade_medals()}
        
        return {}
    
    def get_share_url(self, announcement_id: int, base_url: str = "") -> str:
        """获取分享链接"""
        announcement = self.db.query(Announcement).filter(
            Announcement.id == announcement_id
        ).first()
        
        if not announcement:
            return ""
        
        return f"{base_url}/public/announcement/{announcement.share_code}"
    
    def delete_announcement(self, announcement_id: int) -> Tuple[bool, str]:
        """删除公示"""
        announcement = self.db.query(Announcement).filter(
            Announcement.id == announcement_id
        ).first()
        
        if not announcement:
            return False, "公示不存在"
        
        self.db.delete(announcement)
        self.db.commit()
        
        return True, ""
