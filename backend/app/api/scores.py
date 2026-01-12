"""
成绩管理API路由模块
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.score_service import ScoreService
from app.api.deps import get_current_user, require_permission
from app.models.user import User
from app.schemas import (
    ScoreInfo,
    ScoreCreate,
    ScoreUpdate,
    ScoreInvalidate,
    ScoreDuplicateCheckResponse,
    ResponseBase,
    ImportResponse
)

router = APIRouter(prefix="/scores", tags=["成绩管理"])


@router.get("", summary="获取成绩列表")
async def get_scores(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    event_id: int = Query(None, description="按项目筛选"),
    class_id: int = Query(None, description="按班级筛选"),
    grade_id: int = Query(None, description="按年级筛选"),
    student_id: int = Query(None, description="按学生筛选"),
    round: str = Query(None, description="按轮次筛选（preliminary/final）"),
    include_invalid: bool = Query(False, description="是否包含作废成绩"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取成绩列表
    
    支持多条件筛选：
    - **event_id**: 按项目筛选
    - **class_id**: 按班级筛选
    - **grade_id**: 按年级筛选
    - **student_id**: 按学生筛选
    - **round**: 按轮次筛选
    - **include_invalid**: 是否包含作废成绩
    """
    score_service = ScoreService(db)
    scores, total = score_service.get_score_list(
        page=page,
        page_size=page_size,
        event_id=event_id,
        class_id=class_id,
        grade_id=grade_id,
        student_id=student_id,
        round=round,
        include_invalid=include_invalid
    )
    
    return {
        "items": [
            ScoreInfo(
                id=s.id,
                registration_id=s.registration_id,
                value=float(s.value),
                round=s.round,
                rank=s.rank,
                points=s.points or 0,
                is_valid=s.is_valid,
                invalid_reason=s.invalid_reason,
                update_reason=s.update_reason,
                student_name=s.registration.student.name if s.registration and s.registration.student else None,
                student_no=s.registration.student.student_no if s.registration and s.registration.student else None,
                class_name=s.registration.student.class_.name if s.registration and s.registration.student and s.registration.student.class_ else None,
                event_name=s.registration.event.name if s.registration and s.registration.event else None
            ) for s in scores
        ],
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.post("", response_model=ScoreInfo, summary="录入成绩")
async def create_score(
    request: ScoreCreate,
    current_user: User = Depends(require_permission("score_manage")),
    db: Session = Depends(get_db)
):
    """
    录入成绩
    
    - **registration_id**: 报名ID
    - **value**: 成绩值
    - **round**: 轮次（preliminary/final）
    - **overwrite**: 是否覆盖已存在的成绩
    """
    score_service = ScoreService(db)
    score, error = score_service.create_score(
        registration_id=request.registration_id,
        value=request.value,
        round=request.round,
        created_by=current_user.id,
        overwrite=request.overwrite
    )
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return ScoreInfo(
        id=score.id,
        registration_id=score.registration_id,
        value=float(score.value),
        round=score.round,
        rank=score.rank,
        points=score.points or 0,
        is_valid=score.is_valid,
        invalid_reason=score.invalid_reason,
        update_reason=score.update_reason,
        student_name=score.registration.student.name if score.registration and score.registration.student else None,
        student_no=score.registration.student.student_no if score.registration and score.registration.student else None,
        class_name=score.registration.student.class_.name if score.registration and score.registration.student and score.registration.student.class_ else None,
        event_name=score.registration.event.name if score.registration and score.registration.event else None
    )


@router.get("/check-duplicate", response_model=ScoreDuplicateCheckResponse, summary="成绩查重")
async def check_duplicate(
    registration_id: int = Query(..., description="报名ID"),
    round: str = Query(..., description="轮次（preliminary/final）"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    检查是否已存在成绩记录
    """
    score_service = ScoreService(db)
    exists, existing = score_service.check_duplicate(registration_id, round)
    
    existing_info = None
    if existing:
        existing_info = ScoreInfo(
            id=existing.id,
            registration_id=existing.registration_id,
            value=float(existing.value),
            round=existing.round,
            rank=existing.rank,
            points=existing.points or 0,
            is_valid=existing.is_valid,
            invalid_reason=existing.invalid_reason,
            update_reason=existing.update_reason
        )
    
    return ScoreDuplicateCheckResponse(
        exists=exists,
        existing=existing_info
    )


@router.get("/{score_id}", response_model=ScoreInfo, summary="获取成绩详情")
async def get_score(
    score_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取成绩详情
    """
    score_service = ScoreService(db)
    score = score_service.get_score_by_id(score_id)
    
    if not score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="成绩记录不存在"
        )
    
    return ScoreInfo(
        id=score.id,
        registration_id=score.registration_id,
        value=float(score.value),
        round=score.round,
        rank=score.rank,
        points=score.points or 0,
        is_valid=score.is_valid,
        invalid_reason=score.invalid_reason,
        update_reason=score.update_reason,
        student_name=score.registration.student.name if score.registration and score.registration.student else None,
        student_no=score.registration.student.student_no if score.registration and score.registration.student else None,
        class_name=score.registration.student.class_.name if score.registration and score.registration.student and score.registration.student.class_ else None,
        event_name=score.registration.event.name if score.registration and score.registration.event else None
    )


@router.put("/{score_id}", response_model=ScoreInfo, summary="修改成绩")
async def update_score(
    score_id: int,
    request: ScoreUpdate,
    current_user: User = Depends(require_permission("score_manage")),
    db: Session = Depends(get_db)
):
    """
    修改成绩
    
    - **value**: 新成绩值
    - **reason**: 修改原因（必填）
    
    系统会保留修改记录
    """
    score_service = ScoreService(db)
    score, error = score_service.update_score(
        score_id=score_id,
        value=request.value,
        reason=request.reason,
        updated_by=current_user.id
    )
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return ScoreInfo(
        id=score.id,
        registration_id=score.registration_id,
        value=float(score.value),
        round=score.round,
        rank=score.rank,
        points=score.points or 0,
        is_valid=score.is_valid,
        invalid_reason=score.invalid_reason,
        update_reason=score.update_reason,
        student_name=score.registration.student.name if score.registration and score.registration.student else None,
        student_no=score.registration.student.student_no if score.registration and score.registration.student else None,
        class_name=score.registration.student.class_.name if score.registration and score.registration.student and score.registration.student.class_ else None,
        event_name=score.registration.event.name if score.registration and score.registration.event else None
    )


@router.put("/{score_id}/invalidate", response_model=ScoreInfo, summary="作废成绩")
async def invalidate_score(
    score_id: int,
    request: ScoreInvalidate,
    current_user: User = Depends(require_permission("score_manage")),
    db: Session = Depends(get_db)
):
    """
    作废成绩
    
    - **reason**: 作废原因（必填）
    
    原始数据会保留，仅标记为无效状态
    """
    score_service = ScoreService(db)
    score, error = score_service.invalidate_score(
        score_id=score_id,
        reason=request.reason,
        updated_by=current_user.id
    )
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return ScoreInfo(
        id=score.id,
        registration_id=score.registration_id,
        value=float(score.value),
        round=score.round,
        rank=score.rank,
        points=score.points or 0,
        is_valid=score.is_valid,
        invalid_reason=score.invalid_reason,
        update_reason=score.update_reason,
        student_name=score.registration.student.name if score.registration and score.registration.student else None,
        student_no=score.registration.student.student_no if score.registration and score.registration.student else None,
        class_name=score.registration.student.class_.name if score.registration and score.registration.student and score.registration.student.class_ else None,
        event_name=score.registration.event.name if score.registration and score.registration.event else None
    )


@router.post("/import", response_model=ImportResponse, summary="批量导入成绩")
async def import_scores(
    file: UploadFile = File(..., description="Excel文件"),
    round: str = Query("final", description="轮次（preliminary/final）"),
    current_user: User = Depends(require_permission("score_manage")),
    db: Session = Depends(get_db)
):
    """
    批量导入成绩
    
    Excel格式要求：
    - 第一行为表头
    - 列顺序：学号, 项目名称, 成绩
    
    系统会自动匹配学生和项目，已存在的成绩会被覆盖
    """
    # 检查文件类型
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只支持Excel文件格式(.xlsx, .xls)"
        )
    
    # 读取文件内容
    content = await file.read()
    
    score_service = ScoreService(db)
    success, failed, errors = score_service.import_scores(
        content,
        round=round,
        created_by=current_user.id
    )
    
    return ImportResponse(
        success=success,
        failed=failed,
        errors=errors
    )
