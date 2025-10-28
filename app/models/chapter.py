"""
Chapter Model
"""
from datetime import datetime
from ..extensions import db

class Chapter(db.Model):
    __tablename__ = 'chapters'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    duration = db.Column(db.String(50))
    order = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    lessons = db.relationship('Lesson', backref='chapter', lazy=True, cascade='all, delete-orphan', order_by='Lesson.order')
    
    def to_dict(self, include_lessons=False, user_id=None):
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'duration': self.duration,
            'lessonsCount': len(self.lessons)
        }
        
        if include_lessons:
            data['lessons'] = [lesson.to_dict(user_id=user_id) for lesson in self.lessons]
            
            if user_id:
                from app.models.lesson_progress import LessonProgress
                completed = sum(1 for lesson in self.lessons 
                              if LessonProgress.query.filter_by(user_id=user_id, lesson_id=lesson.id, is_completed=True).first())
                data['completedLessons'] = completed
                data['isCompleted'] = completed == len(self.lessons) if self.lessons else False
        
        return data
    
    def __repr__(self):
        return f'<Chapter {self.title}>'