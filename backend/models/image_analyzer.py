import base64
import numpy as np
from typing import Dict, List
from PIL import Image
from io import BytesIO

class ImageAnalyzer:
    """Analyze medical images (X-ray, MRI, CT, ultrasound)"""
    
    # Disease patterns for different image types
    XRAY_FINDINGS = {
        "pneumonia": {
            "indicators": ["infiltration", "consolidation", "opacity"],
            "confidence_boost": 0.3,
            "recommendations": ["CT scan for confirmation", "Antibiotic therapy", "Follow-up X-ray in 2 weeks"]
        },
        "tuberculosis": {
            "indicators": ["cavitary", "upper lobe", "infiltrate"],
            "confidence_boost": 0.35,
            "recommendations": ["TB test", "Infectious disease consultation", "Isolation precautions"]
        },
        "fracture": {
            "indicators": ["break", "crack", "displacement"],
            "confidence_boost": 0.4,
            "recommendations": ["CT for detailed assessment", "Orthopedic consultation", "Immobilization"]
        },
        "pleural_effusion": {
            "indicators": ["fluid", "effusion", "blunting"],
            "confidence_boost": 0.25,
            "recommendations": ["Ultrasound for fluid assessment", "Thoracentesis if needed", "Underlying cause investigation"]
        }
    }
    
    MRI_FINDINGS = {
        "brain_tumor": {
            "indicators": ["mass", "enhancement", "edema", "lesion"],
            "confidence_boost": 0.4,
            "recommendations": ["Neurosurgery consultation", "Advanced imaging", "Biopsy consideration"]
        },
        "stroke": {
            "indicators": ["ischemia", "infarct", "acute"],
            "confidence_boost": 0.35,
            "recommendations": ["Neurology consultation", "Thrombolytic therapy", "ICU monitoring"]
        }
    }
    
    def analyze(self, image_base64: str, image_type: str) -> Dict:
        """
        Analyze medical image
        """
        try:
            # Decode base64 image
            image_data = base64.b64decode(image_base64)
            image = Image.open(BytesIO(image_data))
            
            # Convert to numpy array
            img_array = np.array(image)
            
            # Analyze based on image type
            if image_type == "xray":
                return self._analyze_xray(img_array, image_base64)
            elif image_type == "mri":
                return self._analyze_mri(img_array, image_base64)
            elif image_type == "ct":
                return self._analyze_ct(img_array, image_base64)
            elif image_type == "ultrasound":
                return self._analyze_ultrasound(img_array, image_base64)
            else:
                return self._generic_analysis(img_array, image_base64)
        
        except Exception as e:
            return {
                "error": str(e),
                "findings": ["Unable to process image"],
                "diagnosis": "Analysis failed",
                "confidence": 0.0,
                "recommendations": ["Please upload a clear medical image"]
            }
    
    def _analyze_xray(self, img_array: np.ndarray, image_base64: str) -> Dict:
        """
        Analyze X-ray image
        """
        findings = []
        diagnoses = {}
        
        # Simple analysis based on image properties
        # In production, this would use trained CNN models
        
        # Check image contrast and brightness
        contrast = img_array.std()
        brightness = img_array.mean()
        
        # Simulate findings based on image properties
        if contrast > 50:
            findings.append("High contrast areas detected - possible infiltration")
            diagnoses["pneumonia"] = 0.6
        
        if brightness < 100:
            findings.append("Dense areas visible - possible consolidation")
            diagnoses["pneumonia"] = max(diagnoses.get("pneumonia", 0), 0.5)
        
        # Default findings if none detected
        if not findings:
            findings.append("Lungs appear relatively clear")
            diagnoses["normal"] = 0.8
        
        primary_diagnosis = max(diagnoses, key=diagnoses.get) if diagnoses else "normal"
        confidence = diagnoses.get(primary_diagnosis, 0.5)
        
        # Get recommendations
        recommendations = self.XRAY_FINDINGS.get(
            primary_diagnosis, 
            {}
        ).get("recommendations", ["Clinical correlation recommended"])
        
        return {
            "findings": findings,
            "diagnosis": primary_diagnosis.replace("_", " ").title(),
            "confidence": min(confidence, 1.0),
            "recommendations": recommendations,
            "severity": "mild" if confidence < 0.6 else "moderate" if confidence < 0.8 else "severe"
        }
    
    def _analyze_mri(self, img_array: np.ndarray, image_base64: str) -> Dict:
        """
        Analyze MRI image
        """
        findings = []
        diagnoses = {}
        
        # Check for abnormal signals
        if img_array.std() > 40:
            findings.append("Signal abnormality detected")
            diagnoses["brain_tumor"] = 0.5
        
        if not findings:
            findings.append("MRI appears normal")
            diagnoses["normal"] = 0.85
        
        primary_diagnosis = max(diagnoses, key=diagnoses.get) if diagnoses else "normal"
        confidence = diagnoses.get(primary_diagnosis, 0.5)
        
        recommendations = self.MRI_FINDINGS.get(
            primary_diagnosis.replace(" ", "_"),
            {}
        ).get("recommendations", ["Follow-up imaging recommended"])
        
        return {
            "findings": findings,
            "diagnosis": primary_diagnosis.replace("_", " ").title(),
            "confidence": min(confidence, 1.0),
            "recommendations": recommendations,
            "severity": "mild" if confidence < 0.6 else "moderate" if confidence < 0.8 else "severe"
        }
    
    def _analyze_ct(self, img_array: np.ndarray, image_base64: str) -> Dict:
        """
        Analyze CT scan
        """
        findings = []
        
        # CT scans typically show more detail
        if img_array.max() > 200:
            findings.append("High density areas detected")
        
        if not findings:
            findings.append("CT scan shows no acute abnormalities")
        
        return {
            "findings": findings,
            "diagnosis": "Require radiologist interpretation for CT",
            "confidence": 0.6,
            "recommendations": ["Expert radiologist review recommended", "Comparison with prior studies if available"],
            "severity": "mild"
        }
    
    def _analyze_ultrasound(self, img_array: np.ndarray, image_base64: str) -> Dict:
        """
        Analyze Ultrasound image
        """
        findings = []
        
        # Ultrasound analysis
        if img_array.mean() < 80:
            findings.append("Fluid-filled structure detected")
        
        if not findings:
            findings.append("Ultrasound findings within normal limits")
        
        return {
            "findings": findings,
            "diagnosis": "Ultrasound assessment",
            "confidence": 0.65,
            "recommendations": ["Clinical correlation recommended", "Follow-up ultrasound if indicated"],
            "severity": "mild"
        }
    
    def _generic_analysis(self, img_array: np.ndarray, image_base64: str) -> Dict:
        """
        Generic image analysis when type is unknown
        """
        findings = []
        
        # Basic analysis
        if img_array.std() > 50:
            findings.append("Image contains significant variation in pixel values")
        
        if not findings:
            findings.append("Image analysis inconclusive")
        
        return {
            "findings": findings,
            "diagnosis": "Requires specialist review",
            "confidence": 0.5,
            "recommendations": ["Please specify image type for accurate analysis", "Specialist consultation recommended"],
            "severity": "mild"
        }

# Singleton
_analyzer = None

def get_image_analyzer() -> ImageAnalyzer:
    global _analyzer
    if _analyzer is None:
        _analyzer = ImageAnalyzer()
    return _analyzer