import json
from typing import Dict, List, Optional

class DrugChecker:
    """Check drug interactions and side effects"""
    
    # Simplified drug database
    DRUG_DATABASE = {
        "aspirin": {
            "category": "Analgesic/Antiplatelet",
            "contraindications": ["warfarin", "ibuprofen"],
            "side_effects": ["bleeding", "GI upset"],
            "warnings": ["Do not use if allergic to NSAIDs"]
        },
        "warfarin": {
            "category": "Anticoagulant",
            "contraindications": ["aspirin", "ibuprofen", "naproxen"],
            "side_effects": ["bleeding", "bruising"],
            "warnings": ["Requires INR monitoring", "Avoid sudden dose changes"]
        },
        "metformin": {
            "category": "Antidiabetic",
            "contraindications": [],
            "side_effects": ["GI upset", "diarrhea"],
            "warnings": ["Monitor kidney function", "Hold before contrast procedures"]
        },
        "lisinopril": {
            "category": "ACE Inhibitor",
            "contraindications": ["potassium supplements"],
            "side_effects": ["cough", "dizziness"],
            "warnings": ["Monitor potassium levels", "Check for pregnancy"]
        },
        "ibuprofen": {
            "category": "NSAID",
            "contraindications": ["aspirin", "warfarin"],
            "side_effects": ["GI upset", "kidney issues"],
            "warnings": ["Use lowest dose for shortest duration", "Not for long-term use"]
        },
        "amoxicillin": {
            "category": "Antibiotic",
            "contraindications": ["cephalexin"],  # Cross-reactivity
            "side_effects": ["allergic reactions", "diarrhea"],
            "warnings": ["Ask about penicillin allergy", "May reduce oral contraceptive effectiveness"]
        },
        "omeprazole": {
            "category": "Proton Pump Inhibitor",
            "contraindications": [],
            "side_effects": ["headache", "diarrhea"],
            "warnings": ["Long-term use affects B12 absorption", "May mask GERD symptoms"]
        },
        "atorvastatin": {
            "category": "Statin",
            "contraindications": [],
            "side_effects": ["muscle pain", "liver issues"],
            "warnings": ["Monitor liver enzymes", "Avoid grapefruit juice"]
        },
        "enalapril": {
            "category": "ACE Inhibitor",
            "contraindications": ["potassium supplements"],
            "side_effects": ["cough", "hypotension"],
            "warnings": ["Check kidney function", "Monitor blood pressure"]
        },
        "metoprolol": {
            "category": "Beta Blocker",
            "contraindications": ["verapamil"],
            "side_effects": ["fatigue", "low heart rate"],
            "warnings": ["Do not stop abruptly", "Monitor heart rate"]
        }
    }
    
    def __init__(self):
        self.database = self.DRUG_DATABASE
        self.total_drugs = len(self.database)
    
    def search_drug(self, drug_name: str) -> Optional[Dict]:
        """
        Search for drug information
        """
        drug_name_lower = drug_name.lower().strip()
        
        # Direct match
        if drug_name_lower in self.database:
            return {
                "name": drug_name_lower,
                **self.database[drug_name_lower]
            }
        
        # Partial match
        for drug, info in self.database.items():
            if drug_name_lower in drug or drug in drug_name_lower:
                return {
                    "name": drug,
                    **info
                }
        
        return None
    
    def check_interaction(self, drug1: str, drug2: str) -> Dict:
        """
        Check if two drugs interact
        """
        drug1_lower = drug1.lower().strip()
        drug2_lower = drug2.lower().strip()
        
        info1 = self.search_drug(drug1_lower)
        info2 = self.search_drug(drug2_lower)
        
        if not info1 or not info2:
            return {
                "has_interaction": False,
                "severity": "unknown",
                "message": "One or both drugs not found in database"
            }
        
        drug1_name = info1["name"]
        drug2_name = info2["name"]
        
        # Check contraindications
        if drug2_name in info1.get("contraindications", []):
            return {
                "has_interaction": True,
                "severity": "major",
                "drug1": drug1_name,
                "drug2": drug2_name,
                "message": f"{drug1_name} and {drug2_name} have a major interaction",
                "recommendation": "Avoid this combination or use alternative drugs"
            }
        
        if drug1_name in info2.get("contraindications", []):
            return {
                "has_interaction": True,
                "severity": "major",
                "drug1": drug1_name,
                "drug2": drug2_name,
                "message": f"{drug1_name} and {drug2_name} have a major interaction",
                "recommendation": "Avoid this combination or use alternative drugs"
            }
        
        return {
            "has_interaction": False,
            "severity": "none",
            "drug1": drug1_name,
            "drug2": drug2_name,
            "message": f"{drug1_name} and {drug2_name} appear safe together",
            "recommendation": "Monitor for any adverse effects"
        }
    
    def get_total_drugs(self) -> int:
        """
        Get total number of drugs in database
        """
        return self.total_drugs
    
    def get_categories(self) -> List[str]:
        """
        Get all drug categories
        """
        categories = set()
        for drug_info in self.database.values():
            if "category" in drug_info:
                categories.add(drug_info["category"])
        return sorted(list(categories))
    
    def get_last_updated(self) -> str:
        """
        Get last update time
        """
        return "2024-09-11"  # This would come from database in production

# Singleton
_drug_checker = None

def get_drug_checker() -> DrugChecker:
    global _drug_checker
    if _drug_checker is None:
        _drug_checker = DrugChecker()
    return _drug_checker