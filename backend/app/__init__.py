import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from flask_cors import CORS
from .models import db

# Load environment variables from .env file
load_dotenv()

def create_app(config_override=None):
    app = Flask(__name__)
    CORS(app)

    # Config would normally be in a config object or .env
    db_uri = os.environ.get('DATABASE_URL', 'sqlite:///medlio.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'super-secret-key')

    if config_override:
        app.config.update(config_override)

    db.init_app(app)
    JWTManager(app)

    with app.app_context():
        try:
            db.create_all() # Ensure tables are created
        except Exception as e:
            app.logger.warning(f"Database initialization check warning: {e}")
        # Import routes here to avoid circular imports
        from .routes.auth_routes import auth_bp
        from .routes.user_routes import user_bp
        from .routes.admin_routes import admin_bp
        app.register_blueprint(auth_bp)
        app.register_blueprint(user_bp)
        app.register_blueprint(admin_bp)

    from flask import send_from_directory
    @app.route('/uploads/<filename>')
    def serve_upload(filename):
        uploads_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'uploads')
        return send_from_directory(uploads_dir, filename)

    return app
