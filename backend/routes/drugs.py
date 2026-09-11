from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from database.db import get_db
from database.models import Patient, DrugInteraction
from llm.ollama_integration import get_llm
from utils.drug_checker import get_drug_checker
from pydantic import BaseModel

router = APIRouter()

# Pydantic schemas
class DrugCheckRequest(BaseModel):
    patient_id: int
    drugs: List[str]

class DrugCheckResponse(BaseModel):
    patient_id: int
    drugs_checked: List[str]
    interactions: List[dict]
    safe: bool
    warnings: List[str]

class DrugInteractionCheck(BaseModel):
    drug1: str
    drug2: str

@router.post("/check-interaction", response_model=dict)
async def check_drug_interaction(
    check: DrugInteractionCheck
) -> dict:
    """
    Check interaction between two drugs
    """
    try:
        llm = get_llm()
        result = llm.check_drug_interaction(check.drug1, check.drug2)
        
        return {
            "drug1": check.drug1,
            "drug2": check.drug2,
            "has_interaction": result.get("has_interaction", False),
            "interaction_type": result.get("interaction_type"),
            "description": result.get("description"),
            "recommendation": result.get("recommendation")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/check-patient-drugs", response_model=DrugCheckResponse)
async def check_patient_drugs(
    check_request: DrugCheckRequest,
    db: Session = Depends(get_db)
) -> DrugCheckResponse:
    """
    Check all drug interactions for a patient
    Includes checking against patient allergies and chronic diseases
    """
    try:
        # Get patient
        patient = db.query(Patient).filter(Patient.id == check_request.patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        interactions = []
        warnings = []
        is_safe = True
        
        llm = get_llm()
        
        # Check all drug combinations
        for i, drug1 in enumerate(check_request.drugs):
            for drug2 in check_request.drugs[i+1:]:
                result = llm.check_drug_interaction(drug1, drug2)
                
                if result.get("has_interaction"):
                    interaction = {
                        "drug1": drug1,
                        "drug2": drug2,
                        "type": result.get("interaction_type"),
                        "description": result.get("description")
                    }
                    interactions.append(interaction)
                    
                    if result.get("interaction_type") == "major":
                        is_safe = False
                        warnings.append(f"⚠️ MAJOR: {drug1} + {drug2} - {result.get('description')}")
                    elif result.get("interaction_type") == "moderate":
                        warnings.append(f"⚠️ MODERATE: {drug1} + {drug2} - {result.get('description')}")
        
        # Check against patient allergies
        for drug in check_request.drugs:
            for allergy in patient.allergies or []:
                if allergy.lower() in drug.lower():
                    is_safe = False
                    warnings.append(f"🚫 ALLERGY: Patient is allergic to {allergy}, drug contains it!")
        
        return DrugCheckResponse(
            patient_id=check_request.patient_id,
            drugs_checked=check_request.drugs,
            interactions=interactions,
            safe=is_safe,
            warnings=warnings
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/database")
async def get_drug_database() -> dict:
    """
    Get available drugs database info
    """
    try:
        drug_checker = get_drug_checker()
        return {
            "total_drugs": drug_checker.get_total_drugs(),
            "categories": drug_checker.get_categories(),
            "last_updated": drug_checker.get_last_updated()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search/{drug_name}")
async def search_drug(
    drug_name: str
) -> dict:
    """
    Search for drug information
    """
    try:
        drug_checker = get_drug_checker()
        drug_info = drug_checker.search_drug(drug_name)
        
        if not drug_info:
            raise HTTPException(status_code=404, detail=f"Drug '{drug_name}' not found")
        
        return drug_info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/classify-drugs")
async def classify_drugs(
    drugs: List[str]
) -> dict:
    """
    Classify drugs by category
    """
    try:
        drug_checker = get_drug_checker()
        classifications = {}
        
        for drug in drugs:
            info = drug_checker.search_drug(drug)
            if info:
                classifications[drug] = info.get("category", "Unknown")
            else:
                classifications[drug] = "Not found"
        
        return {"classifications": classifications}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))