class Config(object):
    TESTING = False
    SECRET_KEY = "123456"
    MONGODB_SETTINGS = {
        "db": "appdb",
        "port": 27017,
        "host": "localhost"
    }

class DevConfig(Config):
    DEBUG = True


class TestConfig(Config):
    DEBUG = False
    
class ProConfig(Config):
    DEBUG = False
