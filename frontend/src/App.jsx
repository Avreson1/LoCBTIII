import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import AdminLogin from './pages/AdminLogin';
import AdminLayout from './layouts/AdminLayout';
import Dashboard from './pages/Dashboard';
import StudentLogin from './pages/StudentLogin';
import ExamIntro from './pages/ExamIntro';
import ExamInterface from './pages/ExamInterface';
import LicenseGate from './LicenseGate';

function App() {
  return (
    <LicenseGate>
      <Router>
        <Routes>
          <Route path="/" element={<StudentLogin />} />
          <Route path="/exam/intro" element={<ExamIntro />} />
          <Route path="/exam/active" element={<ExamInterface />} />

          <Route path="/admin" element={<AdminLogin />} />
          <Route path="/admin/dashboard" element={<AdminLayout />}>
            <Route index element={<Dashboard />} />
          </Route>
        </Routes>
      </Router>
    </LicenseGate>
  );
}

export default App;
