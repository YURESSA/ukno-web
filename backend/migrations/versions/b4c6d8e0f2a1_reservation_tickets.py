"""Add opaque reservation tickets, admission counters and audit records."""
from alembic import op
import sqlalchemy as sa


revision = 'b4c6d8e0f2a1'
down_revision = 'a3b5c7d9e1f2'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('reservations') as batch:
        batch.add_column(sa.Column('ticket_token', sa.String(64), nullable=True))
        batch.add_column(sa.Column('checked_in_count', sa.Integer(), nullable=False, server_default='0'))
        batch.create_unique_constraint('uq_reservations_ticket_token', ['ticket_token'])
        batch.create_check_constraint('ck_reservation_admitted_capacity',
                                      'checked_in_count >= 0 AND checked_in_count <= participants_count')
    op.create_table(
        'reservation_admissions',
        sa.Column('admission_id', sa.Integer(), primary_key=True),
        sa.Column('reservation_id', sa.Integer(),
                  sa.ForeignKey('reservations.reservation_id', ondelete='CASCADE'), nullable=False),
        sa.Column('admin_user_id', sa.Integer(), sa.ForeignKey('users.user_id', ondelete='SET NULL'), nullable=True),
        sa.Column('request_id', sa.String(36), nullable=False),
        sa.Column('participants_count', sa.Integer(), nullable=False),
        sa.Column('admitted_at', sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint('reservation_id', 'request_id', name='uq_admission_request'),
        sa.CheckConstraint('participants_count > 0', name='ck_admission_positive_count'),
    )
    op.create_index('ix_reservation_admissions_reservation_id', 'reservation_admissions', ['reservation_id'])


def downgrade():
    op.drop_table('reservation_admissions')
    with op.batch_alter_table('reservations') as batch:
        batch.drop_constraint('ck_reservation_admitted_capacity', type_='check')
        batch.drop_constraint('uq_reservations_ticket_token', type_='unique')
        batch.drop_column('checked_in_count')
        batch.drop_column('ticket_token')
