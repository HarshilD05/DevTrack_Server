# controllers/task_controller.py
from models.task import TaskModel
from models.project import ProjectModel
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId

class TaskController:
    @staticmethod
    @jwt_required()
    def create_task(project_id):
        current_user_id = get_jwt_identity()
        
        # Get project
        project = ProjectModel.get_project(project_id)
        if not project:
            return jsonify({"error": "Project not found"}), 404
        
        # Check if user is admin
        if ObjectId(current_user_id) not in project["admin_users"]:
            return jsonify({"error": "You don't have permission to create tasks"}), 403
        
        # Process form data
        title = request.form.get("title")
        description = request.form.get("description")
        status = request.form.get("status", "Assigned")
        assigned_users = request.form.getlist("assigned_users")
        files = request.files.getlist("files") if "files" in request.files else None
        
        # Validate input data
        if not all([title, description]) or not assigned_users:
            return jsonify({"error": "Missing required fields"}), 400
        
        # Create task
        task_id = TaskModel.create_task(project_id, title, description, assigned_users, status, files)
        if not task_id:
            return jsonify({"error": "Failed to create task"}), 500
        
        return jsonify({"message": "Task created successfully", "task_id": task_id}), 201
    
    @staticmethod
    @jwt_required()
    def get_task(task_id):
        current_user_id = get_jwt_identity()
        
        # Get task
        task = TaskModel.get_task(task_id)
        if not task:
            return jsonify({"error": "Task not found"}), 404
        
        # Get project
        project = ProjectModel.get_project(str(task["project_id"]))
        if not project:
            return jsonify({"error": "Project not found"}), 404
        
        # Check if user has access to project
        user_id_obj = ObjectId(current_user_id)
        if (user_id_obj not in project["admin_users"] and 
            user_id_obj not in project["participants"] and 
            user_id_obj not in task["assigned_users"]):
            return jsonify({"error": "You don't have access to this task"}), 403
        
        # Convert ObjectId to string
        task["_id"] = str(task["_id"])
        task["project_id"] = str(task["project_id"])
        task["assigned_users"] = [str(user_id) for user_id in task["assigned_users"]]
        
        # Format file info
        for file in task.get("files", []):
            file.pop("path", None)  # Remove server path for security
        
        return jsonify({"task": task}), 200
    
    @staticmethod
    @jwt_required()
    def get_project_tasks(project_id):
        current_user_id = get_jwt_identity()
        
        # Get project
        project = ProjectModel.get_project(project_id)
        if not project:
            return jsonify({"error": "Project not found"}), 404
        
        # Check if user has access to project
        user_id_obj = ObjectId(current_user_id)
        if (user_id_obj not in project["admin_users"] and 
            user_id_obj not in project["participants"]):
            return jsonify({"error": "You don't have access to this project"}), 403
        
        # Get tasks
        tasks = TaskModel.get_project_tasks(project_id)
        
        # Convert ObjectId to string
        for task in tasks:
            task["_id"] = str(task["_id"])
            task["project_id"] = str
            task["project_id"] = str(task["project_id"])
            task["assigned_users"] = [str(user_id) for user_id in task["assigned_users"]]
            
            # Format file info
            for file in task.get("files", []):
                file.pop("path", None)  # Remove server path for security
        
        return jsonify({"tasks": tasks}), 200
    
    @staticmethod
    @jwt_required()
    def get_user_tasks():
        current_user_id = get_jwt_identity()
        
        # Get tasks
        tasks = TaskModel.get_user_tasks(current_user_id)
        
        # Convert ObjectId to string
        for task in tasks:
            task["_id"] = str(task["_id"])
            task["project_id"] = str(task["project_id"])
            task["assigned_users"] = [str(user_id) for user_id in task["assigned_users"]]
            
            # Format file info
            for file in task.get("files", []):
                file.pop("path", None)  # Remove server path for security
        
        return jsonify({"tasks": tasks}), 200
    
    @staticmethod
    @jwt_required()
    def update_task(task_id):
        current_user_id = get_jwt_identity()
        
        # Get task
        task = TaskModel.get_task(task_id)
        if not task:
            return jsonify({"error": "Task not found"}), 404
        
        # Get project
        project = ProjectModel.get_project(str(task["project_id"]))
        if not project:
            return jsonify({"error": "Project not found"}), 404
        
        # Check if user is admin
        is_admin = ObjectId(current_user_id) in project["admin_users"]
        
        # Process form data
        update_data = {}
        
        if "title" in request.form:
            update_data["title"] = request.form.get("title")
        
        if "description" in request.form:
            update_data["description"] = request.form.get("description")
        
        # Only admins can update status directly
        if "status" in request.form and is_admin:
            update_data["status"] = request.form.get("status")
        
        # Only admins can update assigned users
        if "assigned_users" in request.form and is_admin:
            update_data["assigned_users"] = request.form.getlist("assigned_users")
        
        # Get files
        files = request.files.getlist("files") if "files" in request.files else None
        
        # Check if there's anything to update
        if not update_data and not files:
            return jsonify({"error": "No update data provided"}), 400
        
        # Check if user has permission to update
        if not is_admin and ObjectId(current_user_id) not in task["assigned_users"]:
            return jsonify({"error": "You don't have permission to update this task"}), 403
        
        # Update task
        if not TaskModel.update_task(task_id, update_data, files):
            return jsonify({"error": "Failed to update task"}), 500
        
        return jsonify({"message": "Task updated successfully"}), 200
    
    @staticmethod
    @jwt_required()
    def request_status_update(task_id):
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate input data
        if "status" not in data:
            return jsonify({"error": "Missing status field"}), 400
        
        new_status = data["status"]
        
        # Request status update
        if not TaskModel.request_status_update(task_id, new_status, current_user_id):
            return jsonify({"error": "Failed to request status update"}), 500
        
        return jsonify({"message": "Status update requested successfully"}), 200
    
    @staticmethod
    @jwt_required()
    def approve_status_change(request_id):
        current_user_id = get_jwt_identity()
        
        # Approve status change
        if not TaskModel.approve_status_change(request_id, current_user_id):
            return jsonify({"error": "Failed to approve status change"}), 500
        
        return jsonify({"message": "Status change approved successfully"}), 200
    
    @staticmethod
    @jwt_required()
    def delete_task(task_id):
        current_user_id = get_jwt_identity()
        
        # Get task
        task = TaskModel.get_task(task_id)
        if not task:
            return jsonify({"error": "Task not found"}), 404
        
        # Get project
        project = ProjectModel.get_project(str(task["project_id"]))
        if not project:
            return jsonify({"error": "Project not found"}), 404
        
        # Check if user is admin
        if ObjectId(current_user_id) not in project["admin_users"]:
            return jsonify({"error": "You don't have permission to delete this task"}), 403
        
        # Delete task
        if not TaskModel.delete_task(task_id):
            return jsonify({"error": "Failed to delete task"}), 500
        
        return jsonify({"message": "Task deleted successfully"}), 200

