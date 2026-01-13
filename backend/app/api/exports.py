"""
数据导出API路由模块
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from io import BytesIO

from app.core.database import get_db
from app.services.export_service import ExportService
from app.services.certificate_service import CertificateService
from app.api.deps import get_current_user, require_permission
from app.models.user import User
from app.schemas import (
    CertificateGenerateRequest,
    CertificatePreviewRequest,
    ExportableClassInfo,
    ClassRegistrationExportRequest
)

router = APIRouter(prefix="/exports", tags=["数据导出"])


# ========== 班级报名表导出 ==========

@router.get("/exportable-classes", summary="获取可导出班级列表")
async def get_exportable_classes(
    current_user: User = Depends(require_permission("export")),
    db: Session = Depends(get_db)
):
    """
    获取所有有报名记录的班级列表
    
    返回按年级分组的班级信息，包含班级ID、名称、年级名称和报名人数
    """
    export_service = ExportService(db)
    classes = export_service.get_exportable_classes()
    
    # 按年级分组
    grades_dict = {}
    for cls in classes:
        grade_id = cls["grade_id"]
        if grade_id not in grades_dict:
            grades_dict[grade_id] = {
                "id": grade_id,
                "name": cls["grade_name"],
                "classes": []
            }
        grades_dict[grade_id]["classes"].append(cls)
    
    return {"grades": list(grades_dict.values())}


@router.post("/registration-forms", summary="批量导出班级报名表")
async def export_class_registration_forms(
    request: ClassRegistrationExportRequest,
    current_user: User = Depends(require_permission("export")),
    db: Session = Depends(get_db)
):
    """
    批量导出选定班级的报名表Excel
    
    - **class_ids**: 班级ID列表（至少选择一个班级）
    
    每个班级生成独立的工作表，按项目组别分组显示报名记录
    """
    export_service = ExportService(db)
    
    try:
        content = export_service.export_class_registration_forms(request.class_ids)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    return StreamingResponse(
        BytesIO(content),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=class_registration_forms.xlsx"}
    )


@router.get("/registration-form", summary="导出报名表")
async def export_registration_form(
    event_id: int = Query(None, description="按项目筛选"),
    class_id: int = Query(None, description="按班级筛选"),
    grade_id: int = Query(None, description="按年级筛选"),
    current_user: User = Depends(require_permission("export")),
    db: Session = Depends(get_db)
):
    """
    导出报名表 - 每个班级一个独立的Excel文件，打包成ZIP
    
    支持按项目、班级、年级筛选
    """
    export_service = ExportService(db)
    content = export_service.export_registration_form(
        event_id=event_id,
        class_id=class_id,
        grade_id=grade_id
    )
    
    return StreamingResponse(
        BytesIO(content),
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=registration_forms.zip"}
    )


@router.get("/score-sheet", summary="导出成绩表")
async def export_score_sheet(
    event_id: int = Query(None, description="按项目筛选"),
    class_id: int = Query(None, description="按班级筛选"),
    grade_id: int = Query(None, description="按年级筛选"),
    current_user: User = Depends(require_permission("export")),
    db: Session = Depends(get_db)
):
    """
    导出成绩表Excel
    
    支持按项目、班级、年级筛选
    """
    export_service = ExportService(db)
    content = export_service.export_score_sheet(
        event_id=event_id,
        class_id=class_id,
        grade_id=grade_id
    )
    
    return StreamingResponse(
        BytesIO(content),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=score_sheet.xlsx"}
    )


@router.get("/ranking-sheet", summary="导出排名表")
async def export_ranking_sheet(
    type: str = Query(..., description="排名类型（event/class/grade）"),
    event_id: int = Query(None, description="项目ID（type=event时必填）"),
    current_user: User = Depends(require_permission("export")),
    db: Session = Depends(get_db)
):
    """
    导出排名表Excel
    
    - **type**: 排名类型
      - event: 项目排名
      - class: 班级总分
      - grade: 年级奖牌
    - **event_id**: 项目ID（type=event时必填）
    """
    if type == "event" and not event_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="导出项目排名时必须指定event_id"
        )
    
    export_service = ExportService(db)
    content = export_service.export_ranking_sheet(
        type=type,
        event_id=event_id
    )
    
    filename_map = {
        "event": "event_ranking.xlsx",
        "class": "class_total.xlsx",
        "grade": "grade_medals.xlsx"
    }
    
    return StreamingResponse(
        BytesIO(content),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename_map.get(type, 'ranking.xlsx')}"}
    )


@router.get("/participant-form", summary="导出参赛表格")
async def export_participant_form(
    event_id: int = Query(..., description="项目ID"),
    custom_fields: List[str] = Query(None, description="自定义字段列表"),
    current_user: User = Depends(require_permission("export")),
    db: Session = Depends(get_db)
):
    """
    导出参赛表格Excel
    
    - **event_id**: 项目ID
    - **custom_fields**: 自定义字段列表（可选）
    
    默认包含：序号、道次、学号、姓名、班级、年级
    """
    export_service = ExportService(db)
    content = export_service.export_participant_form(
        event_id=event_id,
        custom_fields=custom_fields
    )
    
    return StreamingResponse(
        BytesIO(content),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=participant_form.xlsx"}
    )


@router.get("/all-events", summary="批量导出所有项目参赛表格")
async def export_all_events(
    current_user: User = Depends(require_permission("export")),
    db: Session = Depends(get_db)
):
    """
    批量导出所有项目的参赛表格
    
    每个项目一个工作表
    """
    export_service = ExportService(db)
    content = export_service.export_all_events()
    
    return StreamingResponse(
        BytesIO(content),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=all_events.xlsx"}
    )


# ========== 奖状生成 ==========

@router.get("/certificates/templates", summary="获取奖状模板列表")
async def get_certificate_templates(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取可用的奖状模板列表
    """
    cert_service = CertificateService(db)
    templates = cert_service.get_templates()
    
    return {"templates": templates}


@router.post("/certificates/generate", summary="批量生成奖状")
async def generate_certificates(
    request: CertificateGenerateRequest,
    current_user: User = Depends(require_permission("export")),
    db: Session = Depends(get_db)
):
    """
    批量生成奖状PDF
    
    - **event_id**: 项目ID（可选，不指定则生成所有项目）
    - **rank_start**: 起始名次
    - **rank_end**: 结束名次
    - **template_id**: 模板ID
    - **title**: 奖状标题
    - **signature**: 落款
    - **date**: 日期
    """
    cert_service = CertificateService(db)
    content = cert_service.generate_certificates(
        event_id=request.event_id,
        rank_range=(request.rank_start, request.rank_end),
        template_id=request.template_id,
        title=request.title,
        signature=request.signature,
        date=request.date
    )
    
    return StreamingResponse(
        BytesIO(content),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=certificates.pdf"}
    )


@router.post("/certificates/preview", summary="预览奖状")
async def preview_certificate(
    request: CertificatePreviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    预览奖状（使用模拟数据）
    
    用于查看奖状样式
    """
    cert_service = CertificateService(db)
    content = cert_service.preview_certificate(
        student_name=request.student_name,
        class_name=request.class_name,
        event_name=request.event_name,
        score_value=request.score_value,
        unit=request.unit,
        rank=request.rank,
        title=request.title,
        signature=request.signature
    )
    
    return StreamingResponse(
        BytesIO(content),
        media_type="application/pdf",
        headers={"Content-Disposition": "inline; filename=certificate_preview.pdf"}
    )
