from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from database.db import get_db
from database.models import BloodTest, MedicalImage, Diagnosis, Patient
from llm.ollama_integration import get_llm
from models.blood_analyzer import get_blood_analyzer
from models.image_analyzer import get_image_analyzer
from pydantic import BaseModel
import json

router = APIRouter()

# Pydantic schemas
class BloodTestInput(BaseModel):
    patient_id: int
    hemoglobin: float
    hematocrit: float = None
    red_blood_cells: float = None
    white_blood_cells: float = None
    platelets: float = None
    glucose: float = None
    creatinine: float = None
    urea: float = None
    sodium: float = None
    potassium: float = None
    chloride: float = None

class DiagnosisResponse(BaseModel):
    patient_id: int
    primary_diagnosis: str
    primary_probability: float
    secondary_diagnoses: List
    severity: str
    recommended_tests: List[str]
    recommended_treatments: List[str]
    specialist_referral: str = None

@router.post("/blood")
async def analyze_blood_test(
    blood_input: BloodTestInput,
    db: Session = Depends(get_db)
) -> DiagnosisResponse:
    """
    Analyze blood test results and generate diagnosis
    """
    try:
        # Get patient
        patient = db.query(Patient).filter(Patient.id == blood_input.patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Prepare blood values (exclude None values)
        blood_values = {
            k: v for k, v in blood_input.dict().items() 
            if v is not None and k != "patient_id"
        }
        
        # Analyze blood test
        blood_analyzer = get_blood_analyzer()
        analysis = blood_analyzer.analyze(blood_values, patient.gender)
        
        # Save blood test to database
        blood_test = BloodTest(
            patient_id=patient.id,
            raw_data=blood_values,
            **{k: v for k, v in blood_input.dict().items() if k != "patient_id"}
        )
        db.add(blood_test)
        db.flush()
        
        # Get LLM for additional insights
        llm = get_llm()
        llm_analysis = llm.analyze_blood_test(blood_values) if llm.is_available else {}
        
        # Prepare diagnosis
        primary_diagnosis = analysis["diagnoses"][0]["name"] if analysis["diagnoses"] else "No specific diagnosis"
        primary_probability = analysis["diagnoses"][0]["probability"] if analysis["diagnoses"] else 0.0
        
        secondary_diagnoses = [
            {"name": d["name"], "probability": d["probability"]} 
            for d in analysis["diagnoses"][1:]
        ]
        
        # Create diagnosis record
        diagnosis = Diagnosis(
            patient_id=patient.id,
            blood_test_id=blood_test.id,
            primary_diagnosis=primary_diagnosis,
            primary_probability=primary_probability,
            secondary_diagnoses=secondary_diagnoses,
            severity=analysis["severity"],
            ai_findings=json.dumps(analysis["abnormalities"]),
            ai_confidence=primary_probability,
            ai_model_used="blood_analyzer",
            recommended_tests=analysis["recommendations"],
            specialist_referral=llm_analysis.get("specialist_referral", None)
        )
        
        db.add(diagnosis)
        db.commit()
        
        return DiagnosisResponse(
            patient_id=patient.id,
            primary_diagnosis=primary_diagnosis,
            primary_probability=round(primary_probability, 2),
            secondary_diagnoses=secondary_diagnoses,
            severity=analysis["severity"],
            recommended_tests=analysis["recommendations"],
            recommended_treatments=llm_analysis.get("recommended_treatments", []),
            specialist_referral=llm_analysis.get("specialist_referral")
        )
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/image")
async def analyze_medical_image(
    patient_id: int,
    image_type: str,
    image_base64: str,
    db: Session = Depends(get_db)
) -> dict:
    """
    Analyze medical image (X-ray, MRI, CT, ultrasound)
    """
    try:
        # Get patient
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        if image_type not in ["xray", "mri", "ct", "ultrasound"]:
            raise HTTPException(status_code=400, detail="Invalid image type")
        
        # Save image to database
        medical_image = MedicalImage(
            patient_id=patient.id,
            image_type=image_type,
            image_path=f"{patient_id}_{image_type}_{datetime.utcnow().timestamp()}.jpg",
            image_data=image_base64
        )
        db.add(medical_image)
        db.flush()
        
        # Analyze image
        image_analyzer = get_image_analyzer()
        analysis = image_analyzer.analyze(image_base64, image_type)
        
        # Get LLM insights
        llm = get_llm()
        findings_text = ", ".join(analysis.get("findings", []))
        llm_analysis = llm.analyze_medical_finding(findings_text) if llm.is_available else {}
        
        # Create diagnosis record
        diagnosis = Diagnosis(
            patient_id=patient.id,
            image_id=medical_image.id,
            primary_diagnosis=analysis.get("diagnosis", "Unable to diagnose"),
            primary_probability=analysis.get("confidence", 0.0),
            ai_findings=json.dumps(analysis.get("findings", [])),
            ai_confidence=analysis.get("confidence", 0.0),
            ai_model_used=f"image_analyzer_{image_type}",
            recommended_tests=analysis.get("recommendations", []),
            severity="moderate" if analysis.get("confidence", 0) > 0.7 else "mild"
        )
        
        db.add(diagnosis)
        db.commit()
        
        return {
            "patient_id": patient.id,
            "image_type": image_type,
            "findings": analysis.get("findings", []),
            "diagnosis": analysis.get("diagnosis"),
            "confidence": round(analysis.get("confidence", 0.0), 2),
            "recommendations": analysis.get("recommendations", []),
            "llm_insights": llm_analysis.get("clinical_significance")
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/patient/{patient_id}/diagnoses")
async def get_patient_diagnoses(
    patient_id: int,
    db: Session = Depends(get_db)
) -> List[dict]:
    """
    Get all diagnoses for a patient
    """
    try:
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        diagnoses = db.query(Diagnosis).filter(
            Diagnosis.patient_id == patient_id
        ).order_by(Diagnosis.created_at.desc()).all()
        
        result = []
        for d in diagnoses:
            result.append({
                "id": d.id,
                "primary_diagnosis": d.primary_diagnosis,
                "probability": d.primary_probability,
                "severity": d.severity,
                "created_at": d.created_at.isoformat(),
                "ai_model": d.ai_model_used,
                "findings": json.loads(d.ai_findings) if d.ai_findings else []
            })
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/latest/{patient_id}")
async def get_latest_diagnosis(
    patient_id: int,
    db: Session = Depends(get_db)
) -> dict:
    """
    Get latest diagnosis for a patient
    """
    try:
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        diagnosis = db.query(Diagnosis).filter(
            Diagnosis.patient_id == patient_id
        ).order_by(Diagnosis.created_at.desc()).first()
        
        if not diagnosis:
            raise HTTPException(status_code=404, detail="No diagnosis found")
        
        return {
            "id": diagnosis.id,
            "primary_diagnosis": diagnosis.primary_diagnosis,
            "probability": diagnosis.primary_probability,
            "secondary_diagnoses": diagnosis.secondary_diagnoses,
            "severity": diagnosis.severity,
            "recommendations": diagnosis.recommended_tests,
            "treatments": diagnosis.recommended_treatments,
            "specialist": diagnosis.specialist_referral,
            "created_at": diagnosis.created_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))