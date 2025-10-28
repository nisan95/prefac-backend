"""
Courses Routes
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from ..extensions import db
from ..models.course import Course
from ..models.enrollment import Enrollment
from ..models.chapter import Chapter
from ..models.lesson import Lesson
from ..models.lesson_progress import LessonProgress

courses_bp = Blueprint('courses', __name__, url_prefix='/api/courses')

@courses_bp.route('/my-courses', methods=['GET'])
@jwt_required()
def get_my_courses():
    """
    GET /api/courses/my-courses
    Récupère tous les cours de l'utilisateur avec filtres
    """
    try:
        user_id = get_jwt_identity()
        
        # Paramètres de filtrage
        search = request.args.get('search', '').strip()
        category = request.args.get('category', '').strip()
        status = request.args.get('status', '').strip()
        
        # Requête de base
        query = Enrollment.query.filter_by(user_id=user_id)
        
        # Appliquer les filtres
        if search:
            query = query.join(Course).filter(
                (Course.title.ilike(f'%{search}%')) | 
                (Course.description.ilike(f'%{search}%'))
            )
        
        if category:
            query = query.join(Course).filter(Course.category == category)
        
        if status:
            query = query.filter(Enrollment.status == status)
        
        enrollments = query.all()
        courses = [e.to_dict() for e in enrollments]
        
        # Statistiques
        all_enrollments = Enrollment.query.filter_by(user_id=user_id).all()
        stats = {
            "totalCourses": len(all_enrollments),
            "inProgress": len([e for e in all_enrollments if e.status == 'in-progress']),
            "completed": len([e for e in all_enrollments if e.status == 'completed']),
            "notStarted": len([e for e in all_enrollments if e.status == 'not-started']),
            "averageProgress": int(sum([e.progress for e in all_enrollments]) / len(all_enrollments)) if all_enrollments else 0
        }
        
        return jsonify({"courses": courses, "stats": stats}), 200
        
    except Exception as e:
        return jsonify({"status": 500, "message": str(e)}), 500


@courses_bp.route('/<int:course_id>', methods=['GET'])
@jwt_required()
def get_course_detail(course_id):
    """
    GET /api/courses/<course_id>
    Récupère le détail complet d'un cours
    """
    try:
        user_id = get_jwt_identity()
        
        course = Course.query.get(course_id)
        if not course:
            return jsonify({"status": 404, "message": "Cours non trouvé"}), 404
        
        # Vérifier l'inscription
        enrollment = Enrollment.query.filter_by(user_id=user_id, course_id=course_id).first()
        if not enrollment:
            return jsonify({"status": 403, "message": "Vous n'êtes pas inscrit à ce cours"}), 403
        
        # Mettre à jour la dernière visite
        enrollment.last_accessed = datetime.utcnow()
        db.session.commit()
        
        # Récupérer les chapitres avec leçons
        chapters = Chapter.query.filter_by(course_id=course_id).order_by(Chapter.order).all()
        chapters_data = []
        total_lessons = 0
        completed_lessons = 0
        
        for chapter in chapters:
            chapter_dict = chapter.to_dict(include_lessons=True, user_id=user_id)
            chapters_data.append(chapter_dict)
            total_lessons += chapter_dict['lessonsCount']
            completed_lessons += chapter_dict.get('completedLessons', 0)
        
        response_data = {
            "id": course.id,
            "title": course.title,
            "category": course.category,
            "description": course.description,
            "instructor": course.instructor,
            "duration": course.duration,
            "level": course.level,
            "rating": course.rating,
            "totalLessons": total_lessons,
            "completedLessons": completed_lessons,
            "progress": enrollment.progress,
            "chapters": chapters_data
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({"status": 500, "message": str(e)}), 500


@courses_bp.route('/<int:course_id>/enroll', methods=['POST'])
@jwt_required()
def enroll_course(course_id):
    """
    POST /api/courses/<course_id>/enroll
    Inscrit l'utilisateur à un cours
    """
    try:
        user_id = get_jwt_identity()
        
        course = Course.query.get(course_id)
        if not course:
            return jsonify({"status": 404, "message": "Cours non trouvé"}), 404
        
        # Vérifier si déjà inscrit
        existing = Enrollment.query.filter_by(user_id=user_id, course_id=course_id).first()
        if existing:
            return jsonify({"status": 409, "message": "Vous êtes déjà inscrit à ce cours"}), 409
        
        # Créer l'inscription
        enrollment = Enrollment(user_id=user_id, course_id=course_id)
        db.session.add(enrollment)
        
        # Incrémenter le compteur
        course.students_count += 1
        db.session.commit()
        
        return jsonify({"message": "Inscription réussie", "enrollment": enrollment.to_dict()}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": 500, "message": str(e)}), 500


@courses_bp.route('/<int:course_id>/progress', methods=['GET'])
@jwt_required()
def get_course_progress(course_id):
    """
    GET /api/courses/<course_id>/progress
    Récupère la progression détaillée
    """
    try:
        user_id = get_jwt_identity()
        
        enrollment = Enrollment.query.filter_by(user_id=user_id, course_id=course_id).first()
        if not enrollment:
            return jsonify({"status": 404, "message": "Inscription non trouvée"}), 404
        
        return jsonify({
            "progress": enrollment.progress,
            "status": enrollment.status,
            "totalLessons": enrollment.get_total_lessons(),
            "completedLessons": enrollment.get_completed_lessons(),
            "lastAccessed": enrollment.last_accessed.isoformat() if enrollment.last_accessed else None,
            "enrolledAt": enrollment.enrolled_at.isoformat() if enrollment.enrolled_at else None,
            "completedAt": enrollment.completed_at.isoformat() if enrollment.completed_at else None
        }), 200
        
    except Exception as e:
        return jsonify({"status": 500, "message": str(e)}), 500


@courses_bp.route('/lessons/<int:lesson_id>/complete', methods=['POST'])
@jwt_required()
def complete_lesson(lesson_id):
    """
    POST /api/courses/lessons/<lesson_id>/complete
    Marque une leçon comme complétée
    """
    try:
        user_id = get_jwt_identity()
        
        lesson = Lesson.query.get(lesson_id)
        if not lesson:
            return jsonify({"status": 404, "message": "Leçon non trouvée"}), 404
        
        # Rechercher ou créer la progression
        progress = LessonProgress.query.filter_by(user_id=user_id, lesson_id=lesson_id).first()
        
        if not progress:
            progress = LessonProgress(user_id=user_id, lesson_id=lesson_id)
            db.session.add(progress)
        
        # Marquer comme complétée
        progress.mark_as_completed()
        
        return jsonify({
            "message": "Leçon complétée",
            "progress": {
                "isCompleted": progress.is_completed,
                "completedAt": progress.completed_at.isoformat() if progress.completed_at else None
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": 500, "message": str(e)}), 500


@courses_bp.route('/all', methods=['GET'])
@jwt_required()
def get_all_courses():
    """
    GET /api/courses/all
    Récupère tous les cours disponibles (pour inscription)
    """
    try:
        courses = Course.query.all()
        return jsonify([course.to_dict() for course in courses]), 200
    except Exception as e:
        return jsonify({"status": 500, "message": str(e)}), 500