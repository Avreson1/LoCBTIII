import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Clock, AlertTriangle } from 'lucide-react';

const ExamInterface = () => {
  const [exam, setExam] = useState(null);
  const [currentQIndex, setCurrentQIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [timeLeft, setTimeLeft] = useState(0);
  const [tabWarnings, setTabWarnings] = useState(0);
  const navigate = useNavigate();
  const student = JSON.parse(localStorage.getItem('student') || '{}');

  useEffect(() => {
    // Fetch Exam
    const fetchExam = async () => {
      try {
        const res = await axios.get('http://localhost:8000/api/student/exam');
        setExam(res.data);
        setTimeLeft(res.data.duration * 60);
      } catch (err) {
        alert('Failed to load exam. Please ask proctor.');
      }
    };
    fetchExam();

    // Tab Focus Listener
    const handleVisibilityChange = () => {
      if (document.hidden) {
        setTabWarnings(prev => prev + 1);
        // Could also log this to backend immediately
      }
    };
    document.addEventListener("visibilitychange", handleVisibilityChange);
    return () => document.removeEventListener("visibilitychange", handleVisibilityChange);
  }, []);

  // Timer
  useEffect(() => {
    if (timeLeft <= 0) return;
    const timer = setInterval(() => {
      setTimeLeft(prev => {
        if (prev <= 1) {
          handleSubmit();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [timeLeft]);

  const handleSelect = (questionId, optionLabel) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: optionLabel
    }));
  };

  const handleSubmit = async () => {
    if (!exam) return;
    try {
      await axios.post('http://localhost:8000/api/student/submit', {
        student_id: student.id,
        test_id: exam.test_id,
        answers: answers
      });
      alert('Exam Submitted Successfully!');
      navigate('/');
    } catch (err) {
      alert('Submission failed. Try again.');
    }
  };

  if (!exam) return <div className="p-10 text-center">Loading Exam...</div>;

  const currentQ = exam.questions[currentQIndex];
  const progress = ((currentQIndex + 1) / exam.questions.length) * 100;

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50 overflow-hidden">
      {/* Header */}
      <header className="flex justify-between items-center px-6 py-4 bg-white shadow-sm z-10">
        <div>
          <h1 className="text-xl font-bold text-gray-800">{exam.title}</h1>
          <p className="text-sm text-gray-500">{student.name}</p>
        </div>

        {/* Timer & Warnings */}
        <div className="flex items-center space-x-6">
          {tabWarnings > 0 && (
            <div className="flex items-center text-red-600 font-bold animate-pulse">
              <AlertTriangle className="w-5 h-5 mr-1" />
              <span>Warning: Tab Switched ({tabWarnings})</span>
            </div>
          )}
          <div className="flex items-center text-2xl font-mono font-bold text-blue-700">
            <Clock className="w-6 h-6 mr-2" />
            {formatTime(timeLeft)}
          </div>
        </div>
      </header>

      {/* Progress Bar */}
      <div className="h-1 w-full bg-gray-200">
        <motion.div
          className="h-full bg-blue-600"
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
        />
      </div>

      {/* Main Content */}
      <main className="flex-1 flex items-center justify-center p-6 relative">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentQ.id}
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -50 }}
            transition={{ duration: 0.3 }}
            className="w-full max-w-4xl bg-white p-8 rounded-2xl shadow-xl"
          >
            <div className="mb-8">
              <span className="text-sm font-bold text-blue-500 uppercase tracking-wide">Question {currentQIndex + 1} of {exam.questions.length}</span>
              <h2 className="text-2xl font-medium text-gray-800 mt-2">{currentQ.text}</h2>
            </div>

            <div className="space-y-4">
              {currentQ.options.map((opt) => (
                <label
                  key={opt.label}
                  className={`flex items-center p-4 border-2 rounded-lg cursor-pointer transition-all ${
                    answers[currentQ.id] === opt.label
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <input
                    type="radio"
                    name={`q-${currentQ.id}`}
                    className="hidden"
                    checked={answers[currentQ.id] === opt.label}
                    onChange={() => handleSelect(currentQ.id, opt.label)}
                  />
                  <div className={`w-8 h-8 flex items-center justify-center rounded-full mr-4 border-2 ${
                     answers[currentQ.id] === opt.label
                      ? 'bg-blue-600 border-blue-600 text-white'
                      : 'border-gray-300 text-gray-500'
                  }`}>
                    {opt.label}
                  </div>
                  <span className="text-lg text-gray-700">{opt.text}</span>
                </label>
              ))}
            </div>
          </motion.div>
        </AnimatePresence>
      </main>

      {/* Footer Navigation */}
      <footer className="px-6 py-4 bg-white border-t flex justify-between items-center">
        <button
          onClick={() => setCurrentQIndex(prev => Math.max(0, prev - 1))}
          disabled={currentQIndex === 0}
          className="px-6 py-2 text-gray-600 font-medium disabled:opacity-50 hover:bg-gray-100 rounded-lg transition"
        >
          Previous
        </button>

        {currentQIndex === exam.questions.length - 1 ? (
          <button
            onClick={handleSubmit}
            className="px-8 py-2 bg-green-600 text-white font-bold rounded-lg hover:bg-green-700 transition shadow-lg hover:shadow-xl"
          >
            Submit Exam
          </button>
        ) : (
          <button
            onClick={() => setCurrentQIndex(prev => Math.min(exam.questions.length - 1, prev + 1))}
            className="px-8 py-2 bg-blue-600 text-white font-bold rounded-lg hover:bg-blue-700 transition shadow-lg hover:shadow-xl"
          >
            Next Question
          </button>
        )}
      </footer>
    </div>
  );
};

export default ExamInterface;
