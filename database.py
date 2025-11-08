# from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pydantic import BaseModel
import os
from pathlib import Path
from dotenv import load_dotenv
from models import UserInDB

# Load .env from the current directory
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)
print(f"[database.py] Loading .env from: {env_path}")
print(f"[database.py] DATABASE_URL found: {os.getenv('DATABASE_URL') is not None}")


class EnvVariables:
    database_url = os.getenv("DATABASE_URL", None)
    jwt_secret = os.getenv("JWT_SECRET", None)
    secret_key = os.getenv("SECRET_KEY", None)
    access_token_expiry_time = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", None)
    algorithm = os.getenv("ALGORITHM", None)
    do_origin = os.getenv("DO_ORIGIN", None)
    do_space_name = os.getenv("DO_SPACE_NAME", None)
    do_space_region = os.getenv("DO_SPACE_REGION", None)
    do_space_key = os.getenv("DO_SPACE_KEY", None)
    do_space_secret = os.getenv("DO_SPACE_SECRET", None)
    auth_token = os.getenv("AUTH_TOKEN", None)
    auth_refno = os.getenv("AUTH_REFNO", None)
    images_db_name = os.getenv("IMAGES_DB_NAME", "AisaasBhoomi")
    college_name = os.getenv("COLLEGE_NAME", "TestImages")


if EnvVariables.database_url:
    pass
else:
    print("Database URL not found in environment variables.")

client = MongoClient(EnvVariables.database_url, server_api=ServerApi('1'))

# Get the database
mongo_db = client.Users

# # TODO:Get the collection dynamically
# user_collection = database.get_collection("studio_owners")
