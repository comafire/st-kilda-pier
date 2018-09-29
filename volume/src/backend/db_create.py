import run
from run import db

import sqlalchemy
import os, uuid, base62

DB_ENGINE_URI = "mysql://{}:{}@{}".format(run.DB_USER, run.DB_PW, run.DB_HOST)

engine = sqlalchemy.create_engine(DB_ENGINE_URI)
engine.execute("DROP DATABASE IF EXISTS {}".format(run.DB_NAME))
engine.execute("CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8mb4'".format(run.DB_NAME))
engine.execute("USE {}".format(run.DB_NAME))
