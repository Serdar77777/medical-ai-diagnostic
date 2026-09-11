import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import PatientForm from './pages/PatientForm';
import BloodAnalysis from './pages/BloodAnalysis';
import ImageAnalysis from './pages/ImageAnalysis';
import PatientHistory from './pages/PatientHistory';
import { useOfflineDetection } from './hooks/useOfflineDetection';
import './App.css';

function App() {
  const isOnline = useOfflineDetection();
  const [patients, setPatients] = useState([]);

  useEffect(() => {
    // Load patients from localStorage
    const saved = localStorage.getItem('patients');
    if (saved) {
      setPatients(JSON.parse(saved));
    }
  }, []);

  useEffect(() => {
    // Save patients to localStorage whenever they change
    localStorage.setItem('patients', JSON.stringify(patients));
  }, [patients]);

  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        {/* Header */}
        <header className="bg-white shadow-lg sticky top-0 z-50">
          <div className="container mx-auto px-4 py-4">
            <div className="flex justify-between items-center">
              <Link to="/" className="flex items-center gap-2">
                <span className="text-3xl">🏥</span>
                <h1 className="text-2xl font-bold text-blue-600">Medical AI</h1>
              </Link>
              
              {/* Online/Offline Status */}
              <div className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${
                  isOnline ? 'bg-green-500' : 'bg-red-500'
                }`}></div>
                <span className="text-sm font-semibold">
                  {isOnline ? '🌐 Online' : '📴 Offline'}
                </span>
              </div>
            </div>
          </div>
        </header>

        {/* Navigation */}
        <nav className="bg-blue-600 text-white shadow-md">
          <div className="container mx-auto px-4">
            <div className="flex gap-6 overflow-x-auto py-3">
              <Link to="/" className="hover:text-blue-200 transition whitespace-nowrap">Dashboard</Link>
              <Link to="/patients/new" className="hover:text-blue-200 transition whitespace-nowrap">+ New Patient</Link>
              <Link to="/blood-analysis" className="hover:text-blue-200 transition whitespace-nowrap">Blood Analysis</Link>
              <Link to="/image-analysis" className="hover:text-blue-200 transition whitespace-nowrap">Image Analysis</Link>
              <Link to="/history" className="hover:text-blue-200 transition whitespace-nowrap">History</Link>
            </div>
          </div>
        </nav>

        {/* Offline Warning */}
        {!isOnline && (
          <div className="bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 p-4 m-4 rounded">
            <p className="font-bold">⚠️ Offline Mode</p>
            <p className="text-sm">Working offline. Data will sync when connection is restored.</p>
          </div>
        )}

        {/* Main Content */}
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Dashboard patients={patients} />} />
            <Route path="/patients/new" element={<PatientForm onAdd={setPatients} patients={patients} />} />
            <Route path="/blood-analysis" element={<BloodAnalysis patients={patients} />} />
            <Route path="/image-analysis" element={<ImageAnalysis patients={patients} />} />
            <Route path="/history" element={<PatientHistory patients={patients} />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;