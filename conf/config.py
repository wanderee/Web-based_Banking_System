import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or '123456'
    DB_HOST = 'localhost'
    DB_USER = 'root'
    DB_PASSWD = '123456'
    DB_DATABASE = 'flasky_manange'
    ITEMS_PER_PAGE = 10
    JWT_AUTH_URL_RULE = '/api/auth'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True


class ProductionConfig(Config):
    PRODUCTION = True


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
