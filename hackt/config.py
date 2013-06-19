import os

class Config(object):
    """
    Default configuration, with test values for consumer key & secret
    """
    CONSUMER_KEY = os.getenv('CONSUMER_KEY', 'VLFXgP5KwaaOcHwIj1g5w')
    CONSUMER_SECRET = os.getenv('CONSUMER_SECRET', 'ccEpq0ztdpMbJgbj0vAOemIq3f9PJBE0FKtIxMHvl4')

    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:////tmp/test.db')

    DEBUG = os.getenv('DEBUG', True)
    SECRET_KEY = os.getenv('SECRET_KEY', 'development key')

    BOOTSTRAP_USE_MINIFIED = True
    BOOTSTRAP_USE_CDN = True
    BOOTSTRAP_FONTAWESOME = True