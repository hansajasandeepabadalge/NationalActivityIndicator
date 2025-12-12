"""merge_heads

Revision ID: 446b1540c4d0
Revises: add_l1_learning_system, add_selectors_column
Create Date: 2025-12-11 21:17:54.122782

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '446b1540c4d0'
down_revision: Union[str, None] = ('add_l1_learning_system', 'add_selectors_column')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
