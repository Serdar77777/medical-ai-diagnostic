import React from 'react';

const Dashboard: React.FC<any> = ({ patients }) => {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg shadow-lg p-8">
        <h1 className="text-4xl font-bold mb-2">🏥 Medical AI Diagnostic System</h1>
        <p className="text-lg opacity-90">Offline-capable medical diagnosis platform with AI-powered analysis</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <p className="text-gray-600 text-sm mb-2">👥 Total Patients</p>
          <p className="text-4xl font-bold text-blue-600">{patients.length}</p>
        </div>
        <div className="bg-white rounded-lg shadow-lg p-6">
          <p className="text-gray-600 text-sm mb-2">📊 Analyses Performed</p>
          <p className="text-4xl font-bold text-green-600">0</p>
        </div>
        <div className="bg-white rounded-lg shadow-lg p-6">
          <p className="text-gray-600 text-sm mb-2">💾 Offline Storage</p>
          <p className="text-4xl font-bold text-orange-600">Active</p>
        </div>
      </div>

      {/* Features */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition">
          <div className="text-4xl mb-3">🧪</div>
          <h3 className="text-xl font-bold mb-2">Blood Analysis</h3>
          <p className="text-gray-600">AI-powered analysis of blood test results with disease predictions</p>
        </div>
        <div className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition">
          <div className="text-4xl mb-3">🖼️</div>
          <h3 className="text-xl font-bold mb-2">Image Recognition</h3>
          <p className="text-gray-600">Analyze X-rays, MRI, CT scans, and ultrasound images</p>
        </div>
        <div className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition">
          <div className="text-4xl mb-3">💊</div>
          <h3 className="text-xl font-bold mb-2">Drug Interactions</h3>
          <p className="text-gray-600">Check drug interactions and contraindications instantly</p>
        </div>
        <div className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition">
          <div className="text-4xl mb-3">📴</div>
          <h3 className="text-xl font-bold mb-2">Offline Ready</h3>
          <p className="text-gray-600">Works completely offline with automatic sync when online</p>
        </div>
      </div>

      {/* Recent Patients */}
      {patients.length > 0 && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-bold mb-4">👥 Recent Patients</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Name</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Age</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Gender</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Added</th>
                </tr>
              </thead>
              <tbody>
                {patients.slice(0, 5).map((patient: any) => (
                  <tr key={patient.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3 px-4">{patient.name}</td>
                    <td className="py-3 px-4">{patient.age}</td>
                    <td className="py-3 px-4">{patient.gender}</td>
                    <td className="py-3 px-4 text-sm text-gray-600">
                      {new Date(patient.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;