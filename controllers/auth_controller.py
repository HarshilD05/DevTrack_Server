# controllers/auth_controller.py

from models.user import UserModel
from flask import request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
import re
from datetime import timedelta

class AuthController:
    @staticmethod
    def register():
        data = request.get_json()

        req_fields = ["name", "username", "email", "password", "accountType", "institution"]
        
        # Validate input data
        if not all(key in data for key in req_fields):
            print("Missing required fields")
            return jsonify({"error": "Missing required fields"}), 400
        
        name = data.get("name", None)
        institution = data.get("institution", None)
        accType = data.get("accountType", None)
        username = data["username"]
        email = data.get("email", None)
        password = data["password"]
        
        # Validate email format
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return jsonify({"error": "Invalid email format"}), 400
        
        # Validate password strength
        if len(password) < 8:
            return jsonify({"error": "Password must be at least 8 characters long"}), 400
        
        # Create user
        user_id = UserModel.create_user(name, username, email, password, accType, institution)
        if not user_id:
            return jsonify({"error": "Username or email already exists"}), 400
        
        return jsonify({"message": "User registered successfully", "user_id": user_id}), 201
    
    @staticmethod
    def login():
        data = request.get_json()

        req_fields = ["username", "password"]
        
        # Validate input data
        if not all(key in data for key in req_fields):
            return jsonify({"error": "Missing username or password"}), 400
        
        username = data["username"]
        password = data["password"]
        
        # Authenticate user
        user = UserModel.authenticate_user(username, password)
        if not user:
            return jsonify({"error": "Invalid username or password"}), 401
        
        # Create access token
        access_token = create_access_token(identity=str(user["_id"]), expires_delta=timedelta(hours=1))
        
        return jsonify({
            "message": "Login successful",
            "user": {
                "id": str(user["_id"]),
                "username": user["username"],
                "email": user["email"],
                "verified": user["verified"]
            },
            "access_token": access_token
        }), 200
    
    @staticmethod
    @jwt_required()
    def verify_token():
        current_user_id = get_jwt_identity()
        user = UserModel.get_user_by_id(current_user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify({
            "user": {
                "id": str(user["_id"]),
                "username": user["username"],
                "email": user["email"],
                "verified": user["verified"]
            }
        }), 200
    
    @staticmethod
    @jwt_required()
    def change_password():
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate input data
        if not all(key in data for key in ["current_password", "new_password"]):
            return jsonify({"error": "Missing current or new password"}), 400
        
        current_password = data["current_password"]
        new_password = data["new_password"]
        
        # Validate new password strength
        if len(new_password) < 8:
            return jsonify({"error": "New password must be at least 8 characters long"}), 400
        
        # Get user
        user = UserModel.get_user_by_id(current_user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Verify current password
        if not UserModel.authenticate_user(user["email"], current_password):
            return jsonify({"error": "Current password is incorrect"}), 401
        
        # Update password
        if not UserModel.update_password(current_user_id, new_password):
            return jsonify({"error": "Failed to update password"}), 500
        
        return jsonify({"message": "Password updated successfully"}), 200