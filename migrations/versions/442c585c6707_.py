"""empty message

Revision ID: 442c585c6707
Revises: 1501d88c2b7c
Create Date: 2024-01-31 10:50:15.191370

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '442c585c6707'
down_revision: Union[str, None] = '1501d88c2b7c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('competitors', sa.Column('status', sa.Boolean(), nullable=True))
    op.create_unique_constraint(None, 'matches', ['id'])
    op.add_column('tournaments', sa.Column('number_matches', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tournaments', 'number_matches')
    op.drop_constraint(None, 'matches', type_='unique')
    op.drop_column('competitors', 'status')
    # ### end Alembic commands ###
