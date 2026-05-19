from alembic import op
import sqlalchemy as sa

revision = '20251204_000001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('uuid', sa.String(36), unique=True, index=True),
        sa.Column('username', sa.String(50), unique=True, nullable=False, index=True),
        sa.Column('email', sa.String(100), unique=True, nullable=False, index=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(100)),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('is_superuser', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime),
        sa.Column('updated_at', sa.DateTime),
    )

    op.create_table(
        'items',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('uuid', sa.String(36), unique=True, index=True),
        sa.Column('title', sa.String(100), nullable=False, index=True),
        sa.Column('description', sa.Text),
        sa.Column('price', sa.Numeric(10, 2), nullable=False),
        sa.Column('owner_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE')),
        sa.Column('created_at', sa.DateTime),
        sa.Column('updated_at', sa.DateTime),
    )

    op.create_table(
        'posts',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('uuid', sa.String(36), unique=True, index=True),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('author_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE')),
        sa.Column('is_published', sa.Boolean, default=False),
        sa.Column('view_count', sa.Integer, default=0),
        sa.Column('created_at', sa.DateTime),
        sa.Column('updated_at', sa.DateTime),
        sa.Column('published_at', sa.DateTime),
    )

    op.create_table(
        'comments',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('uuid', sa.String(36), unique=True, index=True),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('post_id', sa.Integer, sa.ForeignKey('posts.id', ondelete='CASCADE')),
        sa.Column('author_name', sa.String(100)),
        sa.Column('author_email', sa.String(100)),
        sa.Column('is_approved', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime),
    )

    op.create_table(
        'tags',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('uuid', sa.String(36), unique=True, index=True),
        sa.Column('name', sa.String(50), unique=True, nullable=False),
        sa.Column('slug', sa.String(50), unique=True, nullable=False),
        sa.Column('created_at', sa.DateTime),
    )

    op.create_table(
        'post_tags',
        sa.Column('post_id', sa.Integer, sa.ForeignKey('posts.id'), primary_key=True),
        sa.Column('tag_id', sa.Integer, sa.ForeignKey('tags.id'), primary_key=True),
    )

    op.create_table(
        'audit_logs',
        sa.Column('id', sa.BigInteger, primary_key=True),
        sa.Column('uuid', sa.String(36), unique=True, index=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=True),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('table_name', sa.String(50), nullable=False),
        sa.Column('record_id', sa.Integer, nullable=True),
        sa.Column('old_values', sa.Text, nullable=True),
        sa.Column('new_values', sa.Text, nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime),
    )


def downgrade():
    op.drop_table('audit_logs')
    op.drop_table('post_tags')
    op.drop_table('tags')
    op.drop_table('comments')
    op.drop_table('posts')
    op.drop_table('items')
    op.drop_table('users')
