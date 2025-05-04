# models/user_model.py
from config.db import db
import bcrypt
from datetime import datetime
from bson import ObjectId

class UserModel:
    collection = db["Users"]

    @staticmethod
    def create_user(username, email, password):
        # Hash the password
        pw_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Check if username or email already exists
        if UserModel.collection.find_one({"$or": [{"username": username}, {"email": email}]}):
            return None
        
        # Create new user
        user = {
            "username": username,
            "email": email,
            "password_hash": pw_hash,
            "verified": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        result = UserModel.collection.insert_one(user)
        return str(result.inserted_id)
    
    @staticmethod
    def authenticate_user(email, password):
        user = UserModel.collection.find_one({"email": email})
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user["password_hash"].encode('utf-8')):
            return user
        return None
    
    @staticmethod
    def get_user_by_id(user_id):
        try:
            return UserModel.collection.find_one({"_id": ObjectId(user_id)})
        except:
            return None
    
    @staticmethod
    def get_user_by_email(email):
        return UserModel.collection.find_one({"email": email})
    
    @staticmethod
    def verify_user(user_id):
        result = UserModel.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"verified": True, "updated_at": datetime.now()}}
        )
        return result.modified_count > 0
    
    @staticmethod
    def update_password(user_id, new_password):
        pw_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
        
        result = UserModel.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"password_hash": pw_hash, "updated_at": datetime.now()}}
        )
        return result.modified_count > 0