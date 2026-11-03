"""Add event moderation; preserve publication of existing events.

Revision ID: a3b5c7d9e1f2
Revises: f2c4e6a8b0d1
"""
from alembic import op
import sqlalchemy as sa

revision = 'a3b5c7d9e1f2'
down_revision = 'f2c4e6a8b0d1'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('events') as batch:
        batch.add_column(sa.Column('moderation_status', sa.String(20), nullable=False, server_default='approved'))
        batch.add_column(sa.Column('moderation_comment', sa.Text(), nullable=True))


def downgrade():
    with op.batch_alter_table('events') as batch:
        batch.drop_column('moderation_comment')
        batch.drop_column('moderation_status')
