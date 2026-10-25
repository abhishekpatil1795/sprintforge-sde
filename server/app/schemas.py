from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

class TaskStatus(str, Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"

class TaskPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class RegisterInput(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    @field_validator("name")
    @classmethod
    def trim_name(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 2: raise ValueError("Name must contain at least 2 non-space characters")
        return value
    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str: return value.strip().lower()

class LoginInput(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=72)
    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str: return value.strip().lower()

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class AuthOut(BaseModel):
    user: UserOut
    token: str
    token_type: str = "bearer"

class ProjectCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: str = Field(default="", max_length=2000)
    @field_validator("name")
    @classmethod
    def trim_name(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 2: raise ValueError("Project name must contain at least 2 non-space characters")
        return value

class ProjectOut(BaseModel):
    id: int
    name: str
    description: str
    owner_id: int
    created_at: datetime
    updated_at: datetime
    task_count: int = 0

class TaskCreate(BaseModel):
    title: str = Field(min_length=2, max_length=160)
    description: str = Field(default="", max_length=2000)
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: datetime | None = None
    @field_validator("title")
    @classmethod
    def trim_title(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 2: raise ValueError("Task title must contain at least 2 non-space characters")
        return value

class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=160)
    description: str | None = Field(default=None, max_length=2000)
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    due_date: datetime | None = None
    @field_validator("title")
    @classmethod
    def trim_title(cls, value: str | None) -> str | None:
        if value is None: return value
        value = value.strip()
        if len(value) < 2: raise ValueError("Task title must contain at least 2 non-space characters")
        return value

class TaskOut(BaseModel):
    id: int
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    due_date: datetime | None
    project_id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class Pagination(BaseModel):
    page: int
    limit: int
    total: int
    pages: int

class TaskListOut(BaseModel):
    tasks: list[TaskOut]
    pagination: Pagination
