import numpy as np
from typing import Dict, List, Tuple
import json
from datetime import datetime

class BloodAnalyzer:
    """Analyze blood test results and predict diseases"""
    
    # Normal ranges for blood tests (can be customized)
    NORMAL_RANGES = {
        "hemoglobin": {"min": 120, "max": 170, "unit": "g/L", "gender_specific": True},  # M: 130-170, F: 120-150
        "hematocrit": {"min": 35, "max": 50, "unit": "%"},
        "red_blood_cells": {"min": 4.0, "max": 6.0, "unit": "M/µL"},
        "white_blood_cells": {"min": 4.5, "max": 11.0, "unit": "K/µL"},
        "platelets": {"min": 150, "max": 400, "unit": "K/µL"},
        "glucose": {"min": 70, "max": 100, "unit": "mg/dL", "fasting": True},
        "creatinine": {"min": 0.6, "max": 1.2, "unit": "mg/dL"},
        "urea": {"min": 7, "max": 20, "unit": "mg/dL"},
        "sodium": {"min": 135, "max": 145, "unit": "mEq/L"},
        "potassium": {"min": 3.5, "max": 5.0, "unit": "mEq/L"},
        "chloride": {"min": 96, "max": 106, "unit": "mEq/L"},
    }
    
    # Disease signatures (simplified rules)
    DISEASE_PATTERNS = {
        "Anemia": {
            "indicators": {
                "hemoglobin": lambda x: x < 120,
                "hematocrit": lambda x: x < 35,
                "red_blood_cells": lambda x: x < 4.0
            },
            "weight": 3,
            "severity_threshold": 0.7
        },
        "Infection": {
            "indicators": {
                "white_blood_cells": lambda x: x > 11.0,
            },
            "weight": 2,
            "severity_threshold": 0.6
        },
        "Diabetes": {
            "indicators": {
                "glucose": lambda x: x > 126,  # Fasting
            },
            "weight": 3,
            "severity_threshold": 0.8
        },
        "Kidney Disease": {
            "indicators": {
                "creatinine": lambda x: x > 1.2,
                "urea": lambda x: x > 20,
            },
            "weight": 2,
            "severity_threshold": 0.7
        },
        "Hypokalemia": {
            "indicators": {
                "potassium": lambda x: x < 3.5,
            },
            "weight": 2,
            "severity_threshold": 0.6
        },
        "Hyperkalemia": {
            "indicators": {
                "potassium": lambda x: x > 5.0,
            },
            "weight": 2,
            "severity_threshold": 0.6
        },
        "Hyponatremia": {
            "indicators": {
                "sodium": lambda x: x < 135,
            },
            "weight": 2,
            "severity_threshold": 0.6
        },
        "Thrombocytopenia": {
            "indicators": {
                "platelets": lambda x: x < 150,
            },
            "weight": 2,
            "severity_threshold": 0.5
        },
    }
    
    def analyze(self, blood_values: Dict[str, float], patient_gender: str = "M") -> Dict:
        """Analyze blood test results"""
        analysis = {
            "timestamp": datetime.utcnow().isoformat(),
            "abnormalities": [],
            "diagnoses": [],
            "recommendations": [],
            "severity": "normal"
        }
        
        # Check for abnormalities
        for test_name, value in blood_values.items():
            if test_name in self.NORMAL_RANGES:
                abnormality = self._check_abnormality(test_name, value, patient_gender)
                if abnormality:
                    analysis["abnormalities"].append(abnormality)
        
        # Match disease patterns
        diagnosis_scores = self._match_diseases(blood_values)
        analysis["diagnoses"] = self._format_diagnoses(diagnosis_scores)
        
        # Generate recommendations
        analysis["recommendations"] = self._generate_recommendations(blood_values, analysis["diagnoses"])
        
        # Determine overall severity
        analysis["severity"] = self._assess_severity(analysis["abnormalities"])
        
        return analysis
    
    def _check_abnormality(self, test_name: str, value: float, gender: str) -> Dict or None:
        """Check if a test value is abnormal"""
        if test_name not in self.NORMAL_RANGES:
            return None
        
        normal_range = self.NORMAL_RANGES[test_name]
        min_val = normal_range["min"]
        max_val = normal_range["max"]
        
        # Adjust for gender if applicable
        if normal_range.get("gender_specific") and gender.upper() == "F":
            if test_name == "hemoglobin":
                min_val = 120
                max_val = 150
        
        if value < min_val:
            return {
                "test": test_name,
                "value": value,
                "normal_range": f"{min_val}-{max_val}",
                "unit": normal_range["unit"],
                "status": "LOW",
                "deviation": ((min_val - value) / min_val) * 100
            }
        elif value > max_val:
            return {
                "test": test_name,
                "value": value,
                "normal_range": f"{min_val}-{max_val}",
                "unit": normal_range["unit"],
                "status": "HIGH",
                "deviation": ((value - max_val) / max_val) * 100
            }
        
        return None
    
    def _match_diseases(self, blood_values: Dict[str, float]) -> Dict[str, float]:
        """Match blood values against disease patterns"""
        scores = {}
        
        for disease_name, pattern in self.DISEASE_PATTERNS.items():
            matched = 0
            total = len(pattern["indicators"])
            
            for indicator, condition in pattern["indicators"].items():
                if indicator in blood_values:
                    if condition(blood_values[indicator]):
                        matched += 1
            
            if total > 0:
                probability = (matched / total) * pattern["weight"]
                if probability >= pattern["severity_threshold"]:
                    scores[disease_name] = min(probability, 1.0)
        
        return scores
    
    def _format_diagnoses(self, diagnosis_scores: Dict[str, float]) -> List[Dict]:
        """Format diagnoses with probabilities"""
        diagnoses = []
        for disease, probability in sorted(diagnosis_scores.items(), key=lambda x: x[1], reverse=True):
            diagnoses.append({
                "name": disease,
                "probability": round(probability, 2),
                "confidence": "high" if probability > 0.8 else "medium" if probability > 0.5 else "low"
            })
        return diagnoses
    
    def _generate_recommendations(self, blood_values: Dict, diagnoses: List) -> List[str]:
        """Generate test recommendations"""
        recommendations = []
        
        # Based on primary diagnosis
        if diagnoses:
            primary = diagnoses[0]["name"]
            
            if "Anemia" in primary:
                recommendations.extend(["Iron level (serum ferritin)", "Vitamin B12 test", "Folate test"])
            elif "Diabetes" in primary:
                recommendations.extend(["HbA1c test", "Insulin level", "Endocrinology consultation"])
            elif "Kidney Disease" in primary:
                recommendations.extend(["BUN test", "GFR calculation", "Nephrology consultation"])
            elif "Infection" in primary:
                recommendations.extend(["Blood culture", "Complete blood count", "Infectious disease consultation"])
        
        return list(set(recommendations))  # Remove duplicates
    
    def _assess_severity(self, abnormalities: List) -> str:
        """Assess overall severity based on abnormalities"""
        if not abnormalities:
            return "normal"
        
        high_deviation_count = sum(1 for a in abnormalities if a.get("deviation", 0) > 50)
        
        if high_deviation_count >= 3:
            return "severe"
        elif high_deviation_count >= 1:
            return "moderate"
        else:
            return "mild"

# Singleton
_analyzer = None

def get_blood_analyzer() -> BloodAnalyzer:
    global _analyzer
    if _analyzer is None:
        _analyzer = BloodAnalyzer()
    return _analyzer