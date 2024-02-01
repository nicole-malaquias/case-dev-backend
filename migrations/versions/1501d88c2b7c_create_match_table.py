"""create Match table

Revision ID: 1501d88c2b7c
Revises: a88a58e25650
Create Date: 2024-01-31 09:22:07.907577

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1501d88c2b7c'
down_revision: Union[str, None] = 'a88a58e25650'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('matches',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('competitor_1_id', sa.Integer(), nullable=False),
    sa.Column('competitor_2_id', sa.Integer(), nullable=False),
    sa.Column('winner_id', sa.Integer(), nullable=True),
    sa.Column('tournament_id', sa.Integer(), nullable=False),
    sa.Column('round', sa.Integer(), nullable=False),
    sa.Column('state', sa.Enum('pending', 'finished', name='match_state'), nullable=False),
    sa.ForeignKeyConstraint(['competitor_1_id'], ['competitors.id'], ),
    sa.ForeignKeyConstraint(['competitor_2_id'], ['competitors.id'], ),
    sa.ForeignKeyConstraint(['tournament_id'], ['tournaments.id'], ),
    sa.ForeignKeyConstraint(['winner_id'], ['competitors.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('matches')
    # ### end Alembic commands ###