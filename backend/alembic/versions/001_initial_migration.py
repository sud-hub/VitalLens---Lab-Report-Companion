"""Initial migration with all tables

Revision ID: 001
Revises: 
Create Date: 2024-11-25 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_initial_migration'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Create panels table
    op.create_table(
        'panels',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(), nullable=False),
        sa.Column('display_name', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key')
    )
    op.create_index(op.f('ix_panels_id'), 'panels', ['id'], unique=False)

    # Create test_types table
    op.create_table(
        'test_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('panel_id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(), nullable=False),
        sa.Column('display_name', sa.String(), nullable=False),
        sa.Column('unit', sa.String(), nullable=False),
        sa.Column('ref_low', sa.Float(), nullable=True),
        sa.Column('ref_high', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['panel_id'], ['panels.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key')
    )
    op.create_index(op.f('ix_test_types_id'), 'test_types', ['id'], unique=False)

    # Create test_aliases table
    op.create_table(
        'test_aliases',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('alias', sa.String(), nullable=False),
        sa.Column('test_type_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['test_type_id'], ['test_types.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('alias')
    )
    op.create_index(op.f('ix_test_aliases_id'), 'test_aliases', ['id'], unique=False)

    # Create reports table
    op.create_table(
        'reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('original_filename', sa.String(), nullable=False),
        sa.Column('raw_ocr_text', sa.Text(), nullable=True),
        sa.Column('parsed_success', sa.Boolean(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reports_id'), 'reports', ['id'], unique=False)

    # Create test_results table
    op.create_table(
        'test_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('report_id', sa.Integer(), nullable=False),
        sa.Column('test_type_id', sa.Integer(), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['report_id'], ['reports.id'], ),
        sa.ForeignKeyConstraint(['test_type_id'], ['test_types.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_test_results_id'), 'test_results', ['id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_test_results_id'), table_name='test_results')
    op.drop_table('test_results')
    
    op.drop_index(op.f('ix_reports_id'), table_name='reports')
    op.drop_table('reports')
    
    op.drop_index(op.f('ix_test_aliases_id'), table_name='test_aliases')
    op.drop_table('test_aliases')
    
    op.drop_index(op.f('ix_test_types_id'), table_name='test_types')
    op.drop_table('test_types')
    
    op.drop_index(op.f('ix_panels_id'), table_name='panels')
    op.drop_table('panels')
    
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
