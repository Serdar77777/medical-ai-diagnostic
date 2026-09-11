# 🏥 Medical AI Diagnostic System

**Complete offline medical diagnosis system with AI-powered analysis of blood tests and medical images**

## 🎯 Features

- ✅ **Blood Analysis Diagnosis** - AI analyzes lab results and suggests diagnoses
- ✅ **Medical Image Recognition** - X-ray, MRI, CT scan analysis
- ✅ **Offline AI** - Works completely offline with local LLaMA models
- ✅ **Doctor Interface** - React web app for medical professionals
- ✅ **Patient Database** - SQLite for storing patient history
- ✅ **Drug Interactions** - Checks for medicine contraindications
- ✅ **Report Generation** - PDF reports with diagnosis and recommendations

## 🛠️ Tech Stack

| Component | Technology | License |
|-----------|-----------|----------|
| **Backend** | FastAPI (Python) | Open Source ✅ |
| **Frontend** | React + TypeScript | Open Source ✅ |
| **AI Model** | LLaMA 2 / Mistral (Ollama) | Open Source ✅ |
| **Medical AI** | CheXpert + MONAI | Open Source ✅ |
| **Database** | SQLite / PostgreSQL | Open Source ✅ |
| **Drug Database** | DrugBank API | Free ✅ |

## 📦 Installation

### Prerequisites
- Python 3.10+
- Node.js 16+
- Ollama (download from https://ollama.ai)
- 8GB RAM minimum

### 1. Clone Repository
```bash
git clone https://github.com/Serdar77777/medical-ai-diagnostic.git
cd medical-ai-diagnostic
```

### 2. Setup Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Setup Frontend
```bash
cd frontend
npm install
npm run build
```

### 4. Install Ollama Models
```bash
ollama pull llama2
ollama pull mistral
```

### 5. Run System
```bash
# Terminal 1 - Backend
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm start
```

## 🚀 Usage

### For Doctors

#### 1. **Blood Analysis Diagnosis**
```
Input:
- Hemoglobin: 140 g/L
- Leukocytes: 8.5 K/µL
- Platelets: 250 K/µL
- Glucose: 145 mg/dL

Output:
- Primary Diagnosis: Mild Anemia (65%)
- Secondary: Hyperglycemia (25%)
- Tertiary: Infection (10%)
- Recommendations: Iron test, Endocrinology consultation
```

#### 2. **Medical Image Analysis**
```
Upload X-ray/MRI → AI analyzes → Reports findings
- Pneumonia detection
- Tumor detection
- Fracture detection
```

#### 3. **Drug Interactions**
```
Check if medicines interact safely
- Auto cross-check with patient allergies
- Warning flags for dangerous combinations
```

## 📊 Project Structure

```
medical-ai-diagnostic/
├── backend/
│   ├── main.py                 # FastAPI app
│   ├── models/
│   │   ├── blood_analyzer.py   # Blood test analysis
│   │   ├── image_analyzer.py   # Image recognition
│   │   └── diagnosis_engine.py # Diagnosis logic
│   ├── database/
│   │   ├── models.py           # SQLAlchemy models
│   │   └── schemas.py          # Pydantic schemas
│   ├── llm/
│   │   └── ollama_integration.py  # LLaMA integration
│   ├── utils/
│   │   ├── drug_checker.py     # Drug interactions
│   │   └── report_generator.py # PDF reports
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── BloodAnalysis.tsx
│   │   │   ├── ImageUpload.tsx
│   │   │   ├── PatientForm.tsx
│   │   │   └── DiagnosisResult.tsx
│   │   ├��─ pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── PatientHistory.tsx
│   │   │   └── Settings.tsx
│   │   ├── services/
│   │   │   └── api.ts
│   │   └── App.tsx
│   ├── package.json
│   └── tsconfig.json
│
├── models/
│   ├── blood_diagnosis_model.pkl  # ML model for blood analysis
│   ├── cnn_xray_model.h5          # CNN for X-ray recognition
│   └── drugbank_data.json         # Drug interactions database
│
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🔬 Diagnosis Workflow

```
1. Patient Data Entry
   ↓
2. Blood Analysis Input OR Image Upload
   ↓
3. AI Processing (Offline LLaMA)
   ↓
4. Disease Prediction & Analysis
   ↓
5. Drug Recommendation
   ↓
6. Contraindication Check
   ↓
7. Report Generation
   ↓
8. Save to Patient History
```

## 📋 API Endpoints

### Blood Analysis
```bash
POST /api/diagnosis/blood
{
  "patient_id": "123",
  "hemoglobin": 140,
  "leukocytes": 8.5,
  "platelets": 250,
  "glucose": 145,
  "creatinine": 1.0
}

Response:
{
  "diagnosis": [
    {"name": "Anemia", "probability": 0.65},
    {"name": "Hyperglycemia", "probability": 0.25}
  ],
  "recommendations": ["Iron test", "Consult endocrinologist"],
  "severity": "mild"
}
```

### Image Analysis
```bash
POST /api/diagnosis/image
multipart/form-data: image.jpg

Response:
{
  "findings": ["Infiltration in lower left lobe"],
  "diagnosis": "Possible pneumonia",
  "confidence": 0.92,
  "recommendations": ["CT scan for confirmation"]
}
```

### Patient History
```bash
GET /api/patients/{patient_id}/history
GET /api/patients
POST /api/patients
PUT /api/patients/{patient_id}
```

## 🤖 AI Models Used

### Blood Analysis
- **XGBoost** - Disease prediction from blood values
- **LLaMA 2** - Medical knowledge & interpretations

### Image Recognition
- **CheXpert** - Chest X-ray diagnosis
- **MONAI** - 3D medical image analysis
- **ResNet-50** - General image classification

## 📚 Medical Databases

- **DrugBank** - Drug interactions & contraindications
- **SNOMED CT** - Medical terminology
- **ICD-10** - Disease codes
- **RxNorm** - Medication classifications

## 🔐 Security & Privacy

- ✅ All processing happens offline (no cloud)
- ✅ Patient data stored locally (SQLite)
- ✅ No internet connection required
- ✅ HIPAA-compliant architecture
- ✅ Encrypted database option

## ⚠️ Disclaimer

**This is an AI-assisted tool for doctors. It should NOT be used as the sole basis for medical diagnosis. Always consult with qualified medical professionals.**

## 🤝 Contributing

Contributions welcome! Please read [CONTRIBUTING.md](./CONTRIBUTING.md)

## 📄 License

MIT License - See [LICENSE](./LICENSE)

---

**Made with ❤️ for healthcare professionals**