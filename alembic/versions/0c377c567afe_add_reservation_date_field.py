"""add reservation_date field

Revision ID: 0c377c567afe
Revises: df1dfd59961f
Create Date: 2024-11-29 14:46:39.803616

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0c377c567afe'
down_revision: Union[str, None] = 'df1dfd59961f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('reservations', sa.Column('reservation_date', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('reservations', 'reservation_date')
    # ### end Alembic commands ###