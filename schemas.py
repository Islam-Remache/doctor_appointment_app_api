from pydantic import BaseModel
from datetime import date, datetime
from typing import Dict
from db.models.prescription import SyncStatus  
class PrescriptionCreate(BaseModel):
    id: int
    patientId: int
    doctorId: int
    instructions: str
    createdAt: datetime
    expiresAt: datetime     

class MedicationCreate(BaseModel):
    id: int
    prescriptionId: int
    name: str
    dosage: str
    frequency: str
    duration: str

class DoctorResponse(BaseModel):
    id: int
    firstName: str
    lastName: str
    address: str
    phone: str
    email: str
    password: str
    photoUrl: str
    googleId: str
    contactEmail: str
    contactPhone: str
    socialLinks: Dict[str, str] = None
    specialtyId: int
    institutionId: int
    
class PatientResponse(BaseModel):
    id: int
    firstName: str
    lastName: str
    address: str
    phone: str
    email: str
    age: int
    password: str
    photoUrl: str
    googleId: str
    
class HealthInstitutionResponse(BaseModel):
    id: int
    name: str
    address: str
    latitude: float
    longitude: float
    type: str
    
class SpecialtyResponse(BaseModel):
    id: int
    label: str


class MedicationResponse(BaseModel):
    id: int
    prescriptionId: int
    name: str
    dosage: str
    frequency: str
    duration: str
    syncStatus: SyncStatus
    
class PrescriptionResponse(BaseModel):
    id: int
    patientId: int
    doctorId: int
    instructions: str
    createdAt: datetime
    expiresAt: datetime
    status: str
    syncStatus: SyncStatus
