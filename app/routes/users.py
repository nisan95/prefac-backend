"""
Users Routes
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models.user import User
from ..models.enrollment import Enrollment
from ..models.lesson_progress import LessonProgress

users_bp = Blueprint('users', __name__, url_prefix='/api/users')

@users_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """
    GET /api/users/profile
    Récupère le profil de l'utilisateur connecté
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({"status": 404, "message": "Utilisateur non trouvé"}), 404
        
        return jsonify(user.to_dict()), 200
    except Exception as e:
        return jsonify({"status": 500, "message": str(e)}), 500


@users_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """
    PUT /api/users/profile
    Met à jour le profil de l'utilisateur
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({"status": 404, "message": "Utilisateur non trouvé"}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({"status": 400, "message": "Aucune donnée fournie"}), 400
        
        # Mise à jour des champs
        if 'name' in data:
            name = data['name'].strip()
            if len(name) >= 2:
                user.name = name
        
        if 'phone' in data:
            user.phone = data['phone'].strip() if data['phone'] else None
        
        if 'location' in data:
            user.location = data['location'].strip() if data['location'] else None
        
        if 'bio' in data:
            bio = data['bio'].strip() if data['bio'] else None
            if bio and len(bio) <= 500:
                user.bio = bio
        
        db.session.commit()
        return jsonify(user.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": 500, "message": str(e)}), 500


@users_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_user_stats():
    """
    GET /api/users/stats
    Récupère les statistiques de l'utilisateur
    """
    try:
        user_id = get_jwt_identity()
        
        enrollments = Enrollment.query.filter_by(user_id=user_id).all()
        
        courses_enrolled = len(enrollments)
        courses_completed = len([e for e in enrollments if e.status == 'completed'])
        average_progress = int(sum([e.progress for e in enrollments]) / courses_enrolled) if courses_enrolled > 0 else 0
        
        completed_lessons = LessonProgress.query.filter_by(user_id=user_id, is_completed=True).count()
        hours_learned = int(completed_lessons * 0.5)  # 30 min par leçon
        
        stats = {
            "coursesEnrolled": courses_enrolled,
            "coursesCompleted": courses_completed,
            "averageProgress": average_progress,
            "hoursLearned": hours_learned,
            "certificatesEarned": courses_completed,
            "currentStreak": 7  # TODO: implémenter la vraie logique
        }
        
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({"status": 500, "message": str(e)}), 500