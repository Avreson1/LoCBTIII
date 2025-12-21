import React, { useState, useEffect } from 'react';
import axios from 'axios';

const ResultsView = () => {
  const [results, setResults] = useState([]);

  useEffect(() => {
    const fetchResults = async () => {
      try {
        const res = await axios.get('http://localhost:8000/api/admin/results');
        setResults(res.data);
      } catch (err) {
        console.error(err);
      }
    };
    fetchResults();
    // Poll every 5s for live updates
    const interval = setInterval(fetchResults, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h2 className="text-lg font-semibold text-gray-800 mb-4">Exam Results</h2>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Student</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Test</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Score</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {results.map((r, idx) => (
              <tr key={idx}>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{r.student_name}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{r.test_title}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-blue-600">{r.score} / {r.total}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{new Date(r.date).toLocaleString()}</td>
              </tr>
            ))}
            {results.length === 0 && (
              <tr>
                <td colSpan="4" className="px-6 py-4 text-center text-sm text-gray-500">No results yet.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ResultsView;
