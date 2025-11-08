import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from models import TokenData
from database import EnvVariables
from bson.objectid import ObjectId

# This scheme will look for a token in the 'Authorization: Bearer <token>' header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Allow fixed token from environment for local/prod token passthrough
        if EnvVariables.auth_token and token == EnvVariables.auth_token:
            return {
                "refNo": EnvVariables.auth_refno,
            }

        payload = jwt.decode(
            token, EnvVariables.jwt_secret, algorithms=[EnvVariables.algorithm]
        )
    #     user_id: str = payload.get("id")
    #     user_role: str = payload.get("role")

    #     if user_role in USER_ROLES:
    #         user_role = USER_ROLES[user_role]
    #     else:
    #         raise credentials_exception

    #     if user_id is None:
    #         raise credentials_exception
    #     token_data = TokenData(user_id=user_id)
        return payload
    except Exception as e:
        print(e)
        raise credentials_exception

    # Here you would query the database to get the full user object
    # This part is simplified, see main.py for the actual DB query
    # user = await get_user_from_db(user_id, user_role)  # You'll define this function

    # if user is None:
    #     raise credentials_exception

    # return user
    


# Simplified placeholder for the DB function.
# The actual implementation will be in main.py to use the database connection.
# async def get_user_from_db(user_id: str, user_role: str):
#     from database import mongo_db  # Avoid circular import

#     user_collection = mongo_db.get_collection(user_role)

#     user = await user_collection.find_one(
#         {"_id": ObjectId(user_id)}
#     )  # Or ObjectId(user_id)
#     if user:
#         # You might want to return a Pydantic model of the user
#         return user
#     return None
