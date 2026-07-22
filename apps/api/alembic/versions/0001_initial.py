"""initial schema via SQLModel metadata
Revision ID: 0001_initial
Revises:
Create Date: 2026-07-22
"""
from alembic import op
from sqlmodel import SQLModel
from packages.shared import models  # noqa: F401
revision='0001_initial'
down_revision=None
branch_labels=None
depends_on=None

def upgrade():
    bind = op.get_bind()
    SQLModel.metadata.create_all(bind)

def downgrade():
    SQLModel.metadata.drop_all(op.get_bind())
