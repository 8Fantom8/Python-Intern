from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import httpx
import shutil
from models import Base, engine, SessionLocal, Employee

app = FastAPI()

class EmployeeCreate(BaseModel):
    first_name: str
    last_name: str
    age: int
    position: str
    remote: bool

class EmployeeRead(BaseModel):
    id: int
    first_name: str
    last_name: str
    age: int
    position: str
    remote: bool

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/employees/new", response_model=EmployeeRead)
async def create_employee(
    first_name: str,
    last_name: str,
    age: int,
    position: str,
    remote: bool,
    image: UploadFile = File(...)
    , db: Session = Depends(get_db)):
    
    # Save the uploaded image to a local directory
    with open(f"images/{image.filename}", "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    
    # Forward the image to Service 2
    async with httpx.AsyncClient() as client:
        files = {'image': (image.filename, open(f"images/{image.filename}", "rb"), image.content_type)}
        response = await client.post("http://localhost:9000/process_image", files=files)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to process employee image")
        employee_id = response.json().get("employee_id")
    
    # Create new employee record
    db_employee = Employee(id=employee_id, first_name=first_name, last_name=last_name, age=age, position=position, remote=remote)
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

@app.get("/employees/list", response_model=List[EmployeeRead])
def list_employees(name: Optional[str] = None, position: Optional[str] = None, remote: Optional[bool] = None, db: Session = Depends(get_db)):
    query = db.query(Employee)
    if name:
        query = query.filter((Employee.first_name.contains(name)) | (Employee.last_name.contains(name)))
    if position:
        query = query.filter(Employee.position.contains(position))
    if remote is not None:
        query = query.filter(Employee.remote == remote)
    return query.all()

@app.get("/employees/{id}", response_model=EmployeeRead)
def get_employee(id: int, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.id == id).first()
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8800)
