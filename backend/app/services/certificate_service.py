"""
奖状生成服务模块
实现奖状模板管理、批量生成、PDF导出
"""
from typing import List, Dict, Tuple, Optional
from io import BytesIO
from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import black, gold, red
import os

from app.models.score import Score
from app.models.registration import Registration
from app.models.event import Event


# 奖状模板配置
CERTIFICATE_TEMPLATES = [
    {
        "id": 1,
        "name": "标准奖状",
        "description": "适用于各类比赛的标准奖状模板"
    },
    {
        "id": 2,
        "name": "金牌奖状",
        "description": "适用于第一名的特殊奖状模板"
    },
    {
        "id": 3,
        "name": "团体奖状",
        "description": "适用于接力赛等团体项目"
    }
]


class CertificateService:
    """奖状生成服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_templates(self) -> List[Dict]:
        """获取奖状模板列表"""
        return CERTIFICATE_TEMPLATES
    
    def generate_certificates(
        self,
        event_id: int = None,
        rank_range: Tuple[int, int] = (1, 3),
        template_id: int = 1,
        title: str = "校园运动会",
        signature: str = "学校体育部",
        date: str = None
    ) -> bytes:
        """
        批量生成奖状PDF
        rank_range: (起始名次, 结束名次)
        """
        # 查询获奖成绩
        query = self.db.query(Score).join(Registration).filter(
            Score.is_valid == True,
            Score.round == "final",
            Score.rank >= rank_range[0],
            Score.rank <= rank_range[1]
        )
        
        if event_id:
            query = query.filter(Registration.event_id == event_id)
        
        scores = query.order_by(Score.rank).all()
        
        # 创建PDF
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=landscape(A4))
        width, height = landscape(A4)
        
        for score in scores:
            self._draw_certificate(
                c, width, height,
                score=score,
                title=title,
                signature=signature,
                date=date,
                template_id=template_id
            )
            c.showPage()
        
        c.save()
        return buffer.getvalue()
    
    def _draw_certificate(
        self,
        c: canvas.Canvas,
        width: float,
        height: float,
        score: Score,
        title: str,
        signature: str,
        date: str,
        template_id: int
    ):
        """绘制单张奖状"""
        reg = score.registration
        student = reg.student
        event = reg.event
        
        # 获取名次文字
        rank_text = self._get_rank_text(score.rank)
        
        # 绘制边框
        c.setStrokeColor(gold if score.rank == 1 else black)
        c.setLineWidth(3)
        c.rect(1*cm, 1*cm, width-2*cm, height-2*cm)
        
        # 绘制标题
        c.setFont("Helvetica-Bold", 36)
        c.drawCentredString(width/2, height - 3*cm, title)
        
        # 绘制"奖状"
        c.setFont("Helvetica-Bold", 48)
        c.setFillColor(red if score.rank == 1 else black)
        c.drawCentredString(width/2, height - 5*cm, "CERTIFICATE")
        c.setFillColor(black)
        
        # 绘制内容
        c.setFont("Helvetica", 24)
        content_y = height - 8*cm
        
        # 学生信息
        c.drawCentredString(width/2, content_y, f"Student: {student.name}")
        content_y -= 1.2*cm
        
        c.drawCentredString(width/2, content_y, f"Class: {student.class_.grade.name} {student.class_.name}")
        content_y -= 1.5*cm
        
        # 比赛信息
        c.setFont("Helvetica", 20)
        c.drawCentredString(width/2, content_y, f"Event: {event.name}")
        content_y -= 1.2*cm
        
        c.drawCentredString(width/2, content_y, f"Result: {float(score.value)} {event.unit}")
        content_y -= 1.2*cm
        
        # 名次
        c.setFont("Helvetica-Bold", 28)
        c.setFillColor(gold if score.rank == 1 else black)
        c.drawCentredString(width/2, content_y, f"Rank: {rank_text}")
        c.setFillColor(black)
        
        # 落款
        c.setFont("Helvetica", 16)
        c.drawString(width - 8*cm, 3*cm, signature)
        if date:
            c.drawString(width - 8*cm, 2.2*cm, date)
    
    def _get_rank_text(self, rank: int) -> str:
        """获取名次文字"""
        rank_map = {
            1: "First Place (Gold)",
            2: "Second Place (Silver)",
            3: "Third Place (Bronze)",
            4: "Fourth Place",
            5: "Fifth Place",
            6: "Sixth Place",
            7: "Seventh Place",
            8: "Eighth Place"
        }
        return rank_map.get(rank, f"No. {rank}")
    
    def preview_certificate(
        self,
        student_name: str,
        class_name: str,
        event_name: str,
        score_value: float,
        unit: str,
        rank: int,
        title: str = "校园运动会",
        signature: str = "学校体育部"
    ) -> bytes:
        """预览奖状（使用模拟数据）"""
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=landscape(A4))
        width, height = landscape(A4)
        
        rank_text = self._get_rank_text(rank)
        
        # 绘制边框
        c.setStrokeColor(gold if rank == 1 else black)
        c.setLineWidth(3)
        c.rect(1*cm, 1*cm, width-2*cm, height-2*cm)
        
        # 绘制标题
        c.setFont("Helvetica-Bold", 36)
        c.drawCentredString(width/2, height - 3*cm, title)
        
        c.setFont("Helvetica-Bold", 48)
        c.setFillColor(red if rank == 1 else black)
        c.drawCentredString(width/2, height - 5*cm, "CERTIFICATE")
        c.setFillColor(black)
        
        # 内容
        c.setFont("Helvetica", 24)
        content_y = height - 8*cm
        
        c.drawCentredString(width/2, content_y, f"Student: {student_name}")
        content_y -= 1.2*cm
        c.drawCentredString(width/2, content_y, f"Class: {class_name}")
        content_y -= 1.5*cm
        
        c.setFont("Helvetica", 20)
        c.drawCentredString(width/2, content_y, f"Event: {event_name}")
        content_y -= 1.2*cm
        c.drawCentredString(width/2, content_y, f"Result: {score_value} {unit}")
        content_y -= 1.2*cm
        
        c.setFont("Helvetica-Bold", 28)
        c.setFillColor(gold if rank == 1 else black)
        c.drawCentredString(width/2, content_y, f"Rank: {rank_text}")
        c.setFillColor(black)
        
        c.setFont("Helvetica", 16)
        c.drawString(width - 8*cm, 3*cm, signature)
        
        c.showPage()
        c.save()
        return buffer.getvalue()
