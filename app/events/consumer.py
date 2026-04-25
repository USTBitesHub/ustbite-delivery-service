import json
import aio_pika
from app.config import settings
from app.database import AsyncSessionLocal
from app.services import delivery_service


async def process_message(message: aio_pika.abc.AbstractIncomingMessage):
    async with message.process():
        try:
            event = json.loads(message.body.decode())
            routing_key = message.routing_key

            if routing_key == "payment.success":
                # Auto-create a delivery record when payment succeeds
                async with AsyncSessionLocal() as db:
                    delivery = await delivery_service.create_delivery_for_order(
                        db=db,
                        order_id=event.get("order_id", ""),
                        restaurant_name=event.get("restaurant_name", "Restaurant"),
                        dropoff_floor=event.get("delivery_floor", ""),
                        dropoff_wing=event.get("delivery_wing", ""),
                        user_email=event.get("user_email", ""),
                        user_name=event.get("user_name", "User"),
                        estimated_minutes=event.get("estimated_minutes", 20),
                    )
                    if delivery:
                        print(f"[delivery] Created delivery {delivery.id} for order {event.get('order_id')}")
                    else:
                        print(f"[delivery] Could not create delivery for order {event.get('order_id')} — no agents available")

        except Exception as e:
            print(f"[delivery] Error processing {message.routing_key}: {e}")


async def start_consumer():
    if not settings.rabbitmq_url:
        print("[delivery] No RABBITMQ_URL — consumer not started")
        return
    try:
        connection = await aio_pika.connect_robust(settings.rabbitmq_url)
        mq_channel = await connection.channel()
        exchange = await mq_channel.declare_exchange(
            "ustbite_events", aio_pika.ExchangeType.TOPIC, durable=True
        )
        queue = await mq_channel.declare_queue("delivery_queue", durable=True)
        await queue.bind(exchange, routing_key="payment.success")
        await queue.consume(process_message)
        print("[delivery] Consumer started — listening for payment.success events")
    except Exception as e:
        print(f"[delivery] Failed to start consumer: {e}")
