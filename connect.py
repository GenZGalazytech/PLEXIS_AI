from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
import boto3
from dotenv import load_dotenv

load_dotenv()

# Read env vars directly to avoid circular import
DATABASE_URL = os.getenv("DATABASE_URL")
IMAGES_DB_NAME = os.getenv("IMAGES_DB_NAME", "ImagesDB")
COLLEGE_NAME = os.getenv("COLLEGE_NAME", "default_college")

if DATABASE_URL:
    client = MongoClient(DATABASE_URL, server_api=ServerApi("1"))
    db = client[IMAGES_DB_NAME]
    user_db = client.Users
    
    try:
        client.admin.command("ping")
        print("[MongoDB] Ping successful. Connected to MongoDB cluster.")
        print(f"[MongoDB] Using database: {IMAGES_DB_NAME}")
        print(f"[MongoDB] Using collection: {COLLEGE_NAME}")
    except Exception as e:
        print(f"[MongoDB] Connection error: {e}")
else:
    print("[MongoDB] DATABASE_URL not found in environment variables.")
    client = None
    db = None
    user_db = None


try:
    DO_SPACE_KEY = os.getenv("DO_SPACE_KEY")
    DO_SPACE_SECRET = os.getenv("DO_SPACE_SECRET")
    DO_SPACE_REGION = os.getenv("DO_SPACE_REGION")
    DO_SPACE_NAME = os.getenv("DO_SPACE_NAME")
    DO_SPACE_ENDPOINT = f"https://{DO_SPACE_REGION}.digitaloceanspaces.com"

    session = boto3.session.Session()
    client = session.client(
        "s3",
        region_name=DO_SPACE_REGION,
        endpoint_url=DO_SPACE_ENDPOINT,
        aws_access_key_id=DO_SPACE_KEY,
        aws_secret_access_key=DO_SPACE_SECRET,
    )
except Exception as e:
    print(e)


def get_s3_client():
    return client


def get_database():
    return db

def get_user_database():
    return user_db


# def get_image_collection():
#     return image_collection
