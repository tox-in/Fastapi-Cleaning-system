from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, datetime
from enum import Enum
from pydantic_settings import BaseSettings

class RoleType(str, Enum):
    CHIEF = "Chief"
    MEMBER = "Member"
    CLIENT = "Client"
    ADMIN = "Admin"

class PriorityType(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class SpecializationType(str, Enum):
    SALON = "Salon Cleaning"
    KITCHEN = "Kitchen Cleaning"
    GARDENING = "Gardening Cleaning"
    BACKYARD = "Backyard Cleaning"
    POULTRY = "Poultry Cleaning"
    GLASS = "Glass Cleaning"
    LAUNDRY = "Laundry Cleaning"

class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: RoleType

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: RoleType = RoleType.MEMBER

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True

class GroupBase(BaseModel):
    name: str
    specialization: SpecializationType
    rating: Optional[float] = 0.0

class GroupCreate(GroupBase):
    chief_id: Optional[int] = None
    member_ids: List[int] = []

class GroupResponse(BaseModel):
    id: int
    name: str
    specialization: SpecializationType
    rating: float
    chief_id: int
    member_ids: List[int]

    class Config:
        from_attributes = True

class ReservationBase(BaseModel):
    cleaning_type: SpecializationType
    address: str
    house_number: str
    cleaning_date: date
    price: float
    priority: PriorityType = PriorityType.MEDIUM

class ReservationCreate(ReservationBase):
    pass

class ReservationResponse(BaseModel):
    id: int
    cleaning_type: str
    address: str
    house_number: str
    cleaning_date: datetime
    price: float
    approved_by_client: bool
    approved_by_admin: bool
    priority: str
    client_id: int
    assigned_group_id: Optional[int] = None

    class Config:
        from_attributes = True

class ReservationUpdate(BaseModel):
    approved_by_client: Optional[bool] = None
    approved_by_admin: Optional[bool] = None
    priority: Optional[PriorityType] = None
    assigned_group_id: Optional[int] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class UserUpdate(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None

class UserWithStats(UserResponse):
    stats: dict

class Settings(BaseSettings):
    SECRET_KEY: str = "my_authentication_key_for_hashing_passwords_and_jwt_secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

class TaskStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None

class TaskListResponse(BaseModel):
    id: int
    cleaning_type: SpecializationType
    address: str
    house_number: str
    cleaning_date: date
    status: str
    priority: PriorityType
    client_id: int
    assigned_group_id: Optional[int] = None
    price: float
    reservation_date: datetime
    approved_by_client: bool = False
    approved_by_admin: bool = False

    class Config:
        from_attributes = True

class TaskStats(BaseModel):
    total_tasks: int
    pending_tasks: int
    in_progress_tasks: int
    completed_tasks: int
    completion_rate: float

class TaskCalendarEntry(BaseModel):
    id: int
    title: str
    start_date: datetime
    end_date: datetime
    status: str
    priority: PriorityType

class GroupWorkload(BaseModel):
    group_name: str
    total_tasks: int
    completed_tasks: int
    completion_rate: float

class TaskDashboard(BaseModel):
    stats: TaskStats
    upcoming_tasks: List[TaskListResponse]
    recent_tasks: List[TaskListResponse]
    group_workload: Optional[List[GroupWorkload]] = None

    class Config:
        from_attributes = True

settings = Settings()