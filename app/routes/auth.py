"""
Authentication Routes
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
from ..extensions import db  
from ..models.user import User  
import re

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

def validate_email(email):
    """Valide un email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    POST /api/auth/register
    Inscription d'un nouvel utilisateur
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"status": 400, "message": "Aucune donnée fournie", "errors": {}}), 400
        
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # Validations
        errors = {}
        
        if not name or len(name) < 2:
            errors['name'] = "Le nom doit contenir au moins 2 caractères"
        
        if not validate_email(email):
            errors['email'] = "Adresse email invalide"
        
        if not password or len(password) < 6:
            errors['password'] = "Le mot de passe doit contenir au moins 6 caractères"
        
        if errors:
            return jsonify({"status": 400, "message": "Données invalides", "errors": errors}), 400
        
        # Vérifier si l'email existe
        if User.query.filter_by(email=email).first():
            return jsonify({"status": 409, "message": "Cet email est déjà utilisé", "errors": {"email": "Email déjà enregistré"}}), 409
        
        # Créer l'utilisateur
        user = User(name=name, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Créer le token JWT
        access_token = create_access_token(identity=user.id, expires_delta=timedelta(days=7))
        
        return jsonify({"token": access_token, "user": user.to_dict()}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": 500, "message": "Erreur serveur", "errors": {"server": str(e)}}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    POST /api/auth/login
    Connexion d'un utilisateur
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"status": 400, "message": "Aucune donnée fournie", "errors": {}}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        keep_connected = data.get('keepConnected', False)
        
        if not email or not password:
            return jsonify({"status": 400, "message": "Email et mot de passe requis", "errors": {}}), 400
        
        # Rechercher l'utilisateur
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({"status": 401, "message": "Email ou mot de passe incorrect", "errors": {}}), 401
        
        # Créer le token JWT
        expires = timedelta(days=30) if keep_connected else timedelta(days=7)
        access_token = create_access_token(identity=user.id, expires_delta=expires)
        
        return jsonify({"token": access_token, "user": user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({"status": 500, "message": "Erreur serveur", "errors": {"server": str(e)}}), 500


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    POST /api/auth/logout
    Déconnexion (côté client supprime le token)
    """
    return jsonify({"message": "Déconnexion réussie"}), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    GET /api/auth/me
    Récupère l'utilisateur connecté
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({"status": 404, "message": "Utilisateur non trouvé"}), 404
        
        return jsonify(user.to_dict()), 200
    except Exception as e:
        return jsonify({"status": 500, "message": str(e)}), 500