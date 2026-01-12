"""
排名统计服务模块
实现项目排名计算、班级总分汇总、年级奖牌统计
"""
from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc
from collections import defaultdict

from app.models.score import Score
from app.models.registration import Registration
from app.models.base import Student, Class, Grade
from app.models.event import Event


class StatisticsService:
    """排名统计服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_event_ranking(
        self,
        event_id: int,
        round: str = "final",
        top_n: int = None
    ) -> List[Dict]:
        """
        获取项目排名
        返回: [{rank, student, score, points}]
        """
        event = self.db.query(Event).filter(Event.id == event_id).first()
        if not event:
            return []
        
        # 查询有效成绩
        query = self.db.query(Score, Registration, Student).join(
            Registration, Score.registration_id == Registration.id
        ).join(
            Student, Registration.student_id == Student.id
        ).filter(
            Registration.event_id == event_id,
            Score.round == round,
            Score.is_valid == True
        )
        
        # 根据项目类型排序（径赛升序，田赛降序）
        if event.type == "track":
            query = query.order_by(asc(Score.value))
        else:
            query = query.order_by(desc(Score.value))
        
        if top_n:
            query = query.limit(top_n)
        
        results = query.all()
        
        # 计算排名和得分
        rankings = []
        scoring_rule = event.scoring_rule or {}
        
        for idx, (score, registration, student) in enumerate(results, 1):
            points = scoring_rule.get(str(idx), 0)
            
            # 更新数据库中的排名和得分
            score.rank = idx
            score.points = points
            
            rankings.append({
                "rank": idx,
                "student": {
                    "id": student.id,
                    "name": student.name,
                    "student_no": student.student_no,
                    "class_name": student.class_.name,
                    "grade_name": student.class_.grade.name
                },
                "score": {
                    "id": score.id,
                    "value": float(score.value),
                    "round": score.round
                },
                "points": points
            })
        
        self.db.commit()
        return rankings
    
    def get_class_total(self, grade_id: int = None) -> List[Dict]:
        """
        获取班级总分榜
        返回: [{rank, class, total_score, gold, silver, bronze}]
        """
        # 查询所有有效成绩
        query = self.db.query(
            Class.id,
            Class.name,
            Grade.name.label("grade_name"),
            func.sum(Score.points).label("total_score"),
            func.sum(func.IF(Score.rank == 1, 1, 0)).label("gold"),
            func.sum(func.IF(Score.rank == 2, 1, 0)).label("silver"),
            func.sum(func.IF(Score.rank == 3, 1, 0)).label("bronze")
        ).join(
            Student, Class.id == Student.class_id
        ).join(
            Registration, Student.id == Registration.student_id
        ).join(
            Score, Registration.id == Score.registration_id
        ).join(
            Grade, Class.grade_id == Grade.id
        ).filter(
            Score.is_valid == True,
            Score.round == "final"
        ).group_by(Class.id)
        
        if grade_id:
            query = query.filter(Class.grade_id == grade_id)
        
        query = query.order_by(desc("total_score"))
        
        results = query.all()
        
        rankings = []
        for idx, row in enumerate(results, 1):
            rankings.append({
                "rank": idx,
                "class": {
                    "id": row.id,
                    "name": row.name,
                    "grade_name": row.grade_name
                },
                "total_score": int(row.total_score or 0),
                "gold": int(row.gold or 0),
                "silver": int(row.silver or 0),
                "bronze": int(row.bronze or 0)
            })
        
        return rankings
    
    def get_grade_medals(self) -> List[Dict]:
        """
        获取年级奖牌榜
        返回: [{rank, grade, gold, silver, bronze, total}]
        """
        query = self.db.query(
            Grade.id,
            Grade.name,
            func.sum(func.IF(Score.rank == 1, 1, 0)).label("gold"),
            func.sum(func.IF(Score.rank == 2, 1, 0)).label("silver"),
            func.sum(func.IF(Score.rank == 3, 1, 0)).label("bronze")
        ).join(
            Class, Grade.id == Class.grade_id
        ).join(
            Student, Class.id == Student.class_id
        ).join(
            Registration, Student.id == Registration.student_id
        ).join(
            Score, Registration.id == Score.registration_id
        ).filter(
            Score.is_valid == True,
            Score.round == "final"
        ).group_by(Grade.id).order_by(
            desc("gold"), desc("silver"), desc("bronze")
        )
        
        results = query.all()
        
        rankings = []
        for idx, row in enumerate(results, 1):
            gold = int(row.gold or 0)
            silver = int(row.silver or 0)
            bronze = int(row.bronze or 0)
            
            rankings.append({
                "rank": idx,
                "grade": {
                    "id": row.id,
                    "name": row.name
                },
                "gold": gold,
                "silver": silver,
                "bronze": bronze,
                "total": gold + silver + bronze
            })
        
        return rankings
    
    def get_scoring_rules(self) -> Dict:
        """获取计分规则"""
        event = self.db.query(Event).first()
        if event and event.scoring_rule:
            return event.scoring_rule
        return {"1": 9, "2": 7, "3": 6, "4": 5, "5": 4, "6": 3, "7": 2, "8": 1}
    
    def update_scoring_rules(self, rules: Dict) -> bool:
        """更新所有项目的计分规则"""
        events = self.db.query(Event).all()
        for event in events:
            event.scoring_rule = rules
        self.db.commit()
        return True
    
    def recalculate_all_rankings(self) -> int:
        """重新计算所有项目排名"""
        events = self.db.query(Event).all()
        count = 0
        for event in events:
            self.get_event_ranking(event.id, "final")
            if event.has_preliminary:
                self.get_event_ranking(event.id, "preliminary")
            count += 1
        return count
