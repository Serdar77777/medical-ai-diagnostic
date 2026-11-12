from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from database.db import get_db
from database.models import BloodTest, MedicalImage, Diagnosis, Patient
from llm.ollama_integration import get_llm
from models.blood_analyzer import get_blood_analyzer
from models.image_analyzer import get_image_analyzer
import json

router = APIRouter()


class BloodTestInput(BaseModel):
    patient_id: int
    hemoglobin: Optional[float] = None
    hematocrit: Optional[float] = None
    red_blood_cells: Optional[float] = None
    white_blood_cells: Optional[float] = None
    leukocytes: Optional[float] = None
    platelets: Optional[float] = None
    glucose: Optional[float] = None
    creatinine: Optional[float] = None
    urea: Optional[float] = None
    sodium: Optional[float] = None
    potassium: Optional[float] = None
    chloride: Optional[float] = None


class ImageAnalysisInput(BaseModel):
    patient_id: int
    image_type: str = 'xray'
    image_base64: str


class DiagnosisResponse(BaseModel):
    patient_id: int
    primary_diagnosis: str
    primary_probability: float
    secondary_diagnoses: List
    severity: str
    recommended_tests: List[str]
    recommended_treatments: List[str]
    specialist_referral: Optional[str] = None


@router.post("/blood")
async def analyze_blood_test(
    blood_input: BloodTestInput,
    db: Session = Depends(get_db)
) -> DiagnosisResponse:
    """
    Analyze blood test results and generate diagnosis.
    Compatible with both canonical and frontend-friendly field names.
    """
    try:
        patient = db.query(Patient).filter(Patient.id == blood_input.patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        # normalize frontend shorthand like leukocytes -> white_blood_cells
        raw = blood_input.dict(exclude_none=True)
        if 'leukocytes' in raw and 'white_blood_cells' not in raw:
            raw['white_blood_cells'] = raw.pop('leukocytes')

        blood_values = {k: v for k, v in raw.items() if k != 'patient_id'}

        blood_analyzer = get_blood_analyzer()
        analysis = blood_analyzer.analyze(blood_values, patient.gender)

        blood_test = BloodTest(
            patient_id=patient.id,
            raw_data=blood_values,
            **{k: v for k, v in raw.items() if k != 'patient_id'}
        )
        db.add(blood_test)
        db.flush()

        llm = get_llm()
        llm_analysis = llm.analyze_blood_test(blood_values) if llm.is_available else {}

        primary_diagnosis = analysis['diagnoses'][0]['name'] if analysis['diagnoses'] else 'No specific diagnosis'
        primary_probability = analysis['diagnoses'][0]['probability'] if analysis['diagnoses'] else 0.0

        secondary_diagnoses = [
            {"name": d['name'], "probability": d['probability']}
            for d in analysis['diagnoses'][1:]
        ]

        diagnosis = Diagnosis(
            patient_id=patient.id,
            blood_test_id=blood_test.id,
            primary_diagnosis=primary_diagnosis,
            primary_probability=primary_probability,
            secondary_diagnoses=secondary_diagnoses,
            severity=analysis['severity'],
            ai_findings=json.dumps(analysis['abnormalities']),
            ai_confidence=primary_probability,
            ai_model_used='blood_analyzer',
            recommended_tests=analysis['recommendations'],
            specialist_referral=llm_analysis.get('specialist_referral', None)
        )

        db.add(diagnosis)
        db.commit()

        return DiagnosisResponse(
            patient_id=patient.id,
            primary_diagnosis=primary_diagnosis,
            primary_probability=round(primary_probability, 2),
            secondary_diagnoses=secondary_diagnoses,
            severity=analysis['severity'],
            recommended_tests=analysis['recommendations'],
            recommended_treatments=llm_analysis.get('recommended_treatments', []),
            specialist_referral=llm_analysis.get('specialist_referral')
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/image")
async def analyze_medical_image(
    payload: ImageAnalysisInput,
    db: Session = Depends(get_db)
) -> dict:
    """Analyze medical image from JSON input payload."""
    try:
        patient = db.query(Patient).filter(Patient.id == payload.patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        image_type = payload.image_type.lower()
        if image_type not in ['xray', 'mri', 'ct', 'ultrasound']:
            raise HTTPException(status_code=400, detail='Invalid image type')

        medical_image = MedicalImage(
            patient_id=patient.id,
            image_type=image_type,
            image_path=f"{payload.patient_id}_{image_type}_{datetime.utcnow().timestamp()}.jpg",
            image_data=payload.image_base64
        )
        db.add(medical_image)
        db.flush()

        image_analyzer = get_image_analyzer()
        analysis = image_analyzer.analyze(payload.image_base64, image_type)

        llm = get_llm()
        findings_text = ', '.join(analysis.get('findings', []))
        llm_analysis = llm.analyze_medical_finding(findings_text) if llm.is_available else {}

        diagnosis = Diagnosis(
            patient_id=patient.id,
            image_id=medical_image.id,
            primary_diagnosis=analysis.get('diagnosis', 'Unable to diagnose'),
            primary_probability=analysis.get('confidence', 0.0),
            ai_findings=json.dumps(analysis.get('findings', [])),
            ai_confidence=analysis.get('confidence', 0.0),
            ai_model_used=f'image_analyzer_{image_type}',
            recommended_tests=analysis.get('recommendations', []),
            severity='moderate' if analysis.get('confidence', 0) > 0.7 else 'mild'
        )

        db.add(diagnosis)
        db.commit()

        return {
            'patient_id': patient.id,
            'image_type': image_type,
            'findings': analysis.get('findings', []),
            'diagnosis': analysis.get('diagnosis'),
            'confidence': round(analysis.get('confidence', 0.0), 2),
            'recommendations': analysis.get('recommendations', []),
            'llm_insights': llm_analysis.get('clinical_significance')
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/patient/{patient_id}/diagnoses')
async def get_patient_diagnoses(
    patient_id: int,
    db: Session = Depends(get_db)
) -> List[dict]:
    try:
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail='Patient not found')

        diagnoses = db.query(Diagnosis).filter(
            Diagnosis.patient_id == patient_id
        ).order_by(Diagnosis.created_at.desc()).all()

        result = []
        for d in diagnoses:
            result.append({
                'id': d.id,
                'primary_diagnosis': d.primary_diagnosis,
                'probability': d.primary_probability,
                'severity': d.severity,
                'created_at': d.created_at.isoformat(),
                'ai_model': d.ai_model_used,
                'findings': json.loads(d.ai_findings) if d.ai_findings else []
            })

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/latest/{patient_id}')
async def get_latest_diagnosis(
    patient_id: int,
    db: Session = Depends(get_db)
) -> dict:
    try:
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail='Patient not found')

        diagnosis = db.query(Diagnosis).filter(
            Diagnosis.patient_id == patient_id
        ).order_by(Diagnosis.created_at.desc()).first()

        if not diagnosis:
            raise HTTPException(status_code=404, detail='No diagnosis found')

        return {
            'id': diagnosis.id,
            'primary_diagnosis': diagnosis.primary_diagnosis,
            'probability': diagnosis.primary_probability,
            'secondary_diagnoses': diagnosis.secondary_diagnoses,
            'severity': diagnosis.severity,
            'recommendations': diagnosis.recommended_tests,
            'treatments': diagnosis.recommended_treatments,
            'specialist': diagnosis.specialist_referral,
            'created_at': diagnosis.created_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
