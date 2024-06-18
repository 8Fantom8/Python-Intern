from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    age = Column(Integer)
    position = Column(String, index=True)
    remote = Column(Boolean)
    photo = Column(String, index=True)
    service_2_id = Column(String, index=True)
