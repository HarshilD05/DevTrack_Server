# app.py
from flask import Flask
import os

# Initialize Flask app
app = Flask(__name__)

# Set App configurations
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["UPLOAD_FOLDER"] = os.getenv("UPLOAD_FOLDER", "./uploads")

# Ensure upload folder exists
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Import and register blueprints
from routes.auth_routes import auth_bp
from routes.project_routes import project_bp
from routes.task_routes import task_bp
from routes.user_routes import user_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(project_bp, url_prefix='/api/projects')
app.register_blueprint(task_bp, url_prefix='/api/tasks')
app.register_blueprint(user_bp, url_prefix='/api/users')

@app.route('/', methods=['GET'])
def index():
    return "Welcome to the Project Management API!"

if __name__ == "__main__":
    app.run(debug=True)