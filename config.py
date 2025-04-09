import os
import pymysql

pymysql.install_as_MySQLdb()

class Config:
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'default_secret_key') 
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:UgandaSkipper9@localhost/nexpertia_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
