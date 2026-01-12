# API路由模块

from app.api import auth
from app.api import users
from app.api import grades
from app.api import classes
from app.api import students
from app.api import events
from app.api import registrations
from app.api import scores
from app.api import statistics
from app.api import exports
from app.api import announcements
from app.api import public
from app.api import logs

__all__ = [
    "auth",
    "users",
    "grades",
    "classes",
    "students",
    "events",
    "registrations",
    "scores",
    "statistics",
    "exports",
    "announcements",
    "public",
    "logs"
]
