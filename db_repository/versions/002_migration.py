from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
source_files = Table('source_files', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('filename', VARCHAR),
)

source_rhymes = Table('source_rhymes', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('filename', String),
)

source_text = Table('source_text', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('filename', String),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['source_files'].drop()
    post_meta.tables['source_rhymes'].create()
    post_meta.tables['source_text'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['source_files'].create()
    post_meta.tables['source_rhymes'].drop()
    post_meta.tables['source_text'].drop()
