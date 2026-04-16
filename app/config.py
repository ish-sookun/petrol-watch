import os


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-change-me')
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://root:@127.0.0.1:5432/petrol_watch'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_TYPE = 'sqlalchemy'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
