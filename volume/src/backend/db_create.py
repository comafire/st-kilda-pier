from run import db

import sqlalchemy
import os, uuid, base62

DB_HOST = "mysql-skp"
DB_USER = "root"
DB_PW =  os.environ['MYSQL_ROOT_PASSWORD']
DB_NAME = "flask_skp"
DB_ENGINE_URI = "mysql://{}:{}@{}".format(DB_USER, DB_PW, DB_HOST)

engine = sqlalchemy.create_engine(DB_ENGINE_URI)
try:
    engine.execute("DROP DATABASE {}".format(DB_NAME))
except:
    print("")
    
engine.execute("CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8mb4'".format(DB_NAME))
engine.execute("USE {}".format(DB_NAME))
