"""
Dashboard Routes
"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.user import User
from ..models.enrollment import Enrollment
from ..models.lesson_progress import LessonProgress

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api')

@dashboard_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    """
    GET /api/dashboard
    Récupère toutes les données du tableau de bord
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({"status": 404, "message": "Utilisateur non trouvé"}), 404
        
        # Récupérer les inscriptions
        enrollments = Enrollment.query.filter_by(user_id=user_id).all()
        
        # Calculer les statistiques
        courses_enrolled = len(enrollments)
        courses_completed = len([e for e in enrollments if e.status == 'completed'])
        average_progress = int(sum([e.progress for e in enrollments]) / courses_enrolled) if courses_enrolled > 0 else 0
        
        completed_lessons = LessonProgress.query.filter_by(user_id=user_id, is_completed=True).count()
        hours_learned = int(completed_lessons * 0.5)
        
        stats = {
            "coursesEnrolled": courses_enrolled,
            "coursesCompleted": courses_completed,
            "averageProgress": average_progress,
            "hoursLearned": hours_learned,
            "certificatesEarned": courses_completed,
            "currentStreak": 7
        }
        
        # Récupérer les 3 cours les plus récents
        recent_enrollments = Enrollment.query.filter_by(user_id=user_id).order_by(
            Enrollment.last_accessed.desc()
        ).limit(3).all()
        
        recent_courses = [e.to_dict() for e in recent_enrollments]
        
        return jsonify({
            "user": user.to_dict(),
            "stats": stats,
            "recentCourses": recent_courses
        }), 200
        
    except Exception as e:
        return jsonify({"status": 500, "message": str(e)}), 500