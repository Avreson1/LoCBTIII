import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Upload, FileText, CheckCircle, Circle } from 'lucide-react';

const TestManager = () => {
  const [tests, setTests] = useState([]);
  const [uploading, setUploading] = useState(false);

  const fetchTests = async () => {
    try {
      const res = await axios.get('http://localhost:8000/api/admin/tests');
      setTests(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchTests();
  }, []);

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', file.name.replace('.docx', ''));

    setUploading(true);
    try {
      await axios.post('http://localhost:8000/api/admin/upload-test', formData);
      fetchTests();
    } catch (err) {
      alert('Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const handlePublish = async (id) => {
    try {
      await axios.post(`http://localhost:8000/api/admin/tests/${id}/publish`);
      fetchTests();
    } catch (err) {
      alert('Publish failed');
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow mb-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold text-gray-800">Manage Tests</h2>
        <div className="relative">
          <input
            type="file"
            accept=".docx"
            onChange={handleUpload}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          />
          <button className="flex items-center px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
            <Upload className="w-4 h-4 mr-2" />
            {uploading ? 'Uploading...' : 'Upload Test (.docx)'}
          </button>
        </div>
      </div>

      <div className="space-y-3">
        {tests.map(test => (
          <div key={test.id} className="flex justify-between items-center p-3 border rounded hover:bg-gray-50">
            <div className="flex items-center">
              <FileText className="w-5 h-5 text-gray-500 mr-3" />
              <div>
                <p className="font-medium">{test.title}</p>
                <p className="text-sm text-gray-500">{test.duration_minutes} mins</p>
              </div>
            </div>
            <button
              onClick={() => handlePublish(test.id)}
              className={`flex items-center px-3 py-1 rounded text-sm ${
                test.is_active
                  ? 'bg-green-100 text-green-800'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {test.is_active ? <CheckCircle className="w-4 h-4 mr-1" /> : <Circle className="w-4 h-4 mr-1" />}
              {test.is_active ? 'Active' : 'Set Active'}
            </button>
          </div>
        ))}
        {tests.length === 0 && <p className="text-gray-500 text-center">No tests found.</p>}
      </div>
    </div>
  );
};

export default TestManager;
