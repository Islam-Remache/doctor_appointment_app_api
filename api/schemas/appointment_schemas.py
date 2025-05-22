# api/schemas/appointment_schemas.py
from pydantic import BaseModel, ConfigDict # Import ConfigDict for Pydantic v2
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional, List, Any, Dict
from datetime import date, time, datetime
from db.models.appointment_models import AppointmentStatus
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

from sqlalchemy import Column, String
from db.models.appointment_models import NotificationType
class DoctorDetailsSchema(BaseModel):
    first_name: str
    last_name: str
    specialty_label: Optional[str] = None
    photo_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True) # Pydantic v2 style

class PatientDetailsSchema(BaseModel):
    patient_id: int # This is required
    first_name: str
    last_name: str
    photo_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True) # Pydantic v2 style

class AppointmentDetailsSchema(BaseModel):
    appointment_id: int
    appointment_status: str
    # ... other fields ...
    doctor: DoctorDetailsSchema
    health_institution_address: Optional[str] = None
    health_institution_latitude: Optional[Decimal] = None
    health_institution_longitude: Optional[Decimal] = None

    model_config = ConfigDict(from_attributes=True) # Pydantic v2 style

class DoctorAppointmentViewSchema(BaseModel):
    appointment_id: int
    appointment_status: str
    # ... other fields ...
    patient: PatientDetailsSchema # Expects PatientDetailsSchema which requires patient_id
    health_institution_address: Optional[str] = None
    health_institution_latitude: Optional[Decimal] = None
    health_institution_longitude: Optional[Decimal] = None

    model_config = ConfigDict(from_attributes=True) # Pydantic v2 style

# ... (AppointmentBase, AppointmentCreate, AppointmentSchema with model_config = ConfigDict(from_attributes=True)) ...
class AppointmentBase(BaseModel):
    patient_id: int
    doctor_id: int
    time_slot_id: Optional[int] = None
    status: str
    qr_code_url: Optional[str] = None
# --- Base Schemas ---
class PatientBase(BaseModel):
    first_name: str
    last_name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: EmailStr
    photo_url: Optional[str] = None

class DoctorBase(BaseModel):
    first_name: str
    last_name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: EmailStr
    photo_url: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    social_links: Optional[Dict[str, str]] = None # e.g. {"linkedin": "url", "twitter": "url"}
    specialty_id: Optional[int] = None

class TimeSlotBase(BaseModel):
    date: date
    start_time: time
    end_time: time
    status: str # "available", "booked"

class AppointmentCreate(AppointmentBase):
    pass

class WorkingHourUpdate(BaseModel):
    day_of_week: int  # 0 (dimanche) à 6 (samedi)
    period: str       # 'morning' ou 'evening'
    start_time: time
    end_time: time

# --- Create Schemas (if needed for other operations) ---
class PatientCreate(PatientBase):
    password: str

class DoctorCreate(DoctorBase):
    password: str

class AppointmentStatusUpdate(BaseModel):
    status: AppointmentStatus

# --- Response Schemas (with ORM mode) ---
class Specialty(BaseModel): # Schema for Specialty
    id: int
    label: str

    class Config:
        orm_mode = True

class Patient(PatientBase):
    id: int

    class Config:
        orm_mode = True

class Doctor(DoctorBase):
    id: int
    specialty: Optional[Specialty] = None # Nested specialty info

    class Config:
        orm_mode = True

class TimeSlot(TimeSlotBase):
    id: int
    doctor_id: int

    class Config:
        orm_mode = True

class Appointment(AppointmentBase):
    id: int
    patient: Optional[Patient] = None # Optional for flexibility, can be required
    doctor: Optional[Doctor] = None   # Optional for flexibility
    time_slot: Optional[TimeSlot] = None # Optional for flexibility

    class Config:
        orm_mode = True
        use_enum_values = True # Important for Enum to string conversion




class NotificationBase(BaseModel):
    title:str
    type: str
    message: str
    user_type: str  # 'patient' or 'doctor'
    
class NotificationCreate(NotificationBase):
    user_id: int
    
class NotificationResponse(NotificationBase):
    id: int
    user_id: int
    is_read: bool
    sent_at: datetime
    title: str
    type : NotificationType

    
    class Config:
        orm_mode = True
        
class NotificationList(BaseModel):
    notifications: List[NotificationResponse]
    total: int
    unread_count: int

class AppointmentSchema(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    time_slot_id: Optional[int] = None
    status: str
    qr_code_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True) # Pydantic v2 style