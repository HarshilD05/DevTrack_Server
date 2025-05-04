# controllers/user_controller.py
from models.user import UserModel
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

class UserController:
    @staticmethod
    @jwt_required()
    def get_profile():
        current_user_id = get_jwt_identity()
        
        # Get user
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
