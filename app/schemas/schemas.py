from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.models import DeliveryStatus

class StandardResponse(BaseModel):
    data: Optional[dict | list] = None
    message: str
    status: str

class DeliveryStatusUpdate(BaseModel):
    status: DeliveryStatus

class DeliveryAgentResponse(BaseModel):
    id: UUID
    name: str
    phone: Optional[str]
    employee_id: str
    is_available: bool
    current_floor: Optional[str]
    current_wing: Optional[str]
    model_config = ConfigDict(from_attributes=True)

class DeliveryResponse(BaseModel):
    id: UUID
    order_id: UUID
    agent_id: UUID
    status: DeliveryStatus
    pickup_floor: Optional[str]
    pickup_restaurant_name: Optional[str]
    dropoff_floor: Optional[str]
    dropoff_wing: Optional[str]
    estimated_minutes: Optional[int]
    created_at: datetime
    actual_delivered_at: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)
