# routes/auth_routes.py
from flask import Blueprint
from controllers.auth_controller import AuthController

auth_bp = Blueprint('auth', __name__)

auth_bp.route('/register', methods=['POST'])(AuthController.register)
auth_bp.route('/login', methods=['POST'])(AuthController.login)
auth_bp.route('/verify-token', methods=['GET'])(AuthController.verify_token)
auth_bp.route('/change-password', methods=['POST'])(AuthController.change_password)