from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
import urllib.parse as urlparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

dbConfig = {
    "MONGO_DB_USER": os.getenv("MONGO_DB_USER", "default_user"),
    "MONGO_USER_PASSWORD": os.getenv("MONGO_USER_PASSWORD", "default_password"),
    "MONGO_DB_NAME": os.getenv("MONGO_DB_NAME", "default_db"),
    "MONGO_DB_HOST": os.getenv("MONGO_DB_HOST", "localhost"),
    "MONGO_CLUSTER_ID": os.getenv("MONGO_CLUSTER_ID", "default_cluster"),
}

# Construct Mongo URI
mongo_uri = (
    f"mongodb+srv://{dbConfig['MONGO_DB_USER']}:"
    f"{urlparse.quote_plus(dbConfig['MONGO_USER_PASSWORD'])}@"
    f"{dbConfig['MONGO_DB_NAME'].lower()}.{dbConfig['MONGO_CLUSTER_ID']}.mongodb.net/dev?retryWrites=true&w=majority"
)

client = MongoClient(mongo_uri, server_api=ServerApi('1'))

# Ping the database to a variable
try:
    client.admin.command('ping')
    print("MongoDB connection successful.")
except Exception as e:
    print(f"MongoDB connection failed: {e}")


db = client["dev"]