from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from models import Doctor, TimeSlot, Appointment, Specialty , HealthInstitution
from database import get_db
from typing import List
from pydantic import BaseModel
from datetime import date, time
from enum import Enum

app = FastAPI()

# Pydantic Models (Request/Response Schemas)
class DoctorBase(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    specialty_id: int | None
    photo_url: str | None
    health_institution_id: int
    class Config:
        from_attributes = True

class SpecialtyResponse(BaseModel):
    id: int
    label: str

    class Config:
        from_attributes = True
class TimeSlotBase(BaseModel):
    id: int
    doctor_id: int
    date: date
    start_time: time
    end_time: time
    status: str

    class Config:
        from_attributes = True

class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    time_slot_id: int
    status: str = "pending"

# --- API Endpoints ---

@app.get("/doctors/", response_model=List[DoctorBase])
def list_doctors(
    skip: int = 0,
    limit: int = Query(default=20, le=100),
    db: Session = Depends(get_db)
):
    doctors = db.query(Doctor).offset(skip).limit(limit).all()
    # FastAPI will automatically convert to proper JSON array format
    return doctors


# 2. Get doctor details by ID
@app.get("/doctors/{doctor_id}", response_model=DoctorBase)
def get_doctor(doctor_id: int, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor

# 3. Get available time slots for a doctor
@app.get("/doctors/{doctor_id}/slots", response_model=List[TimeSlotBase])
def get_doctor_slots(
    doctor_id: int,
    date: date | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(TimeSlot).filter(
        TimeSlot.doctor_id == doctor_id,
        TimeSlot.status == "available"
    )
    if date:
        query = query.filter(TimeSlot.date == date)
    return query.all()

# 4. Schedule an appointment
@app.post("/appointments/", response_model=AppointmentCreate)
def create_appointment(
    appointment: AppointmentCreate,
    db: Session = Depends(get_db)
):
    # Check if time slot exists and is available
    time_slot = db.query(TimeSlot).filter(
        TimeSlot.id == appointment.time_slot_id,
        TimeSlot.status == "available"
    ).first()
    if not time_slot:
        raise HTTPException(status_code=400, detail="Time slot not available")

    # Create appointment
    db_appointment = Appointment(**appointment.model_dump())
    db.add(db_appointment)

    # Mark time slot as booked
    time_slot.status = "booked"
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

@app.get("/specialties/", response_model=List[SpecialtyResponse])
def list_specialties(db: Session = Depends(get_db)):
    specialties = db.query(Specialty).all()
    return specialties


@app.get("/health-institutions/{institution_id}")
def get_health_institution(institution_id: int, db: Session = Depends(get_db)):
    institution = db.query(HealthInstitution).filter(HealthInstitution.id == institution_id).first()
    if not institution:
        raise HTTPException(status_code=404, detail="Health institution not found")
    return institution


class AppointmentStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    canceled = "canceled"  # ✅ British spelling
    declined = "declined"


# --- Response Schema for Appointments ---
class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    status: AppointmentStatus
    time_slot_id: int

    class Config:
        from_attributes = True

# --- Get All Appointments ---
@app.get("/appointments/", response_model=List[AppointmentResponse])
def list_appointments(db: Session = Depends(get_db)):
    return db.query(Appointment).all()

# --- Get Appointment by ID ---
@app.get("/appointments/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(appointment_id: int, db: Session = Depends(get_db)):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment

# --- Delete Appointment by ID ---
@app.delete("/appointments/{appointment_id}")
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Free the associated time slot if needed
    time_slot = db.query(TimeSlot).filter(TimeSlot.id == appointment.time_slot_id).first()
    if time_slot:
        time_slot.status = "available"
    
    db.delete(appointment)
    db.commit()
    return {"message": "Appointment deleted successfully"}

@app.put("/appointments/{appointment_id}/status", response_model=AppointmentResponse)
def update_appointment_status(
    appointment_id: int,
    status: AppointmentStatus,
    db: Session = Depends(get_db)
):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    appointment.status = status
    db.commit()
    db.refresh(appointment)
    return appointment
