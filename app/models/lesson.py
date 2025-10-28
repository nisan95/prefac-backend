"""
Lesson Model
"""
from datetime import datetime
from ..extensions import db

class Lesson(db.Model):
    __tablename__ = 'lessons'
    
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    duration = db.Column(db.String(50))
    order = db.Column(db.Integer, nullable=False)
    is_locked = db.Column(db.Boolean, default=False)
    is_quiz = db.Column(db.Boolean, default=False)
    content = db.Column(db.Text)
    video_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    progress_records = db.relationship('LessonProgress', backref='lesson', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self, user_id=None):
        data = {
            'id': self.id,
            'title': self.title,
            'duration': self.duration,
            'isLocked': self.is_locked,
            'isQuiz': self.is_quiz,
            'content': self.content,
            'videoUrl': self.video_url
        }
        
        if user_id:
            from app.models.lesson_progress import LessonProgress
            progress = LessonProgress.query.filter_by(user_id=user_id, lesson_id=self.id).first()
            data['isCompleted'] = progress.is_completed if progress else False
            data['isCurrent'] = progress.is_current if progress else False
        else:
            data['isCompleted'] = False
            data['isCurrent'] = False
        
        return data
    
    def __repr__(self):
        return f'<Lesson {self.title}>'