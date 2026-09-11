from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database.db import Base

class Patient(Base):
    """Patient model"""
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer)
    gender = Column(String(10))  # M/F/Other
    email = Column(String(100), unique=True, index=True)
    phone = Column(String(20))
    allergies = Column(JSON, default=[])
    chronic_diseases = Column(JSON, default=[])
    current_medications = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    diagnoses = relationship("Diagnosis", back_populates="patient")
    blood_tests = relationship("BloodTest", back_populates="patient")
    images = relationship("MedicalImage", back_populates="patient")

class BloodTest(Base):
    """Blood test results model"""
    __tablename__ = "blood_tests"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False, index=True)
    
    # Blood test values
    hemoglobin = Column(Float)  # g/L
    hematocrit = Column(Float)  # %
    red_blood_cells = Column(Float)  # M/µL
    white_blood_cells = Column(Float)  # K/µL
    platelets = Column(Float)  # K/µL
    glucose = Column(Float)  # mg/dL
    creatinine = Column(Float)  # mg/dL
    urea = Column(Float)  # mg/dL
    sodium = Column(Float)  # mEq/L
    potassium = Column(Float)  # mEq/L
    chloride = Column(Float)  # mEq/L
    
    # Additional fields
    raw_data = Column(JSON)  # Store all values
    test_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    patient = relationship("Patient", back_populates="blood_tests")
    diagnosis = relationship("Diagnosis", back_populates="blood_test", uselist=False)

class MedicalImage(Base):
    """Medical image model (X-ray, MRI, CT, etc.)"""
    __tablename__ = "medical_images"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False, index=True)
    image_type = Column(String(50))  # xray, mri, ct, ultrasound
    image_path = Column(String(255), nullable=False)
    image_data = Column(Text)  # Base64 encoded
    upload_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    patient = relationship("Patient", back_populates="images")
    diagnosis = relationship("Diagnosis", back_populates="medical_image", uselist=False)

class Diagnosis(Base):
    """Diagnosis model"""
    __tablename__ = "diagnoses"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False, index=True)
    blood_test_id = Column(Integer, nullable=True)
    image_id = Column(Integer, nullable=True)
    
    # Diagnosis results
    primary_diagnosis = Column(String(200))
    primary_probability = Column(Float)  # 0-1
    secondary_diagnoses = Column(JSON, default=[])  # List of {name, probability}
    severity = Column(String(50))  # mild, moderate, severe
    
    # AI Analysis
    ai_findings = Column(Text)  # Raw AI findings
    ai_confidence = Column(Float)  # Confidence score
    ai_model_used = Column(String(50))  # blood_analyzer, image_analyzer, etc.
    
    # Recommendations
    recommended_tests = Column(JSON, default=[])
    recommended_treatments = Column(JSON, default=[])
    specialist_referral = Column(String(100))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    doctor_notes = Column(Text)
    
    # Relationships
    patient = relationship("Patient", back_populates="diagnoses")
    blood_test = relationship("BloodTest", back_populates="diagnosis")
    medical_image = relationship("MedicalImage", back_populates="diagnosis")

class DrugInteraction(Base):
    """Drug interaction model"""
    __tablename__ = "drug_interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    drug1 = Column(String(100), nullable=False)
    drug2 = Column(String(100), nullable=False)
    interaction_type = Column(String(50))  # major, moderate, minor
    description = Column(Text)
    is_contraindicated = Column(Boolean, default=False)