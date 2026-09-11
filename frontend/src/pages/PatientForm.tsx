import React, { useState } from 'react';
import { apiClient } from '../services/api';

const PatientForm: React.FC<any> = ({ onAdd, patients }) => {
  const [formData, setFormData] = useState({
    name: '',
    age: '',
    gender: 'M',
    email: '',
    phone: '',
    allergies: '',
    chronic_diseases: '',
    current_medications: '',
  });

  const handleChange = (e: any) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e: any) => {
    e.preventDefault();
    
    try {
      const patient = {
        ...formData,
        age: parseInt(formData.age),
        allergies: formData.allergies.split(',').map(s => s.trim()),
        chronic_diseases: formData.chronic_diseases.split(',').map(s => s.trim()),
        current_medications: formData.current_medications.split(',').map(s => s.trim()),
      };

      // Try online first, fallback to offline
      let newPatient;
      try {
        newPatient = await apiClient.createPatient(patient);
      } catch (error) {
        // Offline fallback
        newPatient = {
          id: Date.now(),
          ...patient,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        };
      }

      onAdd([...patients, newPatient]);
      setFormData({
        name: '',
        age: '',
        gender: 'M',
        email: '',
        phone: '',
        allergies: '',
        chronic_diseases: '',
        current_medications: '',
      });
      alert('Patient added successfully!');
    } catch (error) {
      console.error('Error:', error);
      alert('Error adding patient');
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white rounded-lg shadow-lg p-8">
        <h2 className="text-3xl font-bold mb-6 text-blue-600">➕ New Patient</h2>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <input
              type="text"
              name="name"
              placeholder="Full Name"
              value={formData.name}
              onChange={handleChange}
              required
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
            />
            
            <input
              type="number"
              name="age"
              placeholder="Age"
              value={formData.age}
              onChange={handleChange}
              required
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
            />
            
            <select
              name="gender"
              value={formData.gender}
              onChange={handleChange}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
            >
              <option value="M">Male</option>
              <option value="F">Female</option>
              <option value="O">Other</option>
            </select>
            
            <input
              type="email"
              name="email"
              placeholder="Email (optional)"
              value={formData.email}
              onChange={handleChange}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
            />
          </div>
          
          <input
            type="tel"
            name="phone"
            placeholder="Phone (optional)"
            value={formData.phone}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
          />
          
          <textarea
            name="allergies"
            placeholder="Allergies (comma separated)"
            value={formData.allergies}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 h-20"
          />
          
          <textarea
            name="chronic_diseases"
            placeholder="Chronic Diseases (comma separated)"
            value={formData.chronic_diseases}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 h-20"
          />
          
          <textarea
            name="current_medications"
            placeholder="Current Medications (comma separated)"
            value={formData.current_medications}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 h-20"
          />
          
          <button
            type="submit"
            className="w-full bg-blue-600 text-white font-bold py-3 rounded-lg hover:bg-blue-700 transition"
          >
            ✅ Add Patient
          </button>
        </form>
      </div>
    </div>
  );
};

export default PatientForm;