from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException
from pymongo import MongoClient
from config import Config
import jwt
import datetime
from functools import wraps
import hashlib


class Database:
    _instance = None

    def __new__(cls, uri):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.client = MongoClient(uri)
        return cls._instance

    def __getattr__(self, attr):
        return getattr(self.client, attr)


mongo_client = Database(Config.MONGO_URI)


def HTTPResponse(content: object = None, status_code: int = 200) -> object:
    """
    Constructs an HTTP response based on the provided content and status code.
    Args:
        content (Any): The content to be included in the response. Default is None.
        status_code (int): The HTTP status code to be included in the response. Default is 200.
    Returns:
        JSONResponse: The constructed JSONResponse object with appropriate content and status code.
    """
    if content is None:
        content = {}

    # Encode content to JSON-compatible format
    encoded_content = jsonable_encoder(content)

    # Construct JSONResponse object with provided content and status code
    return JSONResponse(content=encoded_content, status_code=status_code)


def document_to_model(YourModel, doc):
    doc["id"] = str(doc.pop("_id"))
    return YourModel(**doc)


# Secret key for signing JWT tokens
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
# JWT security scheme
bearer_scheme = HTTPBearer()


def hash_password(password, salt):
    return hashlib.sha256((password + salt).encode()).hexdigest()


def authenticate_creds(username: str, password: str):
    result = mongo_client.db.users.find_one({"email": username})
    if not result:
        raise HTTPException(
            status_code=401, detail="Invalid username" + username + ", " + password
        )
    salt = result.get("salt")
    key = result.get("password")
    new_key = hash_password(password, salt)
    if key == new_key:
        return result.get("role")
    raise HTTPException(
        status_code=401,
        detail="Invalid username or password"
        + salt
        + ", "
        + new_key
        + ", "
        + key
        + ","
        + result.get("role"),
    )


# Function to generate JWT token
def create_jwt_token(username: str, role: str) -> str:
    # Calculate the current time
    current_time = datetime.datetime.utcnow()

    # Set the expiry time to 30 minutes from the current time
    expiry_time = current_time + datetime.timedelta(minutes=30)

    data = {"username": username, "role": role}
    # Generate the payload with the expiry time
    payload = {
        "sub": data,
        "exp": expiry_time,
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# Function to validate JWT token
def decode_jwt_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# Dependency function for token validation
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    try:
        payload = decode_jwt_token(credentials.credentials)
        data = payload.get("sub")
        if data:
            return data.get("role")
        raise HTTPException(status_code=401, detail="Invalid token")
    except HTTPException as e:
        print(e)
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


# Decorator function to check user role
def has_role(allowed_roles):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, role: str = "viewer", **kwargs):
            # Check if the role parameter is present in the list of allowed roles
            if role not in allowed_roles:
                raise HTTPException(
                    status_code=403,
                    detail=f"Forbidden: User does not have required role(s): {', '.join(allowed_roles)}",
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator
