# import os
# basedir = os.path.abspath(os.path.dirname(__file__))
#
# SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
# SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://lyrical:$pitfire1@lyricalgenerator.cnx4ehiwgdrl.eu-west-2.rds.amazonaws.com:3306/lyricaldb'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_POOL_RECYCLE = 3600

WTF_CSRF_ENABLED = True
SECRET_KEY = 'AE9E57704F107C6757BF662981'
