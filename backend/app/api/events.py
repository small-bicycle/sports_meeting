"""
运动项目管理API路由模块
"""
from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.event_service import EventService
from app.api.deps import get_current_user, require_permission
from app.models.user import User
from app.schemas import (
    EventInfo,
    EventCreate,
    EventUpdate,
    EventGroupInfo,
    EventGroupCreate,
    EventGroupUpdate,
    DeleteResponse,
    ResponseBase
)

router = APIRouter(prefix="/events", tags=["运动项目管理"])


@router.get("", response_model=List[EventInfo], summary="获取项目列表")
async def get_events(
    type: str = Query(None, description="按类型筛选（track/field）"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取运动项目列表
    
    - **type**: 可选，按项目类型筛选
      - track: 径赛
      - field: 田赛
    """
    event_service = EventService(db)
    events = event_service.get_event_list(type=type)
    
    return [
        EventInfo(
            id=e.id,
            name=e.name,
            type=e.type,
            category=e.category,
            unit=e.unit,
            max_per_class=e.max_per_class,
            max_per_student=e.max_per_student,
            has_preliminary=e.has_preliminary,
            scoring_rule=e.scoring_rule or {},
            groups=[
                EventGroupInfo(
                    id=g.id,
                    event_id=g.event_id,
                    name=g.name,
                    gender=g.gender,
                    grade_ids=g.grade_ids or []
                ) for g in e.groups
            ]
        ) for e in events
    ]


@router.post("", response_model=EventInfo, summary="创建项目")
async def create_event(
    request: EventCreate,
    current_user: User = Depends(require_permission("event_manage")),
    db: Session = Depends(get_db)
):
    """
    创建运动项目
    
    - **name**: 项目名称
    - **type**: 项目类型（track/field）
    - **category**: 子分类（短距离跑/中距离跑/接力跑/跨栏跑/投掷/跳跃/趣味/游泳/跳绳）
    - **unit**: 成绩单位
    - **max_per_class**: 每班限报人数
    - **max_per_student**: 每人限报项目数
    - **has_preliminary**: 是否有预赛
    - **scoring_rule**: 计分规则
    - **groups**: 项目组别列表
    """
    event_service = EventService(db)
    event, error = event_service.create_event(
        name=request.name,
        type=request.type,
        unit=request.unit,
        category=request.category,
        max_per_class=request.max_per_class,
        max_per_student=request.max_per_student,
        has_preliminary=request.has_preliminary,
        scoring_rule=request.scoring_rule
    )
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    # 创建组别
    for group_data in request.groups:
        event_service.create_group(
            event_id=event.id,
            name=group_data.name,
            gender=group_data.gender,
            grade_ids=group_data.grade_ids
        )
    
    # 重新获取完整数据
    event = event_service.get_event_by_id(event.id)
    
    return EventInfo(
        id=event.id,
        name=event.name,
        type=event.type,
        category=event.category,
        unit=event.unit,
        max_per_class=event.max_per_class,
        max_per_student=event.max_per_student,
        has_preliminary=event.has_preliminary,
        scoring_rule=event.scoring_rule or {},
        groups=[
            EventGroupInfo(
                id=g.id,
                event_id=g.event_id,
                name=g.name,
                gender=g.gender,
                grade_ids=g.grade_ids or []
            ) for g in event.groups
        ]
    )


@router.get("/templates", summary="获取预置项目模板")
async def get_templates(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[Dict]:
    """
    获取预置项目模板列表
    
    可用于快速创建常见运动项目
    """
    event_service = EventService(db)
    return event_service.get_templates()


@router.post("/from-template", response_model=EventInfo, summary="从模板创建项目")
async def create_from_template(
    template_name: str = Query(..., description="模板名称"),
    current_user: User = Depends(require_permission("event_manage")),
    db: Session = Depends(get_db)
):
    """
    从预置模板创建项目，自动创建默认组别
    - 个人项目：自动创建男子组、女子组
    - 团体项目：自动创建团体组
    """
    event_service = EventService(db)
    event, error = event_service.create_from_template(template_name)
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return EventInfo(
        id=event.id,
        name=event.name,
        type=event.type,
        category=event.category,
        unit=event.unit,
        max_per_class=event.max_per_class,
        max_per_student=event.max_per_student,
        has_preliminary=event.has_preliminary,
        scoring_rule=event.scoring_rule or {},
        groups=[
            EventGroupInfo(
                id=g.id,
                event_id=g.event_id,
                name=g.name,
                gender=g.gender,
                grade_ids=g.grade_ids or []
            ) for g in event.groups
        ]
    )


@router.post("/batch-from-templates", summary="批量从模板创建项目")
async def batch_create_from_templates(
    template_names: List[str],
    current_user: User = Depends(require_permission("event_manage")),
    db: Session = Depends(get_db)
):
    """
    批量从模板创建项目
    
    - **template_names**: 模板名称列表
    """
    event_service = EventService(db)
    success, fail, errors = event_service.batch_create_from_templates(template_names)
    
    return {
        "success": success,
        "failed": fail,
        "errors": errors,
        "message": f"成功创建 {success} 个项目" + (f"，{fail} 个失败" if fail > 0 else "")
    }


@router.delete("/all", summary="清除所有项目")
async def delete_all_events(
    current_user: User = Depends(require_permission("event_manage")),
    db: Session = Depends(get_db)
):
    """
    一键清除所有项目（包括组别）
    
    注意：如果存在报名记录，将无法删除
    """
    event_service = EventService(db)
    count, error = event_service.delete_all_events()
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return {"message": f"成功删除 {count} 个项目", "deleted": count}


@router.get("/{event_id}", response_model=EventInfo, summary="获取项目详情")
async def get_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取项目详情
    """
    event_service = EventService(db)
    event = event_service.get_event_by_id(event_id)
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    return EventInfo(
        id=event.id,
        name=event.name,
        type=event.type,
        category=event.category,
        unit=event.unit,
        max_per_class=event.max_per_class,
        max_per_student=event.max_per_student,
        has_preliminary=event.has_preliminary,
        scoring_rule=event.scoring_rule or {},
        groups=[
            EventGroupInfo(
                id=g.id,
                event_id=g.event_id,
                name=g.name,
                gender=g.gender,
                grade_ids=g.grade_ids or []
            ) for g in event.groups
        ]
    )


@router.put("/{event_id}", response_model=EventInfo, summary="更新项目")
async def update_event(
    event_id: int,
    request: EventUpdate,
    current_user: User = Depends(require_permission("event_manage")),
    db: Session = Depends(get_db)
):
    """
    更新项目信息
    """
    event_service = EventService(db)
    event, error = event_service.update_event(
        event_id=event_id,
        name=request.name,
        type=request.type,
        unit=request.unit,
        category=request.category,
        max_per_class=request.max_per_class,
        max_per_student=request.max_per_student,
        has_preliminary=request.has_preliminary,
        scoring_rule=request.scoring_rule
    )
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return EventInfo(
        id=event.id,
        name=event.name,
        type=event.type,
        category=event.category,
        unit=event.unit,
        max_per_class=event.max_per_class,
        max_per_student=event.max_per_student,
        has_preliminary=event.has_preliminary,
        scoring_rule=event.scoring_rule or {},
        groups=[
            EventGroupInfo(
                id=g.id,
                event_id=g.event_id,
                name=g.name,
                gender=g.gender,
                grade_ids=g.grade_ids or []
            ) for g in event.groups
        ]
    )


@router.delete("/{event_id}", response_model=DeleteResponse, summary="删除项目")
async def delete_event(
    event_id: int,
    current_user: User = Depends(require_permission("event_manage")),
    db: Session = Depends(get_db)
):
    """
    删除项目
    
    如果项目有报名记录，将无法删除
    """
    event_service = EventService(db)
    success, error, affected = event_service.delete_event(event_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return DeleteResponse(message="删除成功", affected=affected if affected else None)


# ========== 组别管理 ==========

@router.get("/{event_id}/groups", response_model=List[EventGroupInfo], summary="获取项目组别列表")
async def get_event_groups(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取项目的组别列表
    """
    event_service = EventService(db)
    event = event_service.get_event_by_id(event_id)
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    return [
        EventGroupInfo(
            id=g.id,
            event_id=g.event_id,
            name=g.name,
            gender=g.gender,
            grade_ids=g.grade_ids or []
        ) for g in event.groups
    ]


@router.post("/{event_id}/groups", response_model=EventGroupInfo, summary="创建组别")
async def create_group(
    event_id: int,
    request: EventGroupCreate,
    current_user: User = Depends(require_permission("event_manage")),
    db: Session = Depends(get_db)
):
    """
    为项目创建组别
    
    - **name**: 组别名称
    - **gender**: 性别限制（M/F/A）
    - **grade_ids**: 适用年级ID列表
    """
    event_service = EventService(db)
    group, error = event_service.create_group(
        event_id=event_id,
        name=request.name,
        gender=request.gender,
        grade_ids=request.grade_ids
    )
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return EventGroupInfo(
        id=group.id,
        event_id=group.event_id,
        name=group.name,
        gender=group.gender,
        grade_ids=group.grade_ids or []
    )


@router.put("/groups/{group_id}", response_model=EventGroupInfo, summary="更新组别")
async def update_group(
    group_id: int,
    request: EventGroupUpdate,
    current_user: User = Depends(require_permission("event_manage")),
    db: Session = Depends(get_db)
):
    """
    更新组别信息
    """
    event_service = EventService(db)
    group, error = event_service.update_group(
        group_id=group_id,
        name=request.name,
        gender=request.gender,
        grade_ids=request.grade_ids
    )
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return EventGroupInfo(
        id=group.id,
        event_id=group.event_id,
        name=group.name,
        gender=group.gender,
        grade_ids=group.grade_ids or []
    )


@router.delete("/groups/{group_id}", response_model=ResponseBase, summary="删除组别")
async def delete_group(
    group_id: int,
    current_user: User = Depends(require_permission("event_manage")),
    db: Session = Depends(get_db)
):
    """
    删除组别
    
    如果组别有报名记录，将无法删除
    """
    event_service = EventService(db)
    success, error = event_service.delete_group(group_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return ResponseBase(message="删除成功")
