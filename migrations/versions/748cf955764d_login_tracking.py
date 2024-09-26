"""login tracking

Revision ID: 748cf955764d
Revises: 286dfbeef51e
Create Date: 2024-09-10 18:18:09.762471

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '748cf955764d'
down_revision = '286dfbeef51e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user__login',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('login_time', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('user__login', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_user__login_login_time'), ['login_time'], unique=False)
        batch_op.create_index(batch_op.f('ix_user__login_user_id'), ['user_id'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user__login', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user__login_user_id'))
        batch_op.drop_index(batch_op.f('ix_user__login_login_time'))

    op.drop_table('user__login')
    # ### end Alembic commands ###
