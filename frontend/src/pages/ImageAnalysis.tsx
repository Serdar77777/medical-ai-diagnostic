import React, { useState } from 'react';
import { apiClient } from '../services/api';

const ImageAnalysis: React.FC<any> = ({ patients }) => {
  const [selectedPatient, setSelectedPatient] = useState('');
  const [imageType, setImageType] = useState('xray');
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [preview, setPreview] = useState('');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleFileSelect = (e: any) => {
    const file = e.target.files[0];
    if (file) {
      setImageFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleAnalyze = async () => {
    if (!selectedPatient || !imageFile) {
      alert('Please select patient and image');
      return;
    }

    setLoading(true);
    try {
      const reader = new FileReader();
      reader.onload = async () => {
        const base64 = (reader.result as string).split(',')[1];
        const response = await apiClient.analyzeImage({
          patient_id: parseInt(selectedPatient),
          image_type: imageType,
          image_base64: base64,
        });
        setResult(response);
      };
      reader.readAsDataURL(imageFile);
    } catch (error) {
      console.error('Error:', error);
      alert('Error analyzing image');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-6">
      {/* Upload Section */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold mb-4 text-blue-600">🖼️ Image Analysis</h2>
        
        <div className="space-y-4">
          <select
            value={selectedPatient}
            onChange={(e) => setSelectedPatient(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
          >
            <option value="">-- Select Patient --</option>
            {patients.map((p: any) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>

          <select
            value={imageType}
            onChange={(e) => setImageType(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
          >
            <option value="xray">X-Ray</option>
            <option value="mri">MRI</option>
            <option value="ct">CT Scan</option>
            <option value="ultrasound">Ultrasound</option>
          </select>

          <div className="border-2 border-dashed border-blue-300 rounded-lg p-6 text-center cursor-pointer hover:border-blue-500 transition">
            <input
              type="file"
              accept="image/*"
              onChange={handleFileSelect}
              className="hidden"
              id="imageInput"
            />
            <label htmlFor="imageInput" className="cursor-pointer">
              {preview ? (
                <img src={preview} alt="Preview" className="max-h-48 mx-auto rounded" />
              ) : (
                <div>
                  <p className="text-3xl mb-2">📸</p>
                  <p className="text-gray-600">Click to upload image</p>
                </div>
              )}
            </label>
          </div>

          <button
            onClick={handleAnalyze}
            disabled={loading || !imageFile}
            className="w-full bg-green-600 text-white font-bold py-3 rounded-lg hover:bg-green-700 transition disabled:bg-gray-400"
          >
            {loading ? '⏳ Analyzing...' : '✅ Analyze Image'}
          </button>
        </div>
      </div>

      {/* Results Section */}
      {result && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-2xl font-bold mb-4 text-blue-600">📋 Results</h3>
          
          <div className="space-y-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600">Diagnosis</p>
              <p className="text-xl font-bold text-blue-600">{result.diagnosis}</p>
              <p className="text-sm text-gray-600 mt-1">
                Confidence: {(result.confidence * 100).toFixed(1)}%
              </p>
            </div>

            <div>
              <p className="text-sm font-semibold text-gray-700 mb-2">Findings</p>
              <ul className="space-y-1">
                {result.findings?.map((finding: string, idx: number) => (
                  <li key={idx} className="text-sm text-gray-700">• {finding}</li>
                ))}
              </ul>
            </div>

            <div>
              <p className="text-sm font-semibold text-gray-700 mb-2">Recommendations</p>
              <ul className="space-y-1">
                {result.recommendations?.map((rec: string, idx: number) => (
                  <li key={idx} className="text-sm text-gray-700 flex items-start gap-2">
                    <span className="text-green-600">✓</span>
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

export default ImageAnalysis;