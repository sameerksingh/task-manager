# app/views/user_views.py
from fastapi import APIRouter, Depends
from controllers.user_controller import UserController
from models.user import User
from utils import HTTPResponse, verify_token, has_role, hash_password, authenticate_creds, create_jwt_token
from enum import Enum
import constants as api_c


# Define enum for options
class UserFields(str, Enum):
    username = "username"
    id = "id"


router = APIRouter(tags=["user"])


# Login endpoint to obtain JWT token
@router.post("/api/users/login")
async def login(payload: dict):
    username = payload["username"]
    password = payload["password"]
    role = authenticate_creds(username, password)
    token = create_jwt_token(username, role)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/api/users/{field}")
@has_role([api_c.ADMIN, api_c.VIEWER, api_c.EDITOR])
async def get_user(
    field: str, by_id: UserFields, role: str = Depends(verify_token)
):
    if by_id == 'id':
        user = UserController.get_user_by_id(field)
    elif by_id == 'username':
        user = UserController.get_user_by_username(field)
    else:
        return HTTPResponse({"message": "Invalid query parameter"}, 400)
    if user:
        return HTTPResponse(user, 200)
    else:
        return HTTPResponse({"message": "User not found"}, 404)


@router.post("/api/users")
async def create_user_endpoint(user: User):
    user.password = hash_password(user.password, user.salt)
    new_user = UserController.create_user(user)
    if not new_user:
        return HTTPResponse({"message": "This username is already in use"}, 409)
    return HTTPResponse(new_user, 201)


@router.put("/api/users/{user_id}")
@has_role([api_c.ADMIN, api_c.VIEWER, api_c.EDITOR])
async def update_user(user_id: str, user: User, role: str = Depends(verify_token)):
    updated_user = UserController.update_user(user_id, user)
    if updated_user:
        return HTTPResponse(updated_user, 200)
    else:
        return HTTPResponse({"message": "User not found"}, 404)


@router.delete("/api/users/{user_id}")
@has_role([api_c.ADMIN])
async def delete_user(user_id: str, role: str = Depends(verify_token)):
    deleted_status = UserController.delete_user(user_id)
    if deleted_status:
        return HTTPResponse(status_code=204)
    else:
        return HTTPResponse({"message": "User id not found"}, 404)