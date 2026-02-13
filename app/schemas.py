from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any
class UserCreate(BaseModel):
    email: str
    name: str
    password: str
class UserUpdate(BaseModel):
    email: Optional[str] = None
    name: Optional[str] = None
    password: Optional[str] = None
    is_admin: Optional[bool] = None
class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    is_admin: bool
    created_at: datetime
    class Config:
        from_attributes = True
class MessageResponse(BaseModel):
    id: int
    content: str
    sender_id: int
    user_id: int
    is_from_admin: bool
    created_at: datetime
    class Config:
        from_attributes = True
class StatisticResponse(BaseModel):
    total_users: int
    total_services: int
    total_projects: int
    total_messages: int
    total_transactions: int
    active_users: int = 0
    revenue_today: str = "0,0"
    revenue_month: str = "0,0"
    class Config:
        from_attributes = True
class ServiceResponse(BaseModel):
    id: int
    title: str
    icon: str
    short_description: str
    full_description: str
    features: List[str]
    technologies: List[str]
    price_range: str
    duration: str
    order_index: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True
class ProjectResponse(BaseModel):
    id: int
    title: str
    description: str
    status: str
    user_id: int
    service_id: Optional[int]
    created_at: datetime
    class Config:
        from_attributes = True

