"""
班级管理API路由模块
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.base_service import BaseService
from app.api.deps import get_current_user, require_permission
from app.models.user import User
from app.schemas import (
    ClassInfo,
    ClassCreate,
    ClassUpdate,
    ResponseBase,
    DeleteResponse
)

router = APIRouter(prefix="/classes", tags=["班级管理"])


@router.get("", response_model=List[ClassInfo], summary="获取班级列表")
async def get_classes(
    grade_id: int = Query(None, description="按年级筛选"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取班级列表
    
    - **grade_id**: 可选，按年级ID筛选
    """
    base_service = BaseService(db)
    classes = base_service.get_class_list(grade_id=grade_id)
    
    return [
        ClassInfo(
            id=c.id,
            grade_id=c.grade_id,
            name=c.name,
            grade_name=c.grade.name if c.grade else None,
            created_at=c.created_at
        ) for c in classes
    ]


@router.post("", response_model=ClassInfo, summary="创建班级")
async def create_class(
    request: ClassCreate,
    current_user: User = Depends(require_permission("base_manage")),
    db: Session = Depends(get_db)
):
    """
    创建班级
    
    - **grade_id**: 所属年级ID
    - **name**: 班级名称
    """
    base_service = BaseService(db)
    class_, error = base_service.create_class(
        grade_id=request.grade_id,
        name=request.name
    )
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return ClassInfo(
        id=class_.id,
        grade_id=class_.grade_id,
        name=class_.name,
        grade_name=class_.grade.name if class_.grade else None,
        created_at=class_.created_at
    )


@router.put("/{class_id}", response_model=ClassInfo, summary="更新班级")
async def update_class(
    class_id: int,
    request: ClassUpdate,
    current_user: User = Depends(require_permission("base_manage")),
    db: Session = Depends(get_db)
):
    """
    更新班级信息
    """
    base_service = BaseService(db)
    class_, error = base_service.update_class(
        class_id=class_id,
        grade_id=request.grade_id,
        name=request.name
    )
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return ClassInfo(
        id=class_.id,
        grade_id=class_.grade_id,
        name=class_.name,
        grade_name=class_.grade.name if class_.grade else None,
        created_at=class_.created_at
    )


@router.post("/batch", response_model=ResponseBase, summary="批量创建班级")
async def batch_create_classes(
    grade_id: int = Query(..., description="年级ID"),
    class_count: int = Query(..., description="班级数量"),
    prefix: str = Query("", description="班级名称前缀"),
    current_user: User = Depends(require_permission("base_manage")),
    db: Session = Depends(get_db)
):
    """
    批量创建班级
    
    - **grade_id**: 年级ID
    - **class_count**: 要创建的班级数量
    - **prefix**: 班级名称前缀，如"高一"，则创建"高一1班"、"高一2班"等
    """
    base_service = BaseService(db)
    created = 0
    errors = []
    
    for i in range(1, class_count + 1):
        name = f"{prefix}{i}班" if prefix else f"{i}班"
        class_, error = base_service.create_class(grade_id=grade_id, name=name)
        if error:
            errors.append(f"{name}: {error}")
        else:
            created += 1
    
    if errors:
        return ResponseBase(message=f"成功创建{created}个班级，{len(errors)}个失败: {'; '.join(errors)}")
    return ResponseBase(message=f"成功创建{created}个班级")


@router.delete("/clear-all", response_model=ResponseBase, summary="清空所有班级")
async def clear_all_classes(
    current_user: User = Depends(require_permission("base_manage")),
    db: Session = Depends(get_db)
):
    """
    清空所有班级（同时会清空所有学生）
    """
    from app.models.base import Class, Student
    from sqlalchemy import text
    
    # 先删除学生
    student_count = db.query(Student).delete()
    # 再删除班级
    class_count = db.query(Class).delete()
    db.commit()
    
    # 重置自增ID（MySQL语法）
    db.execute(text("ALTER TABLE students AUTO_INCREMENT = 1"))
    db.execute(text("ALTER TABLE classes AUTO_INCREMENT = 1"))
    db.commit()
    
    return ResponseBase(message=f"已清空 {class_count} 个班级、{student_count} 个学生")


@router.delete("/{class_id}", response_model=DeleteResponse, summary="删除班级")
async def delete_class(
    class_id: int,
    current_user: User = Depends(require_permission("base_manage")),
    db: Session = Depends(get_db)
):
    """
    删除班级
    
    如果班级下有学生，将无法删除
    """
    base_service = BaseService(db)
    success, error, affected = base_service.delete_class(class_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return DeleteResponse(message="删除成功", affected=affected if affected else None)
