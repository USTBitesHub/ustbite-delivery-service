"""create_delivery_tables

Revision ID: 2b3c4d5e6f7a
Revises: 1a2b3c4d5e6f
Create Date: 2026-04-25 00:00:00
"""
from alembic import op

revision = '2b3c4d5e6f7a'
down_revision = '1a2b3c4d5e6f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE delivery_status AS ENUM (
                'ASSIGNED', 'PICKED_UP', 'OUT_FOR_DELIVERY', 'DELIVERED'
            );
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;

        CREATE TABLE IF NOT EXISTS delivery_agents (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR NOT NULL,
            phone VARCHAR,
            employee_id VARCHAR NOT NULL UNIQUE,
            is_available BOOLEAN DEFAULT TRUE,
            current_floor VARCHAR,
            current_wing VARCHAR
        );

        CREATE TABLE IF NOT EXISTS deliveries (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            order_id UUID NOT NULL UNIQUE,
            agent_id UUID NOT NULL REFERENCES delivery_agents(id),
            status delivery_status DEFAULT 'ASSIGNED',
            pickup_floor VARCHAR,
            pickup_restaurant_name VARCHAR,
            dropoff_floor VARCHAR,
            dropoff_wing VARCHAR,
            estimated_minutes INTEGER,
            user_email VARCHAR,
            user_name VARCHAR,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            actual_delivered_at TIMESTAMPTZ
        );
        CREATE INDEX IF NOT EXISTS ix_deliveries_order_id ON deliveries(order_id);

        -- Seed: 3 delivery agents so payment.success can auto-assign
        INSERT INTO delivery_agents (id, name, phone, employee_id, is_available)
        VALUES
            ('d0000001-0000-0000-0000-000000000001', 'Arjun Kumar',  '+91-9000000001', 'AGT001', TRUE),
            ('d0000001-0000-0000-0000-000000000002', 'Priya Singh',  '+91-9000000002', 'AGT002', TRUE),
            ('d0000001-0000-0000-0000-000000000003', 'Mohammed Ali', '+91-9000000003', 'AGT003', TRUE)
        ON CONFLICT (employee_id) DO NOTHING;
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS deliveries CASCADE;")
    op.execute("DROP TABLE IF EXISTS delivery_agents CASCADE;")
    op.execute("DROP TYPE IF EXISTS delivery_status;")
