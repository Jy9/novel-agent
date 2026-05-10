import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "novel_agent")
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "change-this-to-a-32-byte-secret-key!!")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
