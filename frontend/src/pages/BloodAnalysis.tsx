import React, { useState } from 'react';
import { apiClient } from '../services/api';

const BloodAnalysis: React.FC<any> = ({ patients }) => {
  const [selectedPatient, setSelectedPatient] = useState('');
  const [bloodValues, setBloodValues] = useState({
    hemoglobin: '',
    leukocytes: '',
    platelets: '',
    glucose: '',
    creatinine: '',
  });
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleInputChange = (e: any) => {
    const { name, value } = e.target;
    setBloodValues(prev => ({
      ...prev,
      [name]: value ? parseFloat(value) : '',
    }));
  };

  const handleAnalyze = async () => {
    if (!selectedPatient) {
      alert('Please select a patient');
      return;
    }

    setLoading(true);
    try {
      const response = await apiClient.analyzeBloodTest({
        patient_id: parseInt(selectedPatient),
        ...bloodValues,
      });
      setResult(response);
    } catch (error) {
      console.error('Error:', error);
      alert('Error analyzing blood test');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-6">
      {/* Input Section */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold mb-4 text-blue-600">🧪 Blood Analysis</h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-semibold mb-2">Select Patient</label>
            <select
              value={selectedPatient}
              onChange={(e) => setSelectedPatient(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
            >
              <option value="">-- Select Patient --</option>
              {patients.map((p: any) => (
                <option key={p.id} value={p.id}>
                  {p.name} (ID: {p.id})
                </option>
              ))}
            </select>
          </div>

          {[
            { name: 'hemoglobin', label: 'Hemoglobin (g/L)', min: 0, max: 200 },
            { name: 'leukocytes', label: 'Leukocytes (K/µL)', min: 0, max: 30 },
            { name: 'platelets', label: 'Platelets (K/µL)', min: 0, max: 1000 },
            { name: 'glucose', label: 'Glucose (mg/dL)', min: 0, max: 500 },
            { name: 'creatinine', label: 'Creatinine (mg/dL)', min: 0, max: 10 },
          ].map(field => (
            <input
              key={field.name}
              type="number"
              name={field.name}
              placeholder={field.label}
              value={bloodValues[field.name as keyof typeof bloodValues]}
              onChange={handleInputChange}
              min={field.min}
              max={field.max}
              step="0.1"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
            />
          ))}

          <button
            onClick={handleAnalyze}
            disabled={loading}
            className="w-full bg-green-600 text-white font-bold py-3 rounded-lg hover:bg-green-700 transition disabled:bg-gray-400"
          >
            {loading ? '⏳ Analyzing...' : '✅ Analyze'}
          </button>
        </div>
      </div>

      {/* Results Section */}
      {result && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-2xl font-bold mb-4 text-blue-600">📊 Results</h3>
          
          <div className="space-y-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600">Primary Diagnosis</p>
              <p className="text-2xl font-bold text-blue-600">{result.primary_diagnosis}</p>
              <p className="text-sm text-gray-600 mt-1">
                Probability: {(result.primary_probability * 100).toFixed(1)}%
              </p>
            </div>

            <div className="bg-yellow-50 p-4 rounded-lg">
              <p className="text-sm font-semibold text-gray-700 mb-2">Severity</p>
              <span className={`px-3 py-1 rounded-full text-sm font-bold ${
                result.severity === 'severe' ? 'bg-red-200 text-red-800' :
                result.severity === 'moderate' ? 'bg-yellow-200 text-yellow-800' :
                'bg-green-200 text-green-800'
              }`}>
                {result.severity.toUpperCase()}
              </span>
            </div>

            <div>
              <p className="text-sm font-semibold text-gray-700 mb-2">Recommendations</p>
              <ul className="space-y-2">
                {result.recommended_tests?.map((rec: string, idx: number) => (
                  <li key={idx} className="text-sm text-gray-700 flex items-start gap-2">
                    <span className="text-green-600 mt-1">✓</span>
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default BloodAnalysis;