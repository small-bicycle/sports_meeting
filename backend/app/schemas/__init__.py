"""
Pydantic schemas for API request/response models
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ========== 通用响应模型 ==========

class ResponseBase(BaseModel):
    """基础响应模型"""
    message: str = "success"


class ErrorResponse(BaseModel):
    """错误响应模型"""
    error: str
    detail: Optional[str] = None


class PaginatedResponse(BaseModel):
    """分页响应模型"""
    items: List[Any]
    total: int
    page: int
    page_size: int


# ========== 认证相关 ==========

class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1)


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str
    token_type: str = "bearer"
    user: "UserInfo"


class PasswordChangeRequest(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=6, max_length=50)


# ========== 用户相关 ==========

class UserInfo(BaseModel):
    """用户信息"""
    id: int
    username: str
    name: str
    permissions: List[str]
    is_admin: bool
    is_active: bool

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    """创建用户请求"""
    username: str = Field(..., min_length=2, max_length=50)
    name: str = Field(..., min_length=1, max_length=50)
    permissions: List[str] = []
    is_admin: bool = False


class UserCreateResponse(BaseModel):
    """创建用户响应"""
    id: int
    username: str
    initial_password: str


class UserUpdate(BaseModel):
    """更新用户请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    permissions: Optional[List[str]] = None
    is_active: Optional[bool] = None


# ========== 年级相关 ==========

class GradeInfo(BaseModel):
    """年级信息"""
    id: int
    name: str
    sort_order: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class GradeCreate(BaseModel):
    """创建年级请求"""
    name: str = Field(..., min_length=1, max_length=50)
    sort_order: int = 0


class GradeUpdate(BaseModel):
    """更新年级请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    sort_order: Optional[int] = None


# ========== 班级相关 ==========

class ClassInfo(BaseModel):
    """班级信息"""
    id: int
    grade_id: int
    name: str
    grade_name: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ClassCreate(BaseModel):
    """创建班级请求"""
    grade_id: int
    name: str = Field(..., min_length=1, max_length=50)


class ClassUpdate(BaseModel):
    """更新班级请求"""
    grade_id: Optional[int] = None
    name: Optional[str] = Field(None, min_length=1, max_length=50)


# ========== 学生相关 ==========

class StudentInfo(BaseModel):
    """学生信息"""
    id: int
    class_id: int
    student_no: str
    name: str
    gender: str
    class_name: Optional[str] = None
    grade_name: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class StudentCreate(BaseModel):
    """创建学生请求"""
    class_id: int
    student_no: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=50)
    gender: str = Field(..., pattern="^[MF]$")


class StudentUpdate(BaseModel):
    """更新学生请求"""
    class_id: Optional[int] = None
    student_no: Optional[str] = Field(None, min_length=1, max_length=20)
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    gender: Optional[str] = Field(None, pattern="^[MF]$")


# ========== 运动项目相关 ==========

class EventGroupInfo(BaseModel):
    """项目组别信息"""
    id: int
    event_id: int
    name: str
    gender: str
    grade_ids: List[int]

    class Config:
        from_attributes = True


class EventGroupCreate(BaseModel):
    """创建组别请求"""
    name: str = Field(..., min_length=1, max_length=50)
    gender: str = Field(default="A", pattern="^[MFA]$")
    grade_ids: List[int] = []


class EventGroupUpdate(BaseModel):
    """更新组别请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    gender: Optional[str] = Field(None, pattern="^[MFA]$")
    grade_ids: Optional[List[int]] = None


class EventInfo(BaseModel):
    """项目信息"""
    id: int
    name: str
    type: str
    unit: str
    max_per_class: int
    max_per_student: int
    has_preliminary: bool
    scoring_rule: Dict[str, int]
    groups: List[EventGroupInfo] = []

    class Config:
        from_attributes = True


class EventCreate(BaseModel):
    """创建项目请求"""
    name: str = Field(..., min_length=1, max_length=100)
    type: str = Field(..., pattern="^(track|field|relay)$")
    unit: str = Field(..., min_length=1, max_length=20)
    max_per_class: int = Field(default=3, ge=1)
    max_per_student: int = Field(default=3, ge=1)
    has_preliminary: bool = False
    scoring_rule: Optional[Dict[str, int]] = None
    groups: List[EventGroupCreate] = []


class EventUpdate(BaseModel):
    """更新项目请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[str] = Field(None, pattern="^(track|field|relay)$")
    unit: Optional[str] = Field(None, min_length=1, max_length=20)
    max_per_class: Optional[int] = Field(None, ge=1)
    max_per_student: Optional[int] = Field(None, ge=1)
    has_preliminary: Optional[bool] = None
    scoring_rule: Optional[Dict[str, int]] = None


# ========== 报名相关 ==========

class RegistrationInfo(BaseModel):
    """报名信息"""
    id: int
    student_id: int
    event_id: int
    group_id: Optional[int]
    lane_no: Optional[int]
    student_name: Optional[str] = None
    student_no: Optional[str] = None
    class_name: Optional[str] = None
    grade_name: Optional[str] = None
    event_name: Optional[str] = None
    group_name: Optional[str] = None

    class Config:
        from_attributes = True


class RegistrationCreate(BaseModel):
    """创建报名请求"""
    student_id: int
    event_id: int
    group_id: Optional[int] = None


class RegistrationLaneUpdate(BaseModel):
    """更新道次请求"""
    lane_no: int


class DuplicateCheckResponse(BaseModel):
    """查重检测响应"""
    is_duplicate: bool
    existing: Optional[RegistrationInfo] = None


# ========== 成绩相关 ==========

class ScoreInfo(BaseModel):
    """成绩信息"""
    id: int
    registration_id: int
    value: float
    round: str
    rank: Optional[int]
    points: int
    is_valid: bool
    invalid_reason: Optional[str]
    update_reason: Optional[str]
    student_name: Optional[str] = None
    student_no: Optional[str] = None
    class_name: Optional[str] = None
    event_name: Optional[str] = None

    class Config:
        from_attributes = True


class ScoreCreate(BaseModel):
    """录入成绩请求"""
    registration_id: int
    value: float
    round: str = Field(default="final", pattern="^(preliminary|final)$")
    overwrite: bool = False


class ScoreUpdate(BaseModel):
    """修改成绩请求"""
    value: float
    reason: str = Field(..., min_length=1, max_length=200)


class ScoreInvalidate(BaseModel):
    """作废成绩请求"""
    reason: str = Field(..., min_length=1, max_length=200)


class ScoreDuplicateCheckResponse(BaseModel):
    """成绩查重响应"""
    exists: bool
    existing: Optional[ScoreInfo] = None


# ========== 统计相关 ==========

class RankingStudent(BaseModel):
    """排名学生信息"""
    id: int
    name: str
    student_no: str
    class_name: str
    grade_name: str


class RankingScore(BaseModel):
    """排名成绩信息"""
    id: int
    value: float
    round: str


class EventRankingItem(BaseModel):
    """项目排名项"""
    rank: int
    student: RankingStudent
    score: RankingScore
    points: int


class ClassTotalItem(BaseModel):
    """班级总分项"""
    rank: int
    class_info: Dict[str, Any] = Field(alias="class")
    total_score: int
    gold: int
    silver: int
    bronze: int

    class Config:
        populate_by_name = True


class GradeMedalsItem(BaseModel):
    """年级奖牌项"""
    rank: int
    grade: Dict[str, Any]
    gold: int
    silver: int
    bronze: int
    total: int


class ScoringRulesUpdate(BaseModel):
    """更新计分规则请求"""
    rules: Dict[str, int]


# ========== 公示相关 ==========

class AnnouncementInfo(BaseModel):
    """公示信息"""
    id: int
    title: str
    share_code: str
    content_type: str
    event_ids: List[int]
    is_active: bool
    created_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AnnouncementCreate(BaseModel):
    """创建公示请求"""
    title: str = Field(..., min_length=1, max_length=200)
    content_type: str = Field(..., pattern="^(event|class|grade)$")
    event_ids: List[int] = []


class AnnouncementCreateResponse(BaseModel):
    """创建公示响应"""
    id: int
    share_url: str
    share_code: str


class PublicAnnouncementResponse(BaseModel):
    """公开公示响应"""
    id: int
    title: str
    content_type: str
    content: Dict[str, Any]
    created_at: Optional[str] = None


# ========== 导出相关 ==========

class ExportRequest(BaseModel):
    """导出请求"""
    event_id: Optional[int] = None
    class_id: Optional[int] = None
    grade_id: Optional[int] = None


class CertificateGenerateRequest(BaseModel):
    """奖状生成请求"""
    event_id: Optional[int] = None
    rank_start: int = Field(default=1, ge=1)
    rank_end: int = Field(default=3, ge=1)
    template_id: int = 1
    title: str = "校园运动会"
    signature: str = "学校体育部"
    date: Optional[str] = None


class CertificatePreviewRequest(BaseModel):
    """奖状预览请求"""
    student_name: str
    class_name: str
    event_name: str
    score_value: float
    unit: str
    rank: int
    title: str = "校园运动会"
    signature: str = "学校体育部"


# ========== 导入响应 ==========

class ImportResponse(BaseModel):
    """导入响应"""
    success: int
    failed: int
    errors: List[str]


# ========== 删除响应 ==========

class DeleteResponse(BaseModel):
    """删除响应"""
    message: str
    affected: Optional[Dict[str, int]] = None


# 更新前向引用
LoginResponse.model_rebuild()
