from flask import Flask, render_template
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize MongoDB
mongo = PyMongo()

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Configure app
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
    app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://localhost:27017/ahp_db')
    
    # Initialize MongoDB with app
    mongo.init_app(app)
    
    # Register blueprints
    from .routes import main_bp
    app.register_blueprint(main_bp)
    
    # Register error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error.html', message='Trang không tồn tại'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('error.html', message='Lỗi máy chủ nội bộ'), 500
    
    return app
