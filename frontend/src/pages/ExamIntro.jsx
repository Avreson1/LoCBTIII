import React from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

const ExamIntro = () => {
  const navigate = useNavigate();
  const student = JSON.parse(localStorage.getItem('student') || '{}');

  return (
    <div className="flex items-center justify-center h-screen bg-gray-50">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-2xl w-full bg-white p-10 rounded-xl shadow-lg"
      >
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Welcome, {student.name || 'Student'}</h1>
        <div className="space-y-4 text-gray-600 text-lg mb-8">
          <p>Please read the following instructions carefully:</p>
          <ul className="list-disc list-inside space-y-2 ml-4">
            <li>Ensure you have a stable connection.</li>
            <li><strong>Do not switch tabs</strong> or minimize the browser. This will be logged.</li>
            <li>The exam will auto-submit when the timer reaches zero.</li>
            <li>Click "Finish Exam" when you are done.</li>
          </ul>
        </div>

        <button
          onClick={() => navigate('/exam/active')}
          className="w-full py-4 bg-green-600 text-white text-xl font-bold rounded-lg hover:bg-green-700 transition"
        >
          I am ready to start
        </button>
      </motion.div>
    </div>
  );
};

export default ExamIntro;
