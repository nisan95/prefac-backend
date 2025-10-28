# ============================================
# LANCER L'APPLICATION
# ============================================
from app import create_app
import os

# Créer l'application
app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'True') == 'True'
    
    print(f"🚀 Serveur démarré sur http://localhost:{port}")
    print(f"📊 Base de données: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)