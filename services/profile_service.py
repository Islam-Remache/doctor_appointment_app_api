# services/profile_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from db.models.models import Doctor, Patient, WorkingHours
from api.schemas.schemas import PatientUpdate, DoctorUpdate

def update_doctor_profile(db: Session, doctor_id: int, doctor_update_data: DoctorUpdate) -> Doctor:
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")

    update_data = doctor_update_data.dict(exclude_unset=True)

    # Séparer les horaires de travail du reste
    working_hours_data = update_data.pop("working_hours", None)

    # Mettre à jour les autres champs du docteur
    for key, value in update_data.items():
        setattr(doctor, key, value)

    # Mettre à jour les horaires de travail si fournis
    if working_hours_data is not None:
        for wh in working_hours_data:
            existing_wh = (
                db.query(WorkingHours)
                .filter(
                    WorkingHours.doctor_id == doctor_id,
                    WorkingHours.day_of_week == wh["day_of_week"],
                    WorkingHours.period == wh["period"]
                )
                .first()
            )
            if existing_wh:
                # Mise à jour
                existing_wh.start_time = wh["start_time"]
                existing_wh.end_time = wh["end_time"]
            else:
                # Insertion
                db.add(WorkingHours(
                    doctor_id=doctor_id,
                    day_of_week=wh["day_of_week"],
                    period=wh["period"],
                    start_time=wh["start_time"],
                    end_time=wh["end_time"]
                ))

    db.commit()
    db.refresh(doctor)
    return doctor

def update_patient_profile(db: Session, patient_id: int, patient_update_data: PatientUpdate) -> Patient:
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    update_data = patient_update_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(patient, key, value)
        
    db.commit()
    db.refresh(patient)
    return patient