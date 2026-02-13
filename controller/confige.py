import os

basedir = os.path.abspath(os.path.dirname(__file__))
instance_path = os.path.join(os.path.dirname(basedir), 'instance')

class config:
    SECRET_KEY = "#DEEP#LEARNING#GENAI#"
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(instance_path, 'db.sqlite3').replace('\\', '/')
    SQLALCHEMY_TRACK_MODIFICATIONS = False    
