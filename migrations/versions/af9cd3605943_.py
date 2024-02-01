"""empty message

Revision ID: af9cd3605943
Revises: 442c585c6707
Create Date: 2024-01-31 11:35:58.530465

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'af9cd3605943'
down_revision: Union[str, None] = '442c585c6707'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('matches', 'competitor_1_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('matches', 'competitor_2_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('matches', 'competitor_2_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('matches', 'competitor_1_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###
