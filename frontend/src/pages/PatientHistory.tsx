import React from 'react';

const PatientHistory: React.FC<any> = ({ patients }) => {
  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-3xl font-bold mb-6 text-blue-600">📋 Patient History</h2>
      
      {patients.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-600 text-lg">No patients added yet</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-gray-100">
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Name</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Age</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Gender</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Email</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Phone</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Added Date</th>
              </tr>
            </thead>
            <tbody>
              {patients.map((patient: any) => (
                <tr key={patient.id} className="border-b border-gray-200 hover:bg-gray-50">
                  <td className="py-3 px-4 font-semibold">{patient.name}</td>
                  <td className="py-3 px-4">{patient.age}</td>
                  <td className="py-3 px-4">{patient.gender}</td>
                  <td className="py-3 px-4 text-gray-600">{patient.email || '-'}</td>
                  <td className="py-3 px-4 text-gray-600">{patient.phone || '-'}</td>
                  <td className="py-3 px-4 text-sm text-gray-500">
                    {new Date(patient.created_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default PatientHistory;