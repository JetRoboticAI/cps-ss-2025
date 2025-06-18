from sqlalchemy import create_engine, Column, Integer, Float, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./patients.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    patientID = Column(String, index=True)
    bpm = Column(Integer)
    spo2 = Column(Integer)
    temp = Column(Float)
    healthStatus = Column(String)
    waitingTime = Column(Integer)

Base.metadata.create_all(bind=engine)
