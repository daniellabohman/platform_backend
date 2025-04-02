"""Initial migration

Revision ID: 72191fba6c56
Revises: 
Create Date: 2025-04-02 14:24:10.168490
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '72191fba6c56'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create the categories table
    op.create_table('categories',
        sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('name', mysql.VARCHAR(length=100), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        mysql_collate='utf8mb4_0900_ai_ci',
        mysql_default_charset='utf8mb4',
        mysql_engine='InnoDB'
    )

    # Create the users table
    op.create_table('users',
        sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('username', mysql.VARCHAR(length=100), nullable=False),
        sa.Column('email', mysql.VARCHAR(length=100), nullable=False),
        sa.Column('password_hash', mysql.VARCHAR(length=255), nullable=False),
        sa.Column('role', mysql.VARCHAR(length=50), nullable=False),
        sa.Column('address', mysql.VARCHAR(length=255), nullable=True),
        sa.Column('city', mysql.VARCHAR(length=255), nullable=True),
        sa.Column('zip_code', mysql.VARCHAR(length=10), nullable=True),
        sa.Column('phone_number', mysql.VARCHAR(length=20), nullable=True),
        sa.Column('is_instructor', mysql.TINYINT(display_width=1), server_default=sa.text("'0'"), autoincrement=False, nullable=True),
        sa.Column('created_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        mysql_collate='utf8mb4_0900_ai_ci',
        mysql_default_charset='utf8mb4',
        mysql_engine='InnoDB'
    )

    # Add unique indexes on the username and email columns
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_index('username', ['username'], unique=True)
        batch_op.create_index('email', ['email'], unique=True)

    # Create the courses table
    op.create_table('courses',
        sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('title', mysql.VARCHAR(length=150), nullable=False),
        sa.Column('description', mysql.TEXT(), nullable=False),
        sa.Column('price', mysql.FLOAT(), nullable=False),
        sa.Column('category_id', mysql.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('instructor_id', mysql.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('resources', mysql.TEXT(), nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], name='courses_ibfk_1'),
        sa.ForeignKeyConstraint(['instructor_id'], ['users.id'], name='courses_ibfk_2'),
        sa.PrimaryKeyConstraint('id'),
        mysql_collate='utf8mb4_0900_ai_ci',
        mysql_default_charset='utf8mb4',
        mysql_engine='InnoDB'
    )

    # Create the bookings table
    op.create_table('bookings',
        sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('user_id', mysql.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('course_id', mysql.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('booking_date', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], name='bookings_ibfk_2'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='bookings_ibfk_1'),
        sa.PrimaryKeyConstraint('id'),
        mysql_collate='utf8mb4_0900_ai_ci',
        mysql_default_charset='utf8mb4',
        mysql_engine='InnoDB'
    )

    # Create the feedback table
    op.create_table('feedback',
        sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('user_id', mysql.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('course_id', mysql.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('rating', mysql.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('comment', mysql.TEXT(), nullable=True),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], name='feedback_ibfk_2'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='feedback_ibfk_1'),
        sa.PrimaryKeyConstraint('id'),
        mysql_collate='utf8mb4_0900_ai_ci',
        mysql_default_charset='utf8mb4',
        mysql_engine='InnoDB'
    )


def downgrade():
    op.drop_table('feedback')
    op.drop_table('bookings')
    op.drop_table('courses')
    op.drop_table('categories')
    op.drop_table('users')
    # ### end Alembic commands ###
