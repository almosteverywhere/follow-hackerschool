import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from hackt.config import Config

if 'RDS_HOSTNAME' in os.environ:
    SQLALCHEMY_DATABASE_URI = 'mysql://' + os.environ['RDS_USERNAME'] + ':' + os.environ['RDS_PASSWORD'] +'@' + os.environ['RDS_HOSTNAME']  + '/' + os.environ['RDS_DB_NAME']

else:
     SQLALCHEMY_DATABASE_URI = Config.SQLALCHEMY_DATABASE_URI


engine = create_engine(SQLALCHEMY_DATABASE_URI, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                       bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import models
    Base.metadata.create_all(bind=engine)

