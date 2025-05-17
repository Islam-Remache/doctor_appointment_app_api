from sqlalchemy import (
    Column, Integer, String, Text, ForeignKey, Float, Numeric, DateTime, Enum, TIMESTAMP
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from ..db_setup import Base
from sqlalchemy.dialects.postgresql import JSONB

class SyncStatus(str, PyEnum):
    SYNCED = "SYNCED"
    PENDING_SYNC = "PENDING_SYNC"


class HealthInstitution(Base):
    __tablename__ = "health_institutions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    address = Column(Text)
    latitude = Column(Numeric(9, 6))
    longitude = Column(Numeric(9, 6))
    type = Column(String(50))  

    doctors = relationship("Doctor", back_populates="institution")


class Specialty(Base):
    __tablename__ = "specialties"

    id = Column(Integer, primary_key=True, index=True)
    label = Column(String(255), nullable=False)

    doctors = relationship("Doctor", back_populates="specialty")


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    address = Column(Text)
    phone = Column(String(20))
    email = Column(String(255), nullable=False)
    password = Column(Text)
    photo_url = Column(Text)
    google_id = Column(Text)
    contact_email = Column(Text)
    contact_phone = Column(Text)
    social_links = Column(JSONB)

    specialty_id = Column(Integer, ForeignKey("specialties.id", ondelete="SET NULL"), nullable=True)
    institution_id = Column(Integer, ForeignKey("health_institutions.id", ondelete="SET NULL"), nullable=True)

    specialty = relationship("Specialty", back_populates="doctors")
    institution = relationship("HealthInstitution", back_populates="doctors")
    prescriptions = relationship("Prescription", back_populates="doctor")


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    address = Column(Text)
    phone = Column(String(20))
    email = Column(String(255), nullable=False)
    age = Column(Integer) 
    password = Column(String(255))
    photo_url = Column(Text)
    google_id = Column(String(255))

    prescriptions = relationship("Prescription", back_populates="patient")


class Prescription(Base):
    __tablename__ = "prescriptions"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False)
    instructions = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    expires_at = Column(TIMESTAMP, nullable=False)
    sync_status = Column(Enum(SyncStatus), nullable=False, default=SyncStatus.PENDING_SYNC)
    status = Column(String(50), default="active")

    patient = relationship("Patient", back_populates="prescriptions")
    doctor = relationship("Doctor", back_populates="prescriptions")
    medications = relationship("Medication", back_populates="prescription", cascade="all, delete-orphan")


class Medication(Base):
    __tablename__ = "medications"

    id = Column(Integer, primary_key=True, index=True)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    dosage = Column(String(255))
    frequency = Column(String(255))
    duration = Column(String(255))
    sync_status = Column(Enum(SyncStatus), nullable=False, default=SyncStatus.PENDING_SYNC)

    prescription = relationship("Prescription", back_populates="medications")
