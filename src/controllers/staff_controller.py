from fastapi import APIRouter, Depends, HTTPException
from typing import List
from database import get_db, Connection
from services.staff_service import StaffService
from models.staff import Staff, StaffCreate
from app import get_current_active_user # Import the dependency
from models.user import User # Import User model

router = APIRouter()

@router.post("/staff", response_model=Staff)
def create_staff(staff: StaffCreate, db: Connection = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    service = StaffService(db)
    return service.create_staff(staff)

@router.get("/staff", response_model=List[Staff])
def get_all_staff(db: Connection = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    service = StaffService(db)
    return service.get_all_staff()

@router.get("/staff/{staff_id}", response_model=Staff)
def get_staff(staff_id: str, db: Connection = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    service = StaffService(db)
    staff = service.get_staff(staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    return staff

@router.put("/staff/{staff_id}", response_model=Staff)
def update_staff(staff_id: str, staff_update: StaffCreate, db: Connection = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    service = StaffService(db)
    staff = service.update_staff(staff_id, staff_update)
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    return staff

@router.delete("/staff/{staff_id}")
def delete_staff(staff_id: str, db: Connection = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    service = StaffService(db)
    if not service.delete_staff(staff_id):
        raise HTTPException(status_code=404, detail="Staff not found")
    return {"message": "Staff deleted successfully"}
