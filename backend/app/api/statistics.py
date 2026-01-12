"""
统计排名API路由模块
"""
from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.statistics_service import StatisticsService
from app.api.deps import get_current_user, require_permission
from app.models.user import User
from app.schemas import (
    EventRankingItem,
    ClassTotalItem,
    GradeMedalsItem,
    ScoringRulesUpdate,
    ResponseBase
)

router = APIRouter(prefix="/statistics", tags=["统计排名"])


@router.get("/event-ranking/{event_id}", summary="获取项目排名")
async def get_event_ranking(
    event_id: int,
    round: str = Query("final", description="轮次（preliminary/final）"),
    top_n: int = Query(None, description="只返回前N名"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    获取项目排名
    
    - **event_id**: 项目ID
    - **round**: 轮次（preliminary/final）
    - **top_n**: 只返回前N名（可选）
    
    排名规则：
    - 径赛：成绩升序（时间越短越好）
    - 田赛：成绩降序（距离/高度越大越好）
    """
    stats_service = StatisticsService(db)
    rankings = stats_service.get_event_ranking(
        event_id=event_id,
        round=round,
        top_n=top_n
    )
    
    return {"rankings": rankings}


@router.get("/class-total", summary="获取班级总分榜")
async def get_class_total(
    grade_id: int = Query(None, description="按年级筛选"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    获取班级总分榜
    
    - **grade_id**: 按年级筛选（可选）
    
    按总分降序排列，同时显示金银铜牌数
    """
    stats_service = StatisticsService(db)
    rankings = stats_service.get_class_total(grade_id=grade_id)
    
    return {"rankings": rankings}


@router.get("/grade-medals", summary="获取年级奖牌榜")
async def get_grade_medals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    获取年级奖牌榜
    
    按金牌数、银牌数、铜牌数依次排序
    """
    stats_service = StatisticsService(db)
    rankings = stats_service.get_grade_medals()
    
    return {"rankings": rankings}


@router.get("/scoring-rules", summary="获取计分规则")
async def get_scoring_rules(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    获取当前计分规则
    
    返回名次与得分的对应关系
    """
    stats_service = StatisticsService(db)
    rules = stats_service.get_scoring_rules()
    
    return {"rules": rules}


@router.put("/scoring-rules", response_model=ResponseBase, summary="更新计分规则")
async def update_scoring_rules(
    request: ScoringRulesUpdate,
    current_user: User = Depends(require_permission("score_manage")),
    db: Session = Depends(get_db)
):
    """
    更新计分规则
    
    - **rules**: 名次与得分的对应关系，如 {"1": 9, "2": 7, "3": 6, ...}
    
    更新后会应用到所有项目
    """
    stats_service = StatisticsService(db)
    stats_service.update_scoring_rules(request.rules)
    
    return ResponseBase(message="计分规则更新成功")


@router.post("/recalculate", response_model=ResponseBase, summary="重新计算所有排名")
async def recalculate_rankings(
    current_user: User = Depends(require_permission("score_manage")),
    db: Session = Depends(get_db)
):
    """
    重新计算所有项目的排名和得分
    
    用于计分规则变更后重新计算
    """
    stats_service = StatisticsService(db)
    count = stats_service.recalculate_all_rankings()
    
    return ResponseBase(message=f"已重新计算{count}个项目的排名")
