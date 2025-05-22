# api/dependencies.py
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.session import get_db
from db.models.appointment_models import Doctor, Patient

async def get_current_user_id():
        
    return 1

async def get_current_user_type():
        
    return "patient"


async def get_current_doctor(doctor_id: int, db: Session = Depends(get_db)) -> Doctor:
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")
    return doctor

async def get_current_patient(patient_id: int, db: Session = Depends(get_db)) -> Patient:
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    return patient

# More realistic (but requires full auth setup):
# from fastapi.security import OAuth2PasswordBearer
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token") # Example token URL

# async def get_current_active_doctor(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
#     # ... (JWT decoding and user lookup logic) ...
#     pass