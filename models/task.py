# models/task_model.py
from config.db import db
from bson import ObjectId
from datetime import datetime
import os
from flask import current_app
import uuid

class TaskModel:
    collection = db["Tasks"]

    @staticmethod
    def create_task(project_id, title, description, assigned_users, status="Assigned", files=None):
        # Get project to verify status is valid
        project = db.projects.find_one({"_id": ObjectId(project_id)})
        if not project or status not in project["stages"]:
            return None
        
        # Convert assigned_users to ObjectId
        assigned_users_obj = [ObjectId(user_id) for user_id in assigned_users]
        
        # Create task
        task = {
            "project_id": ObjectId(project_id),
            "title": title,
            "description": description,
            "assigned_users": [assigned_users_obj],
            "status": status,
            "files": [],
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "status_history": [
                {
                    "status": status,
                    "timestamp": datetime.now()
                }
            ]
        }
        
        # Save files if any
        if files:
            saved_files = []
            for file in files:
                filename = str(uuid.uuid4()) + "_" + file.filename
                file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
                file.save(file_path)
                saved_files.append({
                    "filename": file.filename,
                    "stored_name": filename,
                    "path": file_path,
                    "uploaded_at": datetime.now()
                })
            task["files"] = saved_files
        
        result = TaskModel.collection.insert_one(task)
        return str(result.inserted_id)
    
    @staticmethod
    def get_task(task_id):
        try:
            return TaskModel.collection.find_one({"_id": ObjectId(task_id)})
        except:
            return None
    
    @staticmethod
    def get_project_tasks(project_id):
        return list(TaskModel.collection.find({"project_id": ObjectId(project_id)}))
    
    @staticmethod
    def get_user_tasks(user_id):
        return list(TaskModel.collection.find({"assigned_users": ObjectId(user_id)}))
    
    @staticmethod
    def update_task(task_id, update_data, files=None):
        task = TaskModel.collection.find_one({"_id": ObjectId(task_id)})
        if not task:
            return False
        
        # Handle status change
        if "status" in update_data and update_data["status"] != task["status"]:
            # Get project to verify status is valid
            project = db.projects.find_one({"_id": task["project_id"]})
            if not project or update_data["status"] not in project["stages"]:
                return False
            
            # Add to status history
            update_data["status_history"] = task["status_history"] + [
                {
                    "status": update_data["status"],
                    "timestamp": datetime.now()
                }
            ]
        
        # Handle assigned users
        if "assigned_users" in update_data:
            update_data["assigned_users"] = [ObjectId(user_id) for user_id in update_data["assigned_users"]]
        
        # Handle files
        if files:
            saved_files = task.get("files", [])
            for file in files:
                filename = str(uuid.uuid4()) + "_" + file.filename
                file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
                file.save(file_path)
                saved_files.append({
                    "filename": file.filename,
                    "stored_name": filename,
                    "path": file_path,
                    "uploaded_at": datetime.now()
                })
            update_data["files"] = saved_files
        
        update_data["updated_at"] = datetime.now()
        
        result = TaskModel.collection.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    @staticmethod
    def request_status_update(task_id, new_status, user_id):
        task = TaskModel.collection.find_one({"_id": ObjectId(task_id)})
        if not task:
            return False
        
        # Check if user is assigned to task
        if ObjectId(user_id) not in task["assigned_users"]:
            return False
        
        # Get project to verify status is valid
        project = db.projects.find_one({"_id": task["project_id"]})
        if not project or new_status not in project["stages"]:
            return False
        
        # Create status change request
        request = {
            "task_id": ObjectId(task_id),
            "project_id": task["project_id"],
            "requested_by": ObjectId(user_id),
            "current_status": task["status"],
            "requested_status": new_status,
            "created_at": datetime.now(),
            "status": "pending"  # pending, approved, rejected
        }
        
        db.status_change_requests.insert_one(request)
        return True
    
    @staticmethod
    def approve_status_change(request_id, admin_id):
        # Find request
        request = db.status_change_requests.find_one({"_id": ObjectId(request_id)})
        if not request or request["status"] != "pending":
            return False
        
        # Check if admin is project admin
        project = db.projects.find_one({"_id": request["project_id"]})
        if not project or ObjectId(admin_id) not in project["admin_users"]:
            return False
        
        # Update task status
        task_id = request["task_id"]
        new_status = request["requested_status"]
        
        task = TaskModel.collection.find_one({"_id": task_id})
        status_history = task["status_history"] + [
            {
                "status": new_status,
                "timestamp": datetime.now()
            }
        ]
        
        # Update task
        TaskModel.collection.update_one(
            {"_id": task_id},
            {
                "$set": {
                    "status": new_status,
                    "status_history": status_history,
                    "updated_at": datetime.now()
                }
            }
        )
        
        # Update request
        db.status_change_requests.update_one(
            {"_id": ObjectId(request_id)},
            {
                "$set": {
                    "status": "approved",
                    "approved_by": ObjectId(admin_id),
                    "approved_at": datetime.now()
                }
            }
        )
        
        return True
    
    @staticmethod
    def delete_task(task_id):
        # Get task to delete files
        task = TaskModel.collection.find_one({"_id": ObjectId(task_id)})
        if task and "files" in task:
            for file in task["files"]:
                try:
                    os.remove(file["path"])
                except:
                    pass
        
        # Delete task
        result = TaskModel.collection.delete_one({"_id": ObjectId(task_id)})
        return result.deleted_count > 0