from pydantic import BaseModel, Field, field_validator, model_validator
import constants as api_c
from datetime import datetime


class Task(BaseModel):
    id: str | None = None
    title: str
    description: str
    status: str = Field(choices=api_c.ALLOWED_TASK_STATUS_LIST, default=api_c.TO_DO_STATUS)
    created_by: str
    created_at: datetime = Field(default=datetime.utcnow())
    updated_by: str | None = None
    updated_at: datetime = Field(default=datetime.utcnow())

    @field_validator("status")
    def validate_status(cls, value):
        if value not in api_c.ALLOWED_TASK_STATUS_LIST:
            raise ValueError(f"status must be one of {api_c.ALLOWED_TASK_STATUS_LIST}")
        return value

    @model_validator(mode="before")
    def set_default_updated_by(cls, values):
        if not values.get(api_c.UPDATED_BY):
            values[api_c.UPDATED_BY] = values.get(api_c.CREATED_BY)
        return values


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None
    updated_by: str
    updated_at: datetime = Field(default=datetime.utcnow())
