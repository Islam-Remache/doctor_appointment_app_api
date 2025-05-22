import fastapi
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from db.db_setup import get_db
from db.models.prescription import Patient, Prescription, Medication, Doctor, HealthInstitution, Specialty
from datetime import datetime
from schemas import PrescriptionCreate, MedicationCreate, DoctorResponse, PatientResponse, HealthInstitutionResponse, SpecialtyResponse, PrescriptionResponse, MedicationResponse
from typing import List

router = fastapi.APIRouter()

@router.get("/")
def read_root():
    return "Server is running"


@router.get("/patients", response_model=List[PatientResponse])
def get_patients(db: Session = Depends(get_db)):
    patients = db.query(Patient).all()
    return [
        PatientResponse(
            id=p.id,
            firstName=p.first_name,
            lastName=p.last_name,
            address=p.address,
            phone=p.phone,
            email=p.email,
            age=p.age,
            password=p.password,
            photoUrl=p.photo_url,
            googleId=p.google_id,
        )
        for p in patients
    ]
    
    
    
    
    
    
    
    
@router.get("/doctors/first")
def get_first_doctor(db: Session = Depends(get_db)):
    try:
        doctor = db.query(Doctor).first()
        if doctor is None:
            raise HTTPException(status_code=404, detail="No doctor found")
        return doctor
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving doctor: {e}")

@router.post("/prescriptions")
def insert_prescription(prescription: PrescriptionCreate, db: Session = Depends(get_db)):
    new_prescription = Prescription(
        id=prescription.id,
        patient_id=prescription.patientId,   
        doctor_id=prescription.doctorId,
        instructions=prescription.instructions,
        expires_at=prescription.expiresAt,
        created_at=prescription.createdAt,
    )
    db.add(new_prescription)
    db.commit()
    db.refresh(new_prescription)
    return {"id": new_prescription.id}

@router.post("/medications")
def insert_medications(medications: List[MedicationCreate], db: Session = Depends(get_db)):
    medications_to_insert = [
        Medication(
            id= medication.id,
            prescription_id=medication.prescriptionId,
            name=medication.name,
            dosage=medication.dosage,   
            frequency=medication.frequency,
            duration=medication.duration
        ) for medication in medications
    ]
    db.add_all(medications_to_insert)
    db.commit()

    for medication in medications_to_insert:
        db.refresh(medication)

    return {"ids": [medication.id for medication in medications_to_insert]}


@router.get("/doctors", response_model=List[DoctorResponse])
def get_all_doctors(db: Session = Depends(get_db)):
    doctors = db.query(Doctor).all()
    return [
        DoctorResponse(
            id=d.id,
            firstName=d.first_name,
            lastName=d.last_name,
            address=d.address,
            phone=d.phone,
            email=d.email,
            password=d.password,
            photoUrl=d.photo_url,
            googleId=d.google_id,
            contactEmail=d.contact_email,
            contactPhone=d.contact_phone,
            socialLinks=d.social_links,
            specialtyId=d.specialty_id,
            institutionId=d.institution_id
        ) for d in doctors
    ]
    
    
@router.get("/doctors/{doctor_id}")
def get_doctor(doctor_id: int, db: Session = Depends(get_db)):
    try:
        doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
        if doctor is None:
            raise HTTPException(status_code=404, detail="Doctor not found")
        return doctor
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving doctor: {e}")




@router.get("/health_institutions", response_model=List[HealthInstitutionResponse])
def get_health_institutions(db: Session = Depends(get_db)):
    institutions = db.query(HealthInstitution).all()
    return [
        HealthInstitutionResponse(
            id=i.id,
            name=i.name,
            address=i.address,
            latitude=i.latitude,
            longitude=i.longitude,
            type=i.type
        ) for i in institutions
    ]



@router.get("/specialties", response_model=List[SpecialtyResponse])
def get_specialties(db: Session = Depends(get_db)):
    specialties = db.query(Specialty).all()
    return [
        SpecialtyResponse(
            id=s.id,
            label=s.label
        ) for s in specialties
    ]
    
    

@router.get("/prescriptions", response_model=List[PrescriptionResponse])
def get_prescriptions(db: Session = Depends(get_db)):
    prescriptions = db.query(Prescription).all()
    return [
        PrescriptionResponse(
            id=p.id,
            patientId=p.patient_id,
            doctorId=p.doctor_id,
            instructions=p.instructions,
            createdAt=p.created_at,
            expiresAt=p.expires_at,
            status=p.status,
            syncStatus=p.sync_status
        ) for p in prescriptions
    ]



@router.get("/medications", response_model=List[MedicationResponse])
def get_medications(db: Session = Depends(get_db)):
    medications = db.query(Medication).all()
    return [
        MedicationResponse(
            id=m.id,
            prescriptionId=m.prescription_id,
            name=m.name,
            dosage=m.dosage,
            frequency=m.frequency,
            duration=m.duration,
            syncStatus=m.sync_status
        ) for m in medications
    ]