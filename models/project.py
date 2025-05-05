# models/project_model.py
from config.db import db
from bson import ObjectId
from datetime import datetime

class ProjectModel:
    collection = db["Projects"]

    @staticmethod
    def create_project(name, description, creator_id):
        project = {
            "name": name,
            "description": description,
            "creator_id": ObjectId(creator_id),
            "admin_users": [ObjectId(creator_id)],
            "participants": [],
            "stages": ["Assigned", "In Progress", "Review", "Complete"],
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        result = ProjectModel.collection.insert_one(project)
        return str(result.inserted_id)
    
    @staticmethod
    def get_project(project_id):
        try:
            return ProjectModel.collection.find_one({"_id": ObjectId(project_id)})
        except:
            return None
    
    @staticmethod
    def get_user_projects(user_id):
        user_id_obj = ObjectId(user_id)
        return list(ProjectModel.collection.find({
            "$or": [
                {"creator_id": user_id_obj},
                {"admin_users": user_id_obj},
                {"participants": user_id_obj}
            ]
        }))
    
    @staticmethod
    def update_project(project_id, update_data):
        update_data["updated_at"] = datetime.now()
        
        result = ProjectModel.collection.update_one(
            {"_id": ObjectId(project_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    @staticmethod
    def add_admin(project_id, username):
        user = db.users.find_one({"username": username})
        if not user:
            return False
        user_id_obj = user["_id"]
        result = ProjectModel.collection.update_one(
            {"_id": ObjectId(project_id)},
            {
                "$addToSet": {"admin_users": user_id_obj},
                "$set": {"updated_at": datetime.now()}
            }
        )
        return result.modified_count > 0
    
    @staticmethod
    def add_participant(project_id, username):
        user = db.users.find_one({"username": username})
        if not user:
            return False
        user_id_obj = user["_id"]
        result = ProjectModel.collection.update_one(
            {"_id": ObjectId(project_id)},
            {
                "$addToSet": {"participants": user_id_obj},
                "$set": {"updated_at": datetime.now()}
            }
        )
        return result.modified_count > 0
    
    @staticmethod
    def remove_user(project_id, username):
        user = db.users.find_one({"username": username})
        if not user:
            return False
        user_id_obj = user["_id"]
        result = ProjectModel.collection.update_one(
            {"_id": ObjectId(project_id)},
            {
                "$pull": {
                    "admin_users": user_id_obj,
                    "participants": user_id_obj
                },
                "$set": {"updated_at": datetime.now()}
            }
        )
        return result.modified_count > 0
    
    @staticmethod
    def update_stages(project_id, stages):
        result = ProjectModel.collection.update_one(
            {"_id": ObjectId(project_id)},
            {
                "$set": {
                    "stages": stages,
                    "updated_at": datetime.now()
                }
            }
        )
        return result.modified_count > 0
    
    @staticmethod
    def delete_project(project_id):
        # Delete all tasks associated with the project
        db.tasks.delete_many({"project_id": ObjectId(project_id)})
        
        # Delete the project
        result = ProjectModel.collection.delete_one({"_id": ObjectId(project_id)})
        return result.deleted_count > 0