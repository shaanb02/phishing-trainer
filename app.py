import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging for debugging and monitoring
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    """Base class for SQLAlchemy models"""
    pass

# Initialize SQLAlchemy with custom base class
db = SQLAlchemy(model_class=Base)

# Create the Flask application instance
app = Flask(__name__)

# Set secret key from environment variable for session security
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Configure proxy fix for proper URL generation behind reverse proxies
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure SQLite database (can be changed to PostgreSQL/MySQL in production)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:///phishing_training.db"
)
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the database with the app
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect to login page if not authenticated

@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login sessions"""
    from models import AdminUser
    return AdminUser.query.get(int(user_id))

# Import routes and models after app initialization to avoid circular imports
with app.app_context():
    # Import models to ensure tables are created
    import models  # noqa: F401
    # Import routes to register them with the app
    import routes  # noqa: F401
    
    # Create all database tables
    db.create_all()
    
    logging.info("Database tables created successfully")
