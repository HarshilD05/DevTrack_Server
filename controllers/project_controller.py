# controllers/project_controller.py
from models.project import ProjectModel
from models.user import UserModel
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId

class ProjectController:
    @staticmethod
    @jwt_required()
    def create_project():
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate input data
        if not all(key in data for key in ["name", "description"]):
            return jsonify({"error": "Missing required fields"}), 400
        
        name = data["name"]
        description = data["description"]
        
        # Create project
        project_id = ProjectModel.create_project(name, description, current_user_id)
        if not project_id:
            return jsonify({"error": "Failed to create project"}), 500
        
        return jsonify({"message": "Project created successfully", "project_id": project_id}), 201
    
    @staticmethod
    @jwt_required()
    def get_project(project_id):
        current_user_id = get_jwt_identity()
        
        # Get project
        project = ProjectModel.get_project(project_id)
        if not project:
            return jsonify({"error": "Project not found"}), 404
        
        # Check if user has access to project
        user_id_obj = ObjectId(current_user_id)
        if (user_id_obj != project["creator_id"] and 
            user_id_obj not in project["admin_users"] and 
            user_id_obj not in project["participants"]):
            return jsonify({"error": "You don't have access to this project"}), 403
        
        # Convert ObjectId to string
        project["_id"] = str(project["_id"])
        project["creator_id"] = str(project["creator_id"])
        project["admin_users"] = [str(user_id) for user_id in project["admin_users"]]
        project["participants"] = [str(user_id) for user_id in project["participants"]]
        
        return jsonify({"project": project}), 200
    
    @staticmethod
    @jwt_required()
    def get_user_projects():
        current_user_id = get_jwt_identity()
        
        # Get user projects
        projects = ProjectModel.get_user_projects(current_user_id)
        
        # Convert ObjectId to string
        for project in projects:
            project["_id"] = str(project["_id"])
            project["creator_id"] = str(project["creator_id"])
            project["admin_users"] = [str(user_id) for user_id in project["admin_users"]]
            project["participants"] = [str(user_id) for user_id in project["participants"]]
        
        return jsonify({"projects": projects}), 200
    
    @staticmethod
    @jwt_required()
    def update_project(project_id):
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Get project
        project = ProjectModel.get_project(project_id)
        if not project:
            return jsonify({"error": "Project not found"}), 404
        
        # Check if user is admin
        if ObjectId(current_user_id) not in project["admin_users"]:
            return jsonify({"error": "You don't have permission to update this project"}), 403
        
        # Only allow specific fields to be updated
        allowed_fields = ["name", "description"]
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        # Update project
        if not ProjectModel.update_project(project_id, update_data):
            return jsonify({"error": "Failed to update project"}), 500
        
        return jsonify({"message": "Project updated successfully"}), 200
    
    @staticmethod
    @jwt_required()
    def add_admin(project_id):
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate input data
        if "user_email" not in data:
            return jsonify({"error": "Missing user email"}), 400
        
        # Get project
        project = ProjectModel.get_project(project_id)
        if not project:
            return jsonify({"error": "Project not found"}), 404
        
        # Check if current user is admin
        if ObjectId(current_user_id) not in project["admin_users"]:
            return jsonify({"error": "You don't have permission to add admins"}), 403
        
        # Get user to add
        user = UserModel.get_user_by_email(data["user_email"])
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Add user as admin
        if not ProjectModel.add_admin(project_id, str(user["_id"])):
            return jsonify({"error": "Failed to add admin"}), 500
        
        return jsonify({"message": "Admin added successfully"}), 200
    
    @staticmethod
    @jwt_required()
    def add_participant(project_id):
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate input data
        if "user_email" not in data:
            return jsonify({"error": "Missing user email"}), 400
        
        # Get project
        project = ProjectModel.get_project(project_id)
        if not project:
            return jsonify({"error": "Project not found"}), 404
        
        # Check if current user is admin
        if ObjectId(current_user_id) not in project["admin_users"]:
            return jsonify({"error": "You don't have permission to add participants"}), 403
        
        # Get user to add
        user = UserModel.get_user_by_email(data["user_email"])
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Add user as participant
        if not ProjectModel.add_participant(project_id, str(user["_id"])):
            return jsonify({"error": "Failed to add participant"}), 500
        
        return jsonify({"message": "Participant added successfully"}), 200
    
    @staticmethod
    @jwt_required()
    def update_stages(project_id):
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate input data
        if "stages" not in data or not isinstance(data["stages"], list):
            return jsonify({"error": "Missing or invalid stages"}), 400
        
        # Get project
        project = ProjectModel.get_project(project_id)
        if not project:
            return jsonify({"error": "Project not found"}), 404
        
        # Check if current user is admin
        if ObjectId(current_user_id) not in project["admin_users"]:
            return jsonify({"error": "You don't have permission to update stages"}), 403
        
        # Update stages
        if not ProjectModel.update_stages(project_id, data["stages"]):
            return jsonify({"error": "Failed to update stages"}), 500
        
        return jsonify({"message": "Stages updated successfully"}), 200
    
    @staticmethod
    @jwt_required()
    def delete_project(project_id):
        current_user_id = get_jwt_identity()
        
        # Get project
        project = ProjectModel.get_project(project_id)
        if not project:
            return jsonify({"error": "Project not found"}), 404
        
        # Check if current user is creator
        if project["creator_id"] != ObjectId(current_user_id):
            return jsonify({"error": "Only the project creator can delete it"}), 403
        
        # Delete project
        if not ProjectModel.delete_project(project_id):
            return jsonify({"error": "Failed to delete project"}), 500
        
        return jsonify({"message": "Project deleted successfully"}), 200

