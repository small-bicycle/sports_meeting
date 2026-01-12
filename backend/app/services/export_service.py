"""
数据导出服务模块
实现报名表导出、成绩表导出、排名表导出、参赛表格生成
"""
from typing import List, Dict, Optional
from io import BytesIO
from sqlalchemy.orm import Session
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side

from app.models.registration import Registration
from app.models.score import Score
from app.models.base import Student, Class, Grade
from app.models.event import Event
from app.services.statistics_service import StatisticsService


class ExportService:
    """数据导出服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.stats_service = StatisticsService(db)
    
    def _create_workbook(self) -> Workbook:
        """创建工作簿"""
        return Workbook()
    
    def _style_header(self, ws, row: int = 1):
        """设置表头样式"""
        header_font = Font(bold=True)
        for cell in ws[row]:
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center')
    
    def export_registration_form(
        self,
        event_id: int = None,
        class_id: int = None,
        grade_id: int = None
    ) -> bytes:
        """导出报名表"""
        wb = self._create_workbook()
        ws = wb.active
        ws.title = "报名表"
        
        # 表头
        headers = ["序号", "学号", "姓名", "性别", "班级", "年级", "项目", "组别"]
        ws.append(headers)
        self._style_header(ws)
        
        # 查询数据
        query = self.db.query(Registration).join(Student).join(Class).join(Grade)
        
        if event_id:
            query = query.filter(Registration.event_id == event_id)
        if class_id:
            query = query.filter(Student.class_id == class_id)
        if grade_id:
            query = query.filter(Class.grade_id == grade_id)
        
        registrations = query.all()
        
        for idx, reg in enumerate(registrations, 1):
            ws.append([
                idx,
                reg.student.student_no,
                reg.student.name,
                "男" if reg.student.gender == "M" else "女",
                reg.student.class_.name,
                reg.student.class_.grade.name,
                reg.event.name,
                reg.group.name if reg.group else ""
            ])
        
        # 调整列宽
        for col in ws.columns:
            ws.column_dimensions[col[0].column_letter].width = 12
        
        output = BytesIO()
        wb.save(output)
        return output.getvalue()
    
    def export_score_sheet(
        self,
        event_id: int = None,
        class_id: int = None,
        grade_id: int = None
    ) -> bytes:
        """导出成绩表"""
        wb = self._create_workbook()
        ws = wb.active
        ws.title = "成绩表"
        
        headers = ["序号", "学号", "姓名", "班级", "年级", "项目", "成绩", "轮次", "排名", "得分"]
        ws.append(headers)
        self._style_header(ws)
        
        query = self.db.query(Score).join(Registration).join(Student).join(Class).join(Grade).filter(
            Score.is_valid == True
        )
        
        if event_id:
            query = query.filter(Registration.event_id == event_id)
        if class_id:
            query = query.filter(Student.class_id == class_id)
        if grade_id:
            query = query.filter(Class.grade_id == grade_id)
        
        scores = query.all()
        
        for idx, score in enumerate(scores, 1):
            reg = score.registration
            ws.append([
                idx,
                reg.student.student_no,
                reg.student.name,
                reg.student.class_.name,
                reg.student.class_.grade.name,
                reg.event.name,
                float(score.value),
                "预赛" if score.round == "preliminary" else "决赛",
                score.rank or "",
                score.points or 0
            ])
        
        for col in ws.columns:
            ws.column_dimensions[col[0].column_letter].width = 12
        
        output = BytesIO()
        wb.save(output)
        return output.getvalue()
    
    def export_ranking_sheet(self, type: str = "event", event_id: int = None) -> bytes:
        """导出排名表"""
        wb = self._create_workbook()
        ws = wb.active
        
        if type == "event":
            ws.title = "项目排名"
            headers = ["排名", "学号", "姓名", "班级", "年级", "成绩", "得分"]
            ws.append(headers)
            self._style_header(ws)
            
            if event_id:
                rankings = self.stats_service.get_event_ranking(event_id)
                for r in rankings:
                    ws.append([
                        r["rank"],
                        r["student"]["student_no"],
                        r["student"]["name"],
                        r["student"]["class_name"],
                        r["student"]["grade_name"],
                        r["score"]["value"],
                        r["points"]
                    ])
        
        elif type == "class":
            ws.title = "班级总分"
            headers = ["排名", "班级", "年级", "总分", "金牌", "银牌", "铜牌"]
            ws.append(headers)
            self._style_header(ws)
            
            rankings = self.stats_service.get_class_total()
            for r in rankings:
                ws.append([
                    r["rank"],
                    r["class"]["name"],
                    r["class"]["grade_name"],
                    r["total_score"],
                    r["gold"],
                    r["silver"],
                    r["bronze"]
                ])
        
        elif type == "grade":
            ws.title = "年级奖牌"
            headers = ["排名", "年级", "金牌", "银牌", "铜牌", "奖牌总数"]
            ws.append(headers)
            self._style_header(ws)
            
            rankings = self.stats_service.get_grade_medals()
            for r in rankings:
                ws.append([
                    r["rank"],
                    r["grade"]["name"],
                    r["gold"],
                    r["silver"],
                    r["bronze"],
                    r["total"]
                ])
        
        for col in ws.columns:
            ws.column_dimensions[col[0].column_letter].width = 12
        
        output = BytesIO()
        wb.save(output)
        return output.getvalue()
    
    def export_participant_form(
        self,
        event_id: int,
        custom_fields: List[str] = None
    ) -> bytes:
        """导出参赛表格"""
        wb = self._create_workbook()
        ws = wb.active
        
        event = self.db.query(Event).filter(Event.id == event_id).first()
        ws.title = event.name if event else "参赛表格"
        
        # 默认字段
        default_fields = ["序号", "道次", "学号", "姓名", "班级", "年级"]
        headers = default_fields + (custom_fields or [])
        ws.append(headers)
        self._style_header(ws)
        
        registrations = self.db.query(Registration).filter(
            Registration.event_id == event_id
        ).order_by(Registration.lane_no).all()
        
        for idx, reg in enumerate(registrations, 1):
            row = [
                idx,
                reg.lane_no or idx,
                reg.student.student_no,
                reg.student.name,
                reg.student.class_.name,
                reg.student.class_.grade.name
            ]
            # 自定义字段留空
            row.extend([""] * len(custom_fields or []))
            ws.append(row)
        
        for col in ws.columns:
            ws.column_dimensions[col[0].column_letter].width = 12
        
        output = BytesIO()
        wb.save(output)
        return output.getvalue()
    
    def export_all_events(self) -> bytes:
        """批量导出所有项目参赛表格"""
        wb = self._create_workbook()
        wb.remove(wb.active)  # 移除默认sheet
        
        events = self.db.query(Event).all()
        
        for event in events:
            ws = wb.create_sheet(title=event.name[:31])  # Excel限制31字符
            
            headers = ["序号", "道次", "学号", "姓名", "性别", "班级", "年级"]
            ws.append(headers)
            self._style_header(ws)
            
            registrations = self.db.query(Registration).filter(
                Registration.event_id == event.id
            ).order_by(Registration.lane_no).all()
            
            for idx, reg in enumerate(registrations, 1):
                ws.append([
                    idx,
                    reg.lane_no or idx,
                    reg.student.student_no,
                    reg.student.name,
                    "男" if reg.student.gender == "M" else "女",
                    reg.student.class_.name,
                    reg.student.class_.grade.name
                ])
            
            for col in ws.columns:
                ws.column_dimensions[col[0].column_letter].width = 12
        
        output = BytesIO()
        wb.save(output)
        return output.getvalue()
