"""
年级管理API路由模块
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.base_service import BaseService
from app.api.deps import get_current_user, require_permission
from app.models.user import User
from app.schemas import (
    GradeInfo,
    GradeCreate,
    GradeUpdate,
    ResponseBase,
    DeleteResponse
)

router = APIRouter(prefix="/grades", tags=["年级管理"])


@router.get("", response_model=List[GradeInfo], summary="获取年级列表")
async def get_grades(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取所有年级列表
    
    按排序序号和ID排序
    """
    base_service = BaseService(db)
    grades = base_service.get_grade_list()
    
    return [
        GradeInfo(
            id=g.id,
            name=g.name,
            sort_order=g.sort_order,
            created_at=g.created_at
        ) for g in grades
    ]


@router.post("", response_model=GradeInfo, summary="创建年级")
async def create_grade(
    request: GradeCreate,
    current_user: User = Depends(require_permission("base_manage")),
    db: Session = Depends(get_db)
):
    """
    创建年级
    
    - **name**: 年级名称
    - **sort_order**: 排序序号
    """
    base_service = BaseService(db)
    grade, error = base_service.create_grade(
        name=request.name,
        sort_order=request.sort_order
    )
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return GradeInfo(
        id=grade.id,
        name=grade.name,
        sort_order=grade.sort_order,
        created_at=grade.created_at
    )


@router.put("/{grade_id}", response_model=GradeInfo, summary="更新年级")
async def update_grade(
    grade_id: int,
    request: GradeUpdate,
    current_user: User = Depends(require_permission("base_manage")),
    db: Session = Depends(get_db)
):
    """
    更新年级信息
    """
    base_service = BaseService(db)
    grade, error = base_service.update_grade(
        grade_id=grade_id,
        name=request.name,
        sort_order=request.sort_order
    )
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return GradeInfo(
        id=grade.id,
        name=grade.name,
        sort_order=grade.sort_order,
        created_at=grade.created_at
    )


@router.post("/batch", response_model=ResponseBase, summary="批量创建年级")
async def batch_create_grades(
    names: List[str],
    current_user: User = Depends(require_permission("base_manage")),
    db: Session = Depends(get_db)
):
    """
    批量创建年级
    
    - **names**: 年级名称列表
    """
    base_service = BaseService(db)
    created = 0
    errors = []
    
    for i, name in enumerate(names):
        if not name or not name.strip():
            continue
        grade, error = base_service.create_grade(name=name.strip(), sort_order=i)
        if error:
            errors.append(f"{name}: {error}")
        else:
            created += 1
    
    if errors:
        return ResponseBase(message=f"成功创建{created}个年级，{len(errors)}个失败: {'; '.join(errors)}")
    return ResponseBase(message=f"成功创建{created}个年级")


@router.delete("/clear-all", response_model=ResponseBase, summary="清空所有年级")
async def clear_all_grades(
    current_user: User = Depends(require_permission("base_manage")),
    db: Session = Depends(get_db)
):
    """
    清空所有年级（同时会清空所有班级和学生）
    """
    from app.models.base import Grade, Class, Student
    from sqlalchemy import text
    
    # 先删除学生
    student_count = db.query(Student).delete()
    # 再删除班级
    class_count = db.query(Class).delete()
    # 最后删除年级
    grade_count = db.query(Grade).delete()
    db.commit()
    
    # 重置自增ID（MySQL语法）
    db.execute(text("ALTER TABLE students AUTO_INCREMENT = 1"))
    db.execute(text("ALTER TABLE classes AUTO_INCREMENT = 1"))
    db.execute(text("ALTER TABLE grades AUTO_INCREMENT = 1"))
    db.commit()
    
    return ResponseBase(message=f"已清空 {grade_count} 个年级、{class_count} 个班级、{student_count} 个学生")


@router.delete("/{grade_id}", response_model=DeleteResponse, summary="删除年级")
async def delete_grade(
    grade_id: int,
    current_user: User = Depends(require_permission("base_manage")),
    db: Session = Depends(get_db)
):
    """
    删除年级
    
    如果年级下有班级，将无法删除
    """
    base_service = BaseService(db)
    success, error, affected = base_service.delete_grade(grade_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return DeleteResponse(message="删除成功", affected=affected if affected else None)
