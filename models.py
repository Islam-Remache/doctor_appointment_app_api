from sqlalchemy import Column, Integer, String, ForeignKey, Date, Time, Boolean, JSON, Text, Numeric, Enum
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from database import Base

# Patients
class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(Text)
    photo_url = Column(Text)
    google_id = Column(String(100))

# Specialties
class Specialty(Base):
    __tablename__ = "specialties"
    id = Column(Integer, primary_key=True, index=True)
    label = Column(String(100), unique=True, nullable=False)

# Doctors
class Doctor(Base):
    __tablename__ = "doctors"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    specialty_id = Column(Integer, ForeignKey("specialties.id", ondelete="SET NULL"))
    photo_url = Column(Text)
    social_links = Column(JSON)
    health_institution_id = Column(Integer, ForeignKey("health_institutions.id", ondelete="SET NULL"))

# Time Slots
class TimeSlot(Base):
    __tablename__ = "time_slots"
    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id", ondelete="CASCADE"))
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    status = Column(String(20), server_default="available")

# Appointments
class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"))
    doctor_id = Column(Integer, ForeignKey("doctors.id", ondelete="CASCADE"))
    time_slot_id = Column(Integer, ForeignKey("time_slots.id", ondelete="SET NULL"))
    status = Column(String(20), server_default="pending")
    qr_code_url = Column(Text)

class HealthInstitution(Base):
    __tablename__ = "health_institutions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    address = Column(Text)
    latitude = Column(Numeric(9, 6))
    longitude = Column(Numeric(9, 6))
    type = Column(String(50))  # 'clinic' or 'hospital'