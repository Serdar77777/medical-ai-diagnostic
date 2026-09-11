from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from database.db import get_db
from database.models import Patient
from pydantic import BaseModel, EmailStr

router = APIRouter()

# Pydantic schemas
class PatientCreate(BaseModel):
    name: str
    age: int
    gender: str  # M/F/Other
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    allergies: List[str] = []
    chronic_diseases: List[str] = []
    current_medications: List[str] = []

class PatientUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    allergies: Optional[List[str]] = None
    chronic_diseases: Optional[List[str]] = None
    current_medications: Optional[List[str]] = None

class PatientResponse(BaseModel):
    id: int
    name: str
    age: int
    gender: str
    email: Optional[str]
    phone: Optional[str]
    allergies: List[str]
    chronic_diseases: List[str]
    current_medications: List[str]
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True

@router.post("/", response_model=PatientResponse)
async def create_patient(
    patient: PatientCreate,
    db: Session = Depends(get_db)
) -> PatientResponse:
    """
    Create a new patient
    """
    try:
        # Check if patient with same email already exists
        if patient.email:
            existing = db.query(Patient).filter(Patient.email == patient.email).first()
            if existing:
                raise HTTPException(status_code=400, detail="Patient with this email already exists")
        
        new_patient = Patient(
            name=patient.name,
            age=patient.age,
            gender=patient.gender,
            email=patient.email,
            phone=patient.phone,
            allergies=patient.allergies,
            chronic_diseases=patient.chronic_diseases,
            current_medications=patient.current_medications
        )
        
        db.add(new_patient)
        db.commit()
        db.refresh(new_patient)
        
        return PatientResponse(
            id=new_patient.id,
            name=new_patient.name,
            age=new_patient.age,
            gender=new_patient.gender,
            email=new_patient.email,
            phone=new_patient.phone,
            allergies=new_patient.allergies or [],
            chronic_diseases=new_patient.chronic_diseases or [],
            current_medications=new_patient.current_medications or [],
            created_at=new_patient.created_at.isoformat(),
            updated_at=new_patient.updated_at.isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[PatientResponse])
async def list_patients(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
) -> List[PatientResponse]:
    """
    List all patients
    """
    try:
        patients = db.query(Patient).offset(skip).limit(limit).all()
        return [
            PatientResponse(
                id=p.id,
                name=p.name,
                age=p.age,
                gender=p.gender,
                email=p.email,
                phone=p.phone,
                allergies=p.allergies or [],
                chronic_diseases=p.chronic_diseases or [],
                current_medications=p.current_medications or [],
                created_at=p.created_at.isoformat(),
                updated_at=p.updated_at.isoformat()
            )
            for p in patients
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: int,
    db: Session = Depends(get_db)
) -> PatientResponse:
    """
    Get patient by ID
    """
    try:
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        return PatientResponse(
            id=patient.id,
            name=patient.name,
            age=patient.age,
            gender=patient.gender,
            email=patient.email,
            phone=patient.phone,
            allergies=patient.allergies or [],
            chronic_diseases=patient.chronic_diseases or [],
            current_medications=patient.current_medications or [],
            created_at=patient.created_at.isoformat(),
            updated_at=patient.updated_at.isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: int,
    patient_update: PatientUpdate,
    db: Session = Depends(get_db)
) -> PatientResponse:
    """
    Update patient information
    """
    try:
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Update only provided fields
        update_data = patient_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(patient, field, value)
        
        patient.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(patient)
        
        return PatientResponse(
            id=patient.id,
            name=patient.name,
            age=patient.age,
            gender=patient.gender,
            email=patient.email,
            phone=patient.phone,
            allergies=patient.allergies or [],
            chronic_diseases=patient.chronic_diseases or [],
            current_medications=patient.current_medications or [],
            created_at=patient.created_at.isoformat(),
            updated_at=patient.updated_at.isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{patient_id}")
async def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db)
) -> dict:
    """
    Delete a patient (soft delete - mark as deleted)
    """
    try:
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        db.delete(patient)
        db.commit()
        
        return {"message": "Patient deleted successfully", "patient_id": patient_id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{patient_id}/summary")
async def get_patient_summary(
    patient_id: int,
    db: Session = Depends(get_db)
) -> dict:
    """
    Get comprehensive patient summary
    """
    try:
        from database.models import BloodTest, Diagnosis
        
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Get recent diagnoses
        recent_diagnoses = db.query(Diagnosis).filter(
            Diagnosis.patient_id == patient_id
        ).order_by(Diagnosis.created_at.desc()).limit(5).all()
        
        # Get recent blood tests
        recent_tests = db.query(BloodTest).filter(
            BloodTest.patient_id == patient_id
        ).order_by(BloodTest.test_date.desc()).limit(5).all()
        
        return {
            "patient": {
                "id": patient.id,
                "name": patient.name,
                "age": patient.age,
                "gender": patient.gender,
                "allergies": patient.allergies or [],
                "chronic_diseases": patient.chronic_diseases or [],
                "current_medications": patient.current_medications or []
            },
            "recent_diagnoses": [
                {
                    "primary": d.primary_diagnosis,
                    "probability": d.primary_probability,
                    "severity": d.severity,
                    "created_at": d.created_at.isoformat()
                }
                for d in recent_diagnoses
            ],
            "recent_tests": [
                {
                    "test_date": t.test_date.isoformat(),
                    "hemoglobin": t.hemoglobin,
                    "glucose": t.glucose,
                    "platelets": t.platelets
                }
                for t in recent_tests
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))