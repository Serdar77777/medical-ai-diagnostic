from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager

# Import routers
from routes.diagnosis import router as diagnosis_router
from routes.patients import router as patients_router
from routes.drugs import router as drugs_router
from database.db import init_db, SessionLocal
from llm.ollama_integration import OllamaLLM

load_dotenv()

# Global LLM instance
llm_instance = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global llm_instance
    init_db()
    llm_instance = OllamaLLM()
    print("✅ Medical AI Diagnostic System Started")
    print("📊 Ollama LLM loaded successfully")
    yield
    # Shutdown
    print("🛑 System shutting down...")

app = FastAPI(
    title="Medical AI Diagnostic System",
    description="Offline AI-powered medical diagnosis system for doctors",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(diagnosis_router, prefix="/api/diagnosis", tags=["Diagnosis"])
app.include_router(patients_router, prefix="/api/patients", tags=["Patients"])
app.include_router(drugs_router, prefix="/api/drugs", tags=["Drugs"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Medical AI Diagnostic System",
        "version": "1.0.0",
        "status": "online",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "llm": "ready" if llm_instance else "initializing",
        "database": "connected"
    }

@app.get("/api/models")
async def get_models():
    """Get available AI models info"""
    return {
        "blood_analysis": {
            "name": "XGBoost Disease Predictor",
            "version": "1.0",
            "status": "ready"
        },
        "image_analysis": {
            "name": "CheXpert X-Ray Analyzer",
            "version": "1.0",
            "status": "ready"
        },
        "llm": {
            "name": "LLaMA 2",
            "version": "7B",
            "status": "ready" if llm_instance else "loading"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)