# db/models/appointment_models.py
from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SQLAlchemyEnum, Date, Time, Text, DECIMAL
from sqlalchemy.orm import relationship
from ..session import Base # Assuming db/session.py
from sqlalchemy import (Column, Integer, String, Text, Boolean, TIMESTAMP, ForeignKey,
                        Enum, DECIMAL, TIME, DATE, and_)
from sqlalchemy.orm import relationship,  foreign
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
import enum

class AppointmentStatus(enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    completed = "completed"
    declined = "declined"

class PeriodType(enum.Enum):
    morning = "morning"
    evening = "evening"

class NotificationType(enum.Enum):
    CANCELLED = "CANCELLED"
    RESCHEDULED = "RESCHEDULED"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    UPCOMING = "UPCOMING"
    PRESCRIPTION = "PRESCRIPTION"  
class HealthInstitution(Base): # New Model
    __tablename__ = "health_institutions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    address = Column(Text, nullable=True)
    latitude = Column(DECIMAL(9,6), nullable=True)
    longitude = Column(DECIMAL(9,6), nullable=True)
    type = Column(String(50), nullable=True) # Add CHECK constraint if needed via SQLAlchemy

    # Relationship: An institution can have multiple doctors
    doctors = relationship("Doctor", back_populates="health_institution")


class Specialty(Base):
    __tablename__ = "specialties"
    id = Column(Integer, primary_key=True, index=True)
    label = Column(String(100), unique=True, nullable=False)
    doctors = relationship("Doctor", back_populates="specialty")

class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    photo_url = Column(Text, nullable=True)
    # ... other patient fields
    appointments = relationship("Appointment", back_populates="patient")

class Doctor(Base):
    __tablename__ = "doctors"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    photo_url = Column(Text, nullable=True)
    email = Column(String(100), unique=True, nullable=False)
    specialty_id = Column(Integer, ForeignKey("specialties.id"), nullable=True)
    health_institution_id = Column(Integer, ForeignKey("health_institutions.id"), nullable=True) # New FK

    specialty = relationship("Specialty", back_populates="doctors")
    health_institution = relationship("HealthInstitution", back_populates="doctors") # New relationship
    appointments = relationship("Appointment", back_populates="doctor")

class TimeSlot(Base):
    __tablename__ = "time_slots"
    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    status = Column(String(20), default='available')
    appointments = relationship("Appointment", back_populates="time_slot")

class WorkingHours(Base):
    __tablename__ = "working_hours"
    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id", ondelete="CASCADE"))
    day_of_week = Column(Integer, nullable=False)  # 0=Sunday
    period = Column(Enum(PeriodType, name="period_type_enum"), nullable=False)
    start_time = Column(TIME, nullable=False)
    end_time = Column(TIME, nullable=False)



class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    user_type = Column(String(10), nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    sent_at = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")
    type = Column(Enum(NotificationType, name="notification_type_enum"))

class DeviceToken(Base):
    __tablename__ = "device_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    token = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")

class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    time_slot_id = Column(Integer, ForeignKey("time_slots.id"), nullable=True)
    status = Column(SQLAlchemyEnum('pending', 'confirmed', 'completed', 'declined', name='appointment_status_enum_v2'), default='pending') # Ensure enum name is unique if you had an old one
    qr_code_url = Column(Text, nullable=True) # Already present, ensure it's used

    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
    time_slot = relationship("TimeSlot", back_populates="appointments")