import os

class Config(object):
    """
    Default configuration, with test values for consumer key & secret
    """
    if 'RDS_HOSTNAME' in os.environ:
        DB = {
            'NAME': os.environ['RDS_DB_NAME'],
            'USER': os.environ['RDS_USERNAME'],
            'PASSWORD': os.environ['RDS_PASSWORD'],
            'HOST': os.environ['RDS_HOSTNAME'],
            'PORT': os.environ['RDS_PORT'],
        }
        SQLALCHEMY_DATABASE_URI = 'mysql://' + DB['USER'] + ":" + DB['PASSWORD'] + '@' + DB['HOST'] + ":" + DB['PORT'] + '/' + DB['NAME']
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/test.db'


    CONSUMER_KEY = os.getenv('CONSUMER_KEY', 'VLFXgP5KwaaOcHwIj1g5w')
    CONSUMER_SECRET = os.getenv('CONSUMER_SECRET', 'ccEpq0ztdpMbJgbj0vAOemIq3f9PJBE0FKtIxMHvl4')

    DEBUG = os.getenv('DEBUG', False)
    SECRET_KEY = os.getenv('SECRET_KEY', 'development key')

    BOOTSTRAP_USE_MINIFIED = True
    BOOTSTRAP_USE_CDN = True
    BOOTSTRAP_FONTAWESOME = True