from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import configparser
import psycopg2
import time
from psycopg2.extras import RealDictCursor
from .config import settings


#localhost
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"

# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

#AWS
#SQLALCHEMY_DATABASE_URL = "postgresql://postgres:YI8E64u4j38x5jrpXRby@test-database.cmqn1m8qejus.ap-southeast-2.rds.amazonaws.com:5432/postgres"

# MySQl
#SQLALCHEMY_DATABASE_URL = "mysql://ymtub6arqxnr54jbqm9e:pscale_pw_5ZAJBXhWJN5ZW54jzyBLUsXUZ2atj67jm4ZdGvPN4wN@aws.connect.psdb.cloud/projectx"



engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



# Connect to an existing database
#while True:
#
#    try:
#        conn = psycopg2.connect(host='localhost', dbname='fastapi', user='postgres', password='General23', cursor_factory=RealDictCursor)
#        cursor = conn.cursor()
#        print("Connected to DB")
#        break
#    except Exception as error:
#        print("Falied DB Connection")
#        print("error:", error)
#        time.sleep(2)