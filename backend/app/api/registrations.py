"""
报名管理API路由模块
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.registration_service import RegistrationService
from app.api.deps import get_current_user, require_permission
from app.models.user import User
from app.schemas import (
    RegistrationInfo,
    RegistrationCreate,
    RegistrationLaneUpdate,
    DuplicateCheckResponse,
    ResponseBase,
    ImportResponse
)

router = APIRouter(prefix="/registrations", tags=["报名管理"])


@router.get("", summary="获取报名列表")
async def get_registrations(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    event_id: int = Query(None, description="按项目筛选"),
    class_id: int = Query(None, description="按班级筛选"),
    grade_id: int = Query(None, description="按年级筛选"),
    student_id: int = Query(None, description="按学生筛选"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取报名列表
    
    支持多条件筛选：
    - **event_id**: 按项目筛选
    - **class_id**: 按班级筛选
    - **grade_id**: 按年级筛选
    - **student_id**: 按学生筛选
    """
    reg_service = RegistrationService(db)
    registrations, total = reg_service.get_registration_list(
        page=page,
        page_size=page_size,
        event_id=event_id,
        class_id=class_id,
        grade_id=grade_id,
        student_id=student_id
    )
    
    return {
        "items": [
            RegistrationInfo(
                id=r.id,
                student_id=r.student_id,
                event_id=r.event_id,
                group_id=r.group_id,
                lane_no=r.lane_no,
                student_name=r.student.name if r.student else None,
                student_no=r.student.student_no if r.student else None,
                class_name=r.student.class_.name if r.student and r.student.class_ else None,
                grade_name=r.student.class_.grade.name if r.student and r.student.class_ and r.student.class_.grade else None,
                event_name=r.event.name if r.event else None,
                group_name=r.group.name if r.group else None
            ) for r in registrations
        ],
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.post("", response_model=RegistrationInfo, summary="创建报名")
async def create_registration(
    request: RegistrationCreate,
    current_user: User = Depends(require_permission("registration_manage")),
    db: Session = Depends(get_db)
):
    """
    创建报名记录
    
    - **student_id**: 学生ID
    - **event_id**: 项目ID
    - **group_id**: 组别ID（可选）
    
    系统会自动检查：
    - 是否重复报名
    - 班级报名人数是否超限
    - 个人报名项目数是否超限
    """
    reg_service = RegistrationService(db)
    registration, error = reg_service.create_registration(
        student_id=request.student_id,
        event_id=request.event_id,
        group_id=request.group_id,
        created_by=current_user.id
    )
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return RegistrationInfo(
        id=registration.id,
        student_id=registration.student_id,
        event_id=registration.event_id,
        group_id=registration.group_id,
        lane_no=registration.lane_no,
        student_name=registration.student.name if registration.student else None,
        student_no=registration.student.student_no if registration.student else None,
        class_name=registration.student.class_.name if registration.student and registration.student.class_ else None,
        grade_name=registration.student.class_.grade.name if registration.student and registration.student.class_ and registration.student.class_.grade else None,
        event_name=registration.event.name if registration.event else None,
        group_name=registration.group.name if registration.group else None
    )


@router.get("/check-duplicate", response_model=DuplicateCheckResponse, summary="查重检测")
async def check_duplicate(
    student_id: int = Query(..., description="学生ID"),
    event_id: int = Query(..., description="项目ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    检查是否重复报名
    """
    reg_service = RegistrationService(db)
    is_duplicate, existing = reg_service.check_duplicate(student_id, event_id)
    
    existing_info = None
    if existing:
        existing_info = RegistrationInfo(
            id=existing.id,
            student_id=existing.student_id,
            event_id=existing.event_id,
            group_id=existing.group_id,
            lane_no=existing.lane_no,
            student_name=existing.student.name if existing.student else None,
            student_no=existing.student.student_no if existing.student else None,
            class_name=existing.student.class_.name if existing.student and existing.student.class_ else None,
            grade_name=existing.student.class_.grade.name if existing.student and existing.student.class_ and existing.student.class_.grade else None,
            event_name=existing.event.name if existing.event else None,
            group_name=existing.group.name if existing.group else None
        )
    
    return DuplicateCheckResponse(
        is_duplicate=is_duplicate,
        existing=existing_info
    )


@router.put("/{registration_id}/lane", response_model=ResponseBase, summary="更新道次")
async def update_lane(
    registration_id: int,
    request: RegistrationLaneUpdate,
    current_user: User = Depends(require_permission("registration_manage")),
    db: Session = Depends(get_db)
):
    """
    更新报名记录的道次/序号
    """
    reg_service = RegistrationService(db)
    success, error = reg_service.update_lane_no(registration_id, request.lane_no)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return ResponseBase(message="更新成功")


@router.delete("/{registration_id}", response_model=ResponseBase, summary="取消报名")
async def delete_registration(
    registration_id: int,
    current_user: User = Depends(require_permission("registration_manage")),
    db: Session = Depends(get_db)
):
    """
    取消报名
    
    如果已有成绩记录，将无法取消
    """
    reg_service = RegistrationService(db)
    success, error = reg_service.delete_registration(registration_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return ResponseBase(message="取消成功")


@router.post("/import", response_model=ImportResponse, summary="批量导入报名")
async def import_registrations(
    file: UploadFile = File(..., description="Excel文件"),
    current_user: User = Depends(require_permission("registration_manage")),
    db: Session = Depends(get_db)
):
    """
    批量导入报名
    
    Excel格式要求：
    - 第一行为表头
    - 列顺序：学号, 项目名称, 组别名称(可选)
    
    系统会自动执行查重和限制校验
    """
    # 检查文件类型
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只支持Excel文件格式(.xlsx, .xls)"
        )
    
    # 读取文件内容
    content = await file.read()
    
    reg_service = RegistrationService(db)
    success, failed, errors = reg_service.import_registrations(
        content,
        created_by=current_user.id
    )
    
    return ImportResponse(
        success=success,
        failed=failed,
        errors=errors
    )
