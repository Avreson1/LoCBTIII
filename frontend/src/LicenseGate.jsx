import React, { useEffect, useState } from 'react';
import axios from 'axios';
import PurchasePage from './pages/PurchasePage';

const LicenseGate = ({ children }) => {
  const [status, setStatus] = useState('loading'); // loading, authorized, locked

  useEffect(() => {
    const checkLicense = async () => {
      try {
        // Try to hit a protected endpoint
        await axios.get('http://localhost:8000/api/admin/tests');
        setStatus('authorized');
      } catch (err) {
        if (err.response && err.response.status === 403 && err.response.data.code === 'LICENSE_REQUIRED') {
          setStatus('locked');
        } else if (err.response && err.response.status === 401) {
           // 401 means unauth, but license is present (otherwise middleware would 403)
           setStatus('authorized');
        } else {
           // Network error or server down, assume locked for safety or retry
           // For now, if we can't reach server, we can't verify license.
           setStatus('locked');
        }
      }
    };
    checkLicense();
  }, []);

  if (status === 'loading') {
    return <div className="flex items-center justify-center h-screen">Verifying License...</div>;
  }

  if (status === 'locked') {
    return <PurchasePage />;
  }

  return <>{children}</>;
};

export default LicenseGate;
