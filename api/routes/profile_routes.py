# api/routes/profile_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.session import get_db
from db.models.models import Doctor, Patient
from api.schemas.schemas import Doctor as Doc, Patient as Pat, DoctorUpdate, PatientUpdate
from services import profile_service
# from api.dependencies import get_current_doctor, get_current_patient # For token auth

router = APIRouter(
    prefix="/profile",
    tags=["Profiles"]
)

@router.put("/doctor/{doctor_id}", response_model=Doc)
def update_doctor_profile_endpoint(
    doctor_id: int, # In real app, get from token: current_doctor: models.Doctor = Depends(get_current_doctor)
    profile_data: DoctorUpdate,
    db: Session = Depends(get_db)
):
    """
    Update profile information for the logged-in doctor.
    """
    # doctor_id = current_doctor.id # If using token auth
    
    # Basic check if doctor exists (dependency would handle this better)
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")

    return profile_service.update_doctor_profile(db=db, doctor_id=doctor_id, doctor_update_data=profile_data)


@router.put("/patient/{patient_id}", response_model=Pat)
def update_patient_profile_endpoint(
    patient_id: int, # In real app, get from token: current_patient: models.Patient = Depends(get_current_patient)
    profile_data: PatientUpdate,
    db: Session = Depends(get_db)
):
    """
    Update profile information for the logged-in patient.
    """
    # patient_id = current_patient.id # If using token auth

    # Basic check if patient exists
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
        
    return profile_service.update_patient_profile(db=db, patient_id=patient_id, patient_update_data=profile_data)