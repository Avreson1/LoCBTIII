import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

const StudentLogin = () => {
  const [studentId, setStudentId] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://localhost:8000/api/student/login', {
        student_id: studentId
      });
      if (response.data.success) {
        localStorage.setItem('student', JSON.stringify(response.data.student));
        navigate('/exam/intro');
      }
    } catch (err) {
      setError('Invalid Student ID');
    }
  };

  return (
    <div className="flex items-center justify-center h-screen bg-blue-50">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-md p-8 space-y-6 bg-white rounded-xl shadow-2xl"
      >
        <div className="text-center">
          <h1 className="text-3xl font-extrabold text-blue-900">CBT Exam</h1>
          <p className="mt-2 text-gray-500">Enter your Student ID to begin</p>
        </div>
        {error && <div className="p-3 text-sm text-red-600 bg-red-100 rounded">{error}</div>}
        <form onSubmit={handleLogin} className="space-y-6">
          <div>
            <input
              type="text"
              placeholder="e.g. S001"
              value={studentId}
              onChange={(e) => setStudentId(e.target.value)}
              className="w-full px-4 py-3 text-lg border-2 border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
            />
          </div>
          <button
            type="submit"
            className="w-full px-4 py-3 text-lg font-bold text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition shadow-lg hover:shadow-xl"
          >
            Start Exam
          </button>
        </form>
      </motion.div>
    </div>
  );
};

export default StudentLogin;
