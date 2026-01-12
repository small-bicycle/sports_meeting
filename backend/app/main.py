"""
FastAPI 应用主入口
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.exceptions import BusinessException
from app.core.middleware import OperationLogMiddleware, ExceptionHandlerMiddleware

# 创建FastAPI应用实例
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="学校教师专属的校运会综合管理平台",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# 存储debug模式
app.debug = settings.DEBUG

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加操作日志中间件
app.add_middleware(OperationLogMiddleware)

# 添加异常处理中间件
app.add_middleware(ExceptionHandlerMiddleware)


# 业务异常处理器
@app.exception_handler(BusinessException)
async def business_exception_handler(request: Request, exc: BusinessException):
    """处理业务异常"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.code,
            "message": exc.message,
            "detail": exc.detail
        }
    )


# 注册API路由
from app.api import auth, users, grades, classes, students, events
from app.api import registrations, scores, statistics, exports, announcements
from app.api import public, logs

app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(grades.router, prefix="/api")
app.include_router(classes.router, prefix="/api")
app.include_router(students.router, prefix="/api")
app.include_router(events.router, prefix="/api")
app.include_router(registrations.router, prefix="/api")
app.include_router(scores.router, prefix="/api")
app.include_router(statistics.router, prefix="/api")
app.include_router(exports.router, prefix="/api")
app.include_router(announcements.router, prefix="/api")
app.include_router(public.router, prefix="/api")
app.include_router(logs.router, prefix="/api")


@app.get("/")
async def root():
    """根路径健康检查"""
    return {
        "message": "校园运动会教师端管理系统",
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/api/health")
async def health_check():
    """API健康检查"""
    return {"status": "healthy"}
