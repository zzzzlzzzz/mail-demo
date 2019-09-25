from os import environ


class Config:
    SECRET_KEY = environ.get('SKLTECH_SECRET_KEY', 'development')
    SQLALCHEMY_DATABASE_URI = environ.get('SKLTECH_DATABASE_URL', 'sqlite:////tmp/test.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MESSAGES_LIMIT = 100


class DevelopmentConfig(Config):
    pass


class ProductionConfig(Config):
    pass


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = environ.get('SKLTECH_DATABASE_URL', 'sqlite:////tmp/test.db')
