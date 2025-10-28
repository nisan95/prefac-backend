"""
Enrollment Model
"""
from datetime import datetime
from ..extensions import db

class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    progress = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='not-started')
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'course_id', name='unique_user_course'),)
    
    def update_progress(self):
        """Calcule et met à jour la progression"""
        from app.models.lesson import Lesson
        from app.models.lesson_progress import LessonProgress
        from app.models.chapter import Chapter
        
        chapters = Chapter.query.filter_by(course_id=self.course_id).all()
        total = sum(len(Lesson.query.filter_by(chapter_id=ch.id).all()) for ch in chapters)
        completed = sum(1 for ch in chapters for lesson in Lesson.query.filter_by(chapter_id=ch.id).all()
                       if LessonProgress.query.filter_by(user_id=self.user_id, lesson_id=lesson.id, is_completed=True).first())
        
        self.progress = int((completed / total) * 100) if total > 0 else 0
        
        if self.progress == 0:
            self.status = 'not-started'
        elif self.progress == 100:
            self.status = 'completed'
            if not self.completed_at:
                self.completed_at = datetime.utcnow()
        else:
            self.status = 'in-progress'
        
        db.session.commit()
    
    def to_dict(self):
        return {
            'id': self.course.id,
            'title': self.course.title,
            'category': self.course.category,
            'description': self.course.description,
            'progress': self.progress,
            'status': self.status,
            'instructor': self.course.instructor,
            'duration': self.course.duration,
            'rating': self.course.rating,
            'lastAccessed': self.last_accessed.isoformat() if self.last_accessed else None,
            'totalLessons': self.get_total_lessons(),
            'completedLessons': self.get_completed_lessons()
        }
    
    def get_total_lessons(self):
        from app.models.lesson import Lesson
        from app.models.chapter import Chapter
        return sum(Lesson.query.filter_by(chapter_id=ch.id).count() 
                  for ch in Chapter.query.filter_by(course_id=self.course_id).all())
    
    def get_completed_lessons(self):
        from app.models.lesson_progress import LessonProgress
        return LessonProgress.query.filter_by(user_id=self.user_id, is_completed=True).count()
    
    def __repr__(self):
        return f'<Enrollment User:{self.user_id} Course:{self.course_id}>'