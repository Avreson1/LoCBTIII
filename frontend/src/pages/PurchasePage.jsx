import React, { useState } from 'react';
import axios from 'axios';
import { ShieldAlert, CreditCard, Key } from 'lucide-react';
import { motion } from 'framer-motion';

const PurchasePage = ({ onActivated }) => {
  const [step, setStep] = useState('purchase'); // purchase, key
  const [licenseKey, setLicenseKey] = useState('');
  const [inputKey, setInputKey] = useState('');
  const [error, setError] = useState('');

  const handleBuy = async () => {
    try {
      const res = await axios.post('http://localhost:8000/api/payment/mock');
      setLicenseKey(res.data.license_key);
      setInputKey(res.data.license_key);
      setStep('key');
    } catch (err) {
      alert('Payment failed');
    }
  };

  const handleActivate = async () => {
    try {
      const res = await axios.post('http://localhost:8000/api/license/activate', { key: inputKey });
      if (res.data.success) {
        alert('Activation Successful! Refreshing...');
        window.location.reload();
      }
    } catch (err) {
      setError('Invalid Key');
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="max-w-md w-full bg-white rounded-2xl shadow-2xl overflow-hidden"
      >
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-6 text-center">
          <ShieldAlert className="w-16 h-16 text-white mx-auto mb-2" />
          <h1 className="text-2xl font-bold text-white">License Required</h1>
          <p className="text-blue-100">Activate LoCBT to continue</p>
        </div>

        <div className="p-8">
          {step === 'purchase' ? (
            <div className="space-y-6">
              <div className="text-center space-y-2">
                <h3 className="text-lg font-semibold">Standard License</h3>
                <p className="text-4xl font-bold text-gray-800">$49.99</p>
                <p className="text-gray-500 text-sm">One-time purchase. Lifetime updates.</p>
              </div>

              <button
                onClick={handleBuy}
                className="w-full flex items-center justify-center py-3 bg-gray-900 text-white rounded-xl font-bold hover:bg-gray-800 transition"
              >
                <CreditCard className="w-5 h-5 mr-2" />
                Pay Now
              </button>

              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-300"></div>
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-2 bg-white text-gray-500">Already have a key?</span>
                </div>
              </div>

              <button
                onClick={() => setStep('key')}
                className="w-full py-2 text-blue-600 hover:text-blue-800 font-medium"
              >
                Enter License Key
              </button>
            </div>
          ) : (
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Enter License Key</label>
                <div className="relative">
                  <Key className="absolute left-3 top-3 text-gray-400 w-5 h-5" />
                  <input
                    type="text"
                    value={inputKey}
                    onChange={(e) => setInputKey(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 outline-none font-mono"
                    placeholder="XXXX-XXXX-XXXX-XXXX"
                  />
                </div>
                {error && <p className="text-red-500 text-sm mt-1">{error}</p>}
              </div>

              <button
                onClick={handleActivate}
                className="w-full py-3 bg-green-600 text-white rounded-xl font-bold hover:bg-green-700 transition"
              >
                Activate System
              </button>

              <button
                onClick={() => setStep('purchase')}
                className="w-full text-gray-500 text-sm hover:text-gray-700"
              >
                Back to Payment
              </button>
            </div>
          )}
        </div>
      </motion.div>
    </div>
  );
};

export default PurchasePage;
