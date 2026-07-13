import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { confirmSocket } from '../websocket/client';

const StandaloneConfirm: React.FC = () => {
  const location = useLocation();
  const [token, setToken] = useState('');
  const [message, setMessage] = useState('');

  useEffect(() => {
    // Parse Hash URL params: #/confirm?token=123&message=Delete%20File
    const searchParams = new URLSearchParams(location.hash.split('?')[1]);
    setToken(searchParams.get('token') || '');
    setMessage(searchParams.get('message') || 'Unknown Action');
    
    confirmSocket.connect();
  }, [location]);

  const handleResolve = (approved: boolean) => {
    // 1. Send resolution to backend
    confirmSocket.send({ token, approved });
    
    // 2. Tell Electron to close this standalone OS window
    setTimeout(() => {
      window.electronAPI.closeConfirmationWindow();
    }, 100);
  };

  return (
    <div className="h-screen w-screen bg-zinc-950 flex flex-col items-center justify-center p-6 border border-red-500/30">
      <div className="app-region-drag absolute top-0 left-0 w-full h-8" />
      
      <div className="flex items-center space-x-3 text-red-400 mb-4">
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <h1 className="text-xl font-bold text-white">Tier 3 Action Requires Approval</h1>
      </div>
      
      <p className="text-zinc-300 text-center mb-8 max-w-sm">
        {message}
      </p>
      
      <div className="flex space-x-4 w-full px-4">
        <button 
          onClick={() => handleResolve(false)}
          className="flex-1 py-3 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-200 transition-colors font-medium"
        >
          Deny
        </button>
        <button 
          onClick={() => handleResolve(true)}
          className="flex-1 py-3 rounded-lg bg-red-600 hover:bg-red-500 text-white transition-colors font-medium shadow-lg shadow-red-500/20"
        >
          Approve Action
        </button>
      </div>
    </div>
  );
};

export default StandaloneConfirm;
