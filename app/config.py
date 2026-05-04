class FlaskConfig(object):
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:123456@localhost:3306/neo4j_ask"
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY = "jasmine"