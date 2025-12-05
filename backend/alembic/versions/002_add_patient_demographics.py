"""Add patient demographics to reports

Revision ID: 002_add_patient_demographics
Revises: 001_initial_migration
Create Date: 2025-12-05

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_add_patient_demographics'
down_revision = '001_initial_migration'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add patient_gender and patient_age columns to reports table."""
    # Add patient demographics columns
    op.add_column('reports', sa.Column('patient_gender', sa.String(), nullable=True))
    op.add_column('reports', sa.Column('patient_age', sa.Integer(), nullable=True))


def downgrade() -> None:
    """Remove patient demographics columns from reports table."""
    # Remove patient demographics columns
    op.drop_column('reports', 'patient_age')
    op.drop_column('reports', 'patient_gender')
