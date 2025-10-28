"""
Course Model
"""
from datetime import datetime
from ..extensions import db

class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False, index=True)
    description = db.Column(db.Text)
    instructor = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.String(50))
    level = db.Column(db.String(20), default='Débutant')
    rating = db.Column(db.Float, default=0.0)
    students_count = db.Column(db.Integer, default=0)
    thumbnail = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    chapters = db.relationship('Chapter', backref='course', lazy=True, cascade='all, delete-orphan', order_by='Chapter.order')
    enrollments = db.relationship('Enrollment', backref='course', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self, include_chapters=False):
        data = {
            'id': self.id,
            'title': self.title,
            'category': self.category,
            'description': self.description,
            'instructor': self.instructor,
            'duration': self.duration,
            'level': self.level,
            'rating': self.rating,
            'studentsCount': self.students_count,
            'thumbnail': self.thumbnail
        }
        if include_chapters:
            data['chapters'] = [ch.to_dict(include_lessons=True) for ch in self.chapters]
        return data
    
    def __repr__(self):
        return f'<Course {self.title}>'