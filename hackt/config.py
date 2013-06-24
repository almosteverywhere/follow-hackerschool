import os


class Config(object):
    """
    Default configuration, with test values for consumer key & secret
    """
    CONSUMER_KEY = os.getenv('CONSUMER_KEY', 'VLFXgP5KwaaOcHwIj1g5w')
    CONSUMER_SECRET = os.getenv('CONSUMER_SECRET', 'ccEpq0ztdpMbJgbj0vAOemIq3f9PJBE0FKtIxMHvl4')

    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'postgresql://nina:password:@localhost:5432/scrape2')

    DEBUG = os.getenv('DEBUG', True)
    SECRET_KEY = os.getenv('SECRET_KEY', 'development key')

    BOOTSTRAP_USE_MINIFIED = True
    BOOTSTRAP_USE_CDN = True
    BOOTSTRAP_FONTAWESOME = True


class CeleryConfig(object):
    """
    Celery configuration file, using Amazon SQS as a broker.
    """
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', 'your_key')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', 'your_secret')

    BROKER_URL = 'sqs://'
    BROKER_TRANSPORT_OPTIONS = {'polling_interval': 0.3,
                                'visibility_timeout': 120,
                                'queue_name_prefix': 'celery-',}

    CELERY_IMPORTS = ['database.models', 'hackt.tasks']
    CELERY_ANNOTATIONS = {"*": {"rate_limit": "10/s"}}