"""
Lesson Progress Model
"""
from datetime import datetime
from ..extensions import db

class LessonProgress(db.Model):
    __tablename__ = 'lesson_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    is_current = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'lesson_id', name='unique_user_lesson'),)
    
    def mark_as_completed(self):
        """Marque comme complétée"""
        self.is_completed = True
        self.is_current = False
        self.completed_at = datetime.utcnow()
        db.session.commit()
        
        # Mettre à jour la progression du cours
        from app.models.enrollment import Enrollment
        enrollment = Enrollment.query.filter_by(
            user_id=self.user_id,
            course_id=self.lesson.chapter.course_id
        ).first()
        
        if enrollment:
            enrollment.update_progress()
    
    def __repr__(self):
        return f'<LessonProgress User:{self.user_id} Lesson:{self.lesson_id}>'