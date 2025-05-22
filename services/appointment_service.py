# services/appointment_service.py
from sqlalchemy.orm import Session, selectinload
from typing import List, Optional, Dict, Any
from fastapi import HTTPException
from decimal import Decimal

from db.models.appointment_models import (
    Appointment as AppointmentModel,
    Doctor as DoctorModel,
    Patient as PatientModel, # Ensure PatientModel is imported
    TimeSlot as TimeSlotModel,
    Specialty as SpecialtyModel,
    HealthInstitution as HealthInstitutionModel
)

# Helper for general appointment details (shows doctor info)
def _format_appointment_details(appt: AppointmentModel) -> Dict[str, Any]:
    doctor_info = {
        "first_name": "N/A", "last_name": "N/A",
        "specialty_label": None, "photo_url": None,
    }
    health_institution_address: Optional[str] = None
    health_institution_latitude: Optional[Decimal] = None
    health_institution_longitude: Optional[Decimal] = None

    if appt.doctor:
        doctor_info["first_name"] = appt.doctor.first_name
        doctor_info["last_name"] = appt.doctor.last_name
        doctor_info["photo_url"] = appt.doctor.photo_url
        if appt.doctor.specialty:
            doctor_info["specialty_label"] = appt.doctor.specialty.label
        if appt.doctor.health_institution:
            health_institution_address = appt.doctor.health_institution.address
            health_institution_latitude = appt.doctor.health_institution.latitude
            health_institution_longitude = appt.doctor.health_institution.longitude

    slot_date_str: Optional[str] = None
    slot_start_time_str: Optional[str] = None
    slot_end_time_str: Optional[str] = None

    if appt.time_slot:
        if appt.time_slot.date:
            slot_date_str = appt.time_slot.date.isoformat()
        if appt.time_slot.start_time:
            slot_start_time_str = appt.time_slot.start_time.isoformat()
        if appt.time_slot.end_time:
            slot_end_time_str = appt.time_slot.end_time.isoformat()

    return {
        "appointment_id": appt.id,
        "appointment_status": str(appt.status),
        "qr_code_url": appt.qr_code_url,
        "date": slot_date_str,
        "start_time": slot_start_time_str,
        "end_time": slot_end_time_str,
        "doctor": doctor_info,
        "health_institution_address": health_institution_address,
        "health_institution_latitude": health_institution_latitude,
        "health_institution_longitude": health_institution_longitude
    }

# Helper for doctor viewing their appointments (shows patient info)
def _format_appointment_for_doctor_view(appt: AppointmentModel) -> Dict[str, Any]:
    patient_info = {
        "patient_id": None, # Initialize, will be overwritten if appt.patient exists
        "first_name": "N/A",
        "last_name": "N/A",
        "photo_url": None
    }
    if appt.patient: # This check is important
        patient_info["patient_id"] = appt.patient.id # ⭐ ADD THIS LINE & USE .id ⭐
        patient_info["first_name"] = appt.patient.first_name
        patient_info["last_name"] = appt.patient.last_name
        patient_info["photo_url"] = appt.patient.photo_url
    else:
        # If appt.patient is None, Pydantic will fail because patient_id is required (not Optional[int])
        # You might need to decide how to handle this. For now, this structure will likely still
        # cause a Pydantic error if appt.patient can be None AND PatientDetailsSchema requires patient_id.
        # One solution is to make patient_id Optional in PatientDetailsSchema if an appointment might not have a patient.
        # Or, ensure appointments processed by this function ALWAYS have a patient.
        # Given the query in get_detailed_appointments_for_doctor eager loads patient,
        # appt.patient should exist if the FK patient_id in the appointments table is valid.
        # If patient_id in appointments table could be NULL, then PatientDetailsSchema needs patient_id: Optional[int]
        pass


    health_institution_address: Optional[str] = None
    health_institution_latitude: Optional[Decimal] = None
    health_institution_longitude: Optional[Decimal] = None

    if appt.doctor and appt.doctor.health_institution:
        health_institution_address = appt.doctor.health_institution.address
        health_institution_latitude = appt.doctor.health_institution.latitude
        health_institution_longitude = appt.doctor.health_institution.longitude

    slot_date_str: Optional[str] = None
    slot_start_time_str: Optional[str] = None
    slot_end_time_str: Optional[str] = None

    if appt.time_slot:
        if appt.time_slot.date:
            slot_date_str = appt.time_slot.date.isoformat()
        if appt.time_slot.start_time:
            slot_start_time_str = appt.time_slot.start_time.isoformat()
        if appt.time_slot.end_time:
            slot_end_time_str = appt.time_slot.end_time.isoformat()

    return {
        "appointment_id": appt.id,
        "appointment_status": str(appt.status),
        "qr_code_url": appt.qr_code_url,
        "date": slot_date_str,
        "start_time": slot_start_time_str,
        "end_time": slot_end_time_str,
        "patient": patient_info, # This patient_info dict must now contain 'patient_id'
        "health_institution_address": health_institution_address,
        "health_institution_latitude": health_institution_latitude,
        "health_institution_longitude": health_institution_longitude
    }


def get_all_detailed_appointments(db: Session) -> List[Dict[str, Any]]:
    appointments_from_db = db.query(AppointmentModel)\
        .options(
            selectinload(AppointmentModel.time_slot),
            selectinload(AppointmentModel.doctor).selectinload(DoctorModel.specialty),
            selectinload(AppointmentModel.doctor).selectinload(DoctorModel.health_institution)
        ).all()
    return [_format_appointment_details(appt) for appt in appointments_from_db]

def get_detailed_appointments_for_patient(db: Session, patient_id: int) -> List[Dict[str, Any]]:
    appointments_from_db = db.query(AppointmentModel)\
        .filter(AppointmentModel.patient_id == patient_id)\
        .options(
            selectinload(AppointmentModel.time_slot),
            selectinload(AppointmentModel.doctor).selectinload(DoctorModel.specialty),
            selectinload(AppointmentModel.doctor).selectinload(DoctorModel.health_institution)
        ).all()
    if not appointments_from_db:
        return []
    return [_format_appointment_details(appt) for appt in appointments_from_db]

def get_detailed_appointments_for_doctor(db: Session, doctor_id: int) -> List[Dict[str, Any]]:
    doctor = db.query(DoctorModel).filter(DoctorModel.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail=f"Doctor with id {doctor_id} not found")

    appointments_from_db = db.query(AppointmentModel)\
        .filter(AppointmentModel.doctor_id == doctor_id)\
        .options(
            selectinload(AppointmentModel.time_slot),
            selectinload(AppointmentModel.patient), # Eager load patient
            selectinload(AppointmentModel.doctor).selectinload(DoctorModel.health_institution)
        ).all()

    if not appointments_from_db:
        return []
    # If any appointment in appointments_from_db has a NULL patient_id in the database,
    # then appt.patient will be None. If PatientDetailsSchema requires patient_id, this will fail.
    return [_format_appointment_for_doctor_view(appt) for appt in appointments_from_db]

# ... (rest of your service functions: get_all_appointments, delete_appointment, _update_appointment_status, etc.) ...
def get_all_appointments(db: Session): # Basic list
    return db.query(AppointmentModel).all()

def delete_appointment(db: Session, appointment_id: int) -> bool:
    # ... (as before) ...
    appointment_to_delete = db.query(AppointmentModel).filter(AppointmentModel.id == appointment_id).first()
    if not appointment_to_delete:
        raise HTTPException(status_code=404, detail=f"Appointment with id {appointment_id} not found")
    try:
        db.delete(appointment_to_delete)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Could not delete appointment")

def _update_appointment_status(db: Session, appointment_id: int, new_status: str) -> AppointmentModel:
    # ... (as before) ...
    appointment = db.query(AppointmentModel).filter(AppointmentModel.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail=f"Appointment with id {appointment_id} not found")
    if appointment.status != 'pending':
        raise HTTPException(status_code=400, detail=f"Appointment status can only be changed from 'pending'. Current status: {appointment.status}")
    appointment.status = new_status
    try:
        db.commit()
        db.refresh(appointment)
        return appointment
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Could not update appointment status: {str(e)}")


def _get_full_appointment_details_after_update(db: Session, appointment_id: int) -> Dict[str, Any]:
    # ... (as before) ...
    appointment_details_obj = db.query(AppointmentModel).options(
        selectinload(AppointmentModel.time_slot),
        selectinload(AppointmentModel.doctor).selectinload(DoctorModel.specialty),
        selectinload(AppointmentModel.doctor).selectinload(DoctorModel.health_institution),
        selectinload(AppointmentModel.patient)
    ).filter(AppointmentModel.id == appointment_id).one_or_none()
    if not appointment_details_obj:
        raise HTTPException(status_code=404, detail="Appointment not found after update attempt.")
    return _format_appointment_details(appointment_details_obj)


def confirm_appointment_status(db: Session, appointment_id: int) -> Dict[str, Any]:
    _update_appointment_status(db, appointment_id, "confirmed")
    return _get_full_appointment_details_after_update(db, appointment_id)

def decline_appointment_status(db: Session, appointment_id: int) -> Dict[str, Any]:
    _update_appointment_status(db, appointment_id, "declined")
    return _get_full_appointment_details_after_update(db, appointment_id)