from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# db url connection and create session
from app.test_service_models import Base

# create database engine
db_url = 'postgresql://user:postgres@35.184.60.255:5432/test-service-db'
engine = create_engine(db_url)

# create tables with Base object from models
Base.metadata.create_all(engine)

# define and return session object
Session = sessionmaker(bind=engine)
session = Session()