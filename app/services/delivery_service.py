from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.models import Delivery, DeliveryAgent, DeliveryStatus
from datetime import datetime, timezone

async def get_delivery_by_order(db: AsyncSession, order_id: str):
    result = await db.execute(select(Delivery).filter(Delivery.order_id == order_id))
    return result.scalars().first()

async def get_delivery(db: AsyncSession, delivery_id: str):
    result = await db.execute(select(Delivery).filter(Delivery.id == delivery_id))
    return result.scalars().first()

async def update_delivery_status(db: AsyncSession, delivery_id: str, status: DeliveryStatus):
    delivery = await get_delivery(db, delivery_id)
    if not delivery:
        return None
        
    delivery.status = status
    if status == DeliveryStatus.DELIVERED:
        delivery.actual_delivered_at = datetime.now(timezone.utc)
        
        # Free up agent
        agent_result = await db.execute(select(DeliveryAgent).filter(DeliveryAgent.id == delivery.agent_id))
        agent = agent_result.scalars().first()
        if agent:
            agent.is_available = True
            
    await db.commit()
    await db.refresh(delivery)
    return delivery

async def get_agents(db: AsyncSession):
    result = await db.execute(select(DeliveryAgent))
    return result.scalars().all()

async def get_agent(db: AsyncSession, agent_id: str):
    result = await db.execute(select(DeliveryAgent).filter(DeliveryAgent.id == agent_id))
    return result.scalars().first()
