"""
Prefac Backend - Application Factory
"""
from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    """Factory pour créer l'application Flask"""
    
    app = Flask(__name__)
    
    # ============================================
    # CONFIGURATION
    # ============================================
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///prefac.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = os.getenv('DEBUG', 'False') == 'True'
    
    # Security
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
    
    # JWT Configuration
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_HEADER_TYPE'] = 'Bearer'
    
    # ============================================
    # INITIALISER LES EXTENSIONS
    # ============================================
    from .extensions import db
    
    db.init_app(app)
    migrate = Migrate(app, db)
    jwt = JWTManager(app)
    bcrypt = Bcrypt(app)
    
    # CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173", "http://localhost:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
        }
    })
    
    # ============================================
    # GESTIONNAIRES D'ERREURS JWT
    # ============================================
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'status': 401, 'message': 'Token expiré'}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'status': 401, 'message': 'Token invalide'}), 401
    
    @jwt.unauthorized_loader
    def unauthorized_callback(error):
        return jsonify({'status': 401, 'message': 'Token manquant'}), 401
    
    # ============================================
    # GESTIONNAIRES D'ERREURS GLOBAUX
    # ============================================
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"status": 404, "message": "Ressource non trouvée"}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({"status": 500, "message": "Erreur serveur"}), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        db.session.rollback()
        return jsonify({"status": 500, "message": str(error)}), 500
    
    # ============================================
    # ROUTES DE BASE
    # ============================================
    @app.route('/', methods=['GET'])
    def index():
        return jsonify({
            "message": "Prefac API - Backend fonctionnel ✅",
            "version": "1.0.0",
            "endpoints": {
                "auth": "/api/auth/*",
                "users": "/api/users/*",
                "courses": "/api/courses/*",
                "dashboard": "/api/dashboard"
            }
        }), 200
    
    @app.route('/api/health', methods=['GET'])
    def health():
        try:
            db.session.execute(db.text('SELECT 1'))
            return jsonify({"status": "healthy", "database": "connected"}), 200
        except:
            return jsonify({"status": "unhealthy", "database": "disconnected"}), 500
    
    # ============================================
    # ENREGISTRER LES BLUEPRINTS
    # ============================================
    with app.app_context():
        from .routes.auth import auth_bp
        from .routes.users import users_bp
        from .routes.courses import courses_bp
        from .routes.dashboard import dashboard_bp
        
        app.register_blueprint(auth_bp)
        app.register_blueprint(users_bp)
        app.register_blueprint(courses_bp)
        app.register_blueprint(dashboard_bp)
        
        # Créer les tables
        db.create_all()
        print("✅ Base de données initialisée")
    
    return app