from pydantic import BaseModel, Field
import secrets
import constants as api_c


# Note: salt of each user set only first time
class User(BaseModel):
    id: str | None = None
    username: str
    role: str = Field(choices=[api_c.ADMIN, api_c.VIEWER, api_c.EDITOR], default=api_c.EDITOR)
    salt: str = secrets.token_hex(16)
    password_hash: str
