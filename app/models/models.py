import uuid
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base
import enum

class DeliveryStatus(str, enum.Enum):
    ASSIGNED = "ASSIGNED"
    PICKED_UP = "PICKED_UP"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"

class DeliveryAgent(Base):
    __tablename__ = "delivery_agents"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    phone = Column(String)
    employee_id = Column(String, unique=True, nullable=False)
    is_available = Column(Boolean, default=True)
    current_floor = Column(String)
    current_wing = Column(String)

class Delivery(Base):
    __tablename__ = "deliveries"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), nullable=False, unique=True)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("delivery_agents.id"), nullable=False)
    status = Column(Enum(DeliveryStatus), default=DeliveryStatus.ASSIGNED)
    pickup_floor = Column(String)
    pickup_restaurant_name = Column(String)
    dropoff_floor = Column(String)
    dropoff_wing = Column(String)
    estimated_minutes = Column(Integer)
    user_email = Column(String)
    user_name = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    actual_delivered_at = Column(DateTime(timezone=True))



#dummy commit
