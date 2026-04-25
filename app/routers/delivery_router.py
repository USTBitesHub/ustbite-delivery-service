from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import StandardResponse, DeliveryResponse, DeliveryStatusUpdate, DeliveryAgentResponse
from app.services import delivery_service
from app.events.publisher import publish_event
from app.models.models import DeliveryStatus

# NOTE: prefixes match what KGateway sends after stripping /api:
#   /api/delivery/...  →  /delivery/...  (via URLRewrite)
router = APIRouter(prefix="/delivery", tags=["Delivery"])
agents_router = APIRouter(prefix="/delivery/agents", tags=["Agents"])


def format_response(data, message="Success"):
    return {"data": data, "message": message, "status": "success"}


@router.get("/order/{order_id}", response_model=StandardResponse)
async def get_order_delivery(order_id: str, db: AsyncSession = Depends(get_db)):
    delivery = await delivery_service.get_delivery_by_order(db, order_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found for this order")
    return format_response(DeliveryResponse.model_validate(delivery).model_dump(mode="json"))


@router.put("/{id}/status", response_model=StandardResponse)
async def update_status(id: str, payload: DeliveryStatusUpdate, db: AsyncSession = Depends(get_db)):
    delivery = await delivery_service.update_delivery_status(db, id, payload.status)
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")

    await publish_event("delivery.status_updated", {
        "delivery_id": str(delivery.id),
        "order_id": str(delivery.order_id),
        "status": payload.status.value,
        "user_email": delivery.user_email,
        "user_name": delivery.user_name,
        "restaurant_name": delivery.pickup_restaurant_name,
        "delivery_floor": delivery.dropoff_floor,
        "delivery_wing": delivery.dropoff_wing,
    })

    return format_response(DeliveryResponse.model_validate(delivery).model_dump(mode="json"))


@agents_router.get("", response_model=StandardResponse)
async def list_agents(db: AsyncSession = Depends(get_db)):
    agents = await delivery_service.get_agents(db)
    data = [DeliveryAgentResponse.model_validate(a).model_dump(mode="json") for a in agents]
    return format_response(data)


@agents_router.get("/{id}", response_model=StandardResponse)
async def get_agent(id: str, db: AsyncSession = Depends(get_db)):
    agent = await delivery_service.get_agent(db, id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return format_response(DeliveryAgentResponse.model_validate(agent).model_dump(mode="json"))
