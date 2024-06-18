from pydantic import BaseModel
from typing import Optional

class EmployeeBase(BaseModel):
    first_name: str
    last_name: str
    age: int
    position: str
    remote: bool

class EmployeeCreate(EmployeeBase):
    pass

class Employee(EmployeeBase):
    id: int
    photo: Optional[str]

    class Config:
        orm_mode = True
