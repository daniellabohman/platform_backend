import os
import pymysql

pymysql.install_as_MySQLdb()

class Config:
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:UgandaSkipper9@localhost/nexpertia_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
