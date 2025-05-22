# api/routes/appointment_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload # Make sure selectinload is imported if used directly here
from typing import List

from db.session import get_db
from services import appointment_service # Main service
from db.models.appointment_models import ( # Import models if directly querying here
    Appointment as AppointmentModel,
    Doctor as DoctorModel
)
from api.schemas.appointment_schemas import (
    AppointmentDetailsSchema,
    AppointmentSchema,
    DoctorAppointmentViewSchema
)

router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"]
)

# Endpoint for ALL detailed appointments (general view)
@router.get("/details", response_model=List[AppointmentDetailsSchema])
def read_all_appointments_with_details(db: Session = Depends(get_db)):
    appointments_details = appointment_service.get_all_detailed_appointments(db=db)
    return appointments_details

# Endpoint for a specific patient's detailed appointments
@router.get("/patient/{patient_id}/details", response_model=List[AppointmentDetailsSchema])
def read_patient_appointments_with_details(patient_id: int, db: Session = Depends(get_db)):
    appointments_details = appointment_service.get_detailed_appointments_for_patient(db=db, patient_id=patient_id)
    return appointments_details

# Endpoint for a specific doctor's detailed appointments (doctor's perspective)
@router.get("/doctor/{doctor_id}/details", response_model=List[DoctorAppointmentViewSchema])
def read_doctor_appointments_with_details(doctor_id: int, db: Session = Depends(get_db)):
    appointments_details = appointment_service.get_detailed_appointments_for_doctor(db=db, doctor_id=doctor_id)
    return appointments_details

# Original simple list of all appointments (basic info)
@router.get("/", response_model=List[AppointmentSchema])
def read_all_appointments_simple(db: Session = Depends(get_db)):
    appointments = appointment_service.get_all_appointments(db=db)
    return appointments

# Endpoint to delete an appointment
@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_single_appointment(appointment_id: int, db: Session = Depends(get_db)):
    appointment_service.delete_appointment(db=db, appointment_id=appointment_id)
    return None

# Endpoint for doctor/admin to confirm a 'pending' appointment
@router.patch("/{appointment_id}/confirm", response_model=AppointmentDetailsSchema)
def confirm_appointment_by_doctor(appointment_id: int, db: Session = Depends(get_db)):
    updated_appointment_details = appointment_service.confirm_appointment_status(db=db, appointment_id=appointment_id)
    return updated_appointment_details

# Endpoint for doctor/admin to decline a 'pending' appointment
@router.patch("/{appointment_id}/decline", response_model=AppointmentDetailsSchema)
def decline_appointment_by_doctor(appointment_id: int, db: Session = Depends(get_db)):
    updated_appointment_details = appointment_service.decline_appointment_status(db=db, appointment_id=appointment_id)
    return updated_appointment_details

# --- NEW ENDPOINT AS PER OPTION C ---
@router.get("/{appointment_id}/details_single", response_model=AppointmentDetailsSchema)
def read_single_appointment_details(appointment_id: int, db: Session = Depends(get_db)):
    """
    Retrieve detailed information for a single appointment by its ID.
    """
    # It's better to have this logic in the service layer, but for directness here:
    appointment_db = db.query(AppointmentModel).filter(AppointmentModel.id == appointment_id).options(
        selectinload(AppointmentModel.time_slot),
        selectinload(AppointmentModel.doctor).selectinload(DoctorModel.specialty),
        selectinload(AppointmentModel.doctor).selectinload(DoctorModel.health_institution),
        selectinload(AppointmentModel.patient) # Load patient if _format_appointment_details uses it
    ).first()

    if not appointment_db:
        raise HTTPException(status_code=404, detail=f"Appointment with ID {appointment_id} not found")
    
    # Reuse your existing formatting logic from the service.
    # Ensure _format_appointment_details handles all loaded relationships correctly.
    return appointment_service._format_appointment_details(appointment_db)


# --- NEW ENDPOINT FOR DOCTOR VIEWING A SINGLE APPOINTMENT'S DETAILS ---
@router.get("/{appointment_id}/doctor_view_details", response_model=DoctorAppointmentViewSchema)
def read_single_appointment_details_for_doctor_view(
    appointment_id: int,
    db: Session = Depends(get_db)
    # You might want to add a check here to ensure the requesting user is the doctor
    # for this appointment_id, or an admin, using authentication/authorization.
):
    """
    Retrieve detailed information for a single appointment by its ID,
    formatted for a doctor's perspective (includes patient details).
    """
    appointment_db = db.query(AppointmentModel).filter(AppointmentModel.id == appointment_id).options(
        selectinload(AppointmentModel.time_slot),
        selectinload(AppointmentModel.patient), # Crucial for patient details
        selectinload(AppointmentModel.doctor).selectinload(DoctorModel.health_institution) # For doctor's institution details
    ).first()

    if not appointment_db:
        raise HTTPException(status_code=404, detail=f"Appointment with ID {appointment_id} not found")

    # Reuse your existing formatting logic for the doctor's view
    return appointment_service._format_appointment_for_doctor_view(appointment_db)