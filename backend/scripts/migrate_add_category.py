"""
迁移脚本：为 events 表添加 category 字段
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine

def migrate():
    """添加 category 字段"""
    with engine.connect() as conn:
        # 检查字段是否已存在
        try:
            conn.execute(text("SELECT category FROM events LIMIT 1"))
            print("category 字段已存在，无需迁移")
            return
        except:
            pass
        
        # 添加字段
        conn.execute(text("ALTER TABLE events ADD COLUMN category VARCHAR(50)"))
        conn.commit()
        print("成功添加 category 字段")

if __name__ == "__main__":
    migrate()
