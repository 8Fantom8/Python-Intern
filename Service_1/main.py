from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil
import os
import requests

from database import SessionLocal, engine
import models as models
import schemas as schemas

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/employees/new", response_model=schemas.Employee)
async def create_employee(
    first_name: str = Query(...),
    last_name: str = Query(...),
    age: int = Query(...),
    position: str = Query(...),
    remote: bool = Query(...),
    photo: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    photo_filename = f"{photo.filename}"
    photo_path = f"photos/{photo_filename}"

    # Ensure photos directory exists
    if not os.path.exists("photos"):
        os.makedirs("photos")

    # Save the photo locally
    with open(photo_path, "wb") as buffer:
        shutil.copyfileobj(photo.file, buffer)

    # Forward image to Service 2
    files = {'photo': (photo.filename, open(photo_path, 'rb'), photo.content_type)}
    try:
        response = requests.post("http://127.0.0.1:9000/generate_id", files=files)
        response.raise_for_status()  # Raise an error for bad responses
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Service 2 error: {str(e)}")

    service_2_id = response.json().get("employee_id")
    if not service_2_id:
        raise HTTPException(status_code=500, detail="Service 2 did not return a valid employee ID")

    db_employee = models.Employee(
        first_name=first_name,
        last_name=last_name,
        age=age,
        position=position,
        remote=remote,
        photo=photo_filename,
        service_2_id=service_2_id
    )

    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

@app.get("/employees/list", response_model=List[schemas.Employee])
def list_employees(
    name: Optional[str] = None,
    position: Optional[str] = None,
    remote: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Employee)
    if name:
        query = query.filter((models.Employee.first_name.contains(name)) | (models.Employee.last_name.contains(name)))
    if position:
        query = query.filter(models.Employee.position == position)
    if remote is not None:
        query = query.filter(models.Employee.remote == remote)
    return query.all()

@app.get("/employees/{employee_id}", response_model=schemas.Employee)
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee
