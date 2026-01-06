import React from 'react';
import TestManager from '../components/TestManager';
import ResultsView from '../components/ResultsView';

const Dashboard = () => {
  return (
    <div className="space-y-6">
      <TestManager />
      <ResultsView />
    </div>
  );
};

export default Dashboard;
