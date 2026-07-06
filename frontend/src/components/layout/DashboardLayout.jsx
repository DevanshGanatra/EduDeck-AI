import React, { useEffect } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import Sidebar from './Sidebar';

const DashboardLayout = () => {
  const navigate = useNavigate();

  useEffect(() => {
    // Basic auth check
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
    }

    const handleAuthFail = () => navigate('/login');
    window.addEventListener('auth-failed', handleAuthFail);
    return () => window.removeEventListener('auth-failed', handleAuthFail);
  }, [navigate]);

  return (
    <div className="flex min-h-screen bg-gray-50/50 relative overflow-hidden">
      {/* Decorative Background Blobs */}
      <div className="absolute top-[-10%] left-[-10%] w-96 h-96 bg-brand-300/30 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-blob"></div>
      <div className="absolute top-[20%] right-[-5%] w-72 h-72 bg-blue-300/30 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-blob animation-delay-2000"></div>
      <div className="absolute bottom-[-10%] left-[20%] w-80 h-80 bg-purple-300/30 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-blob animation-delay-4000"></div>

      {/* Main Layout */}
      <Sidebar />
      <main className="flex-1 p-8 h-screen overflow-y-auto relative z-10">
        <div className="max-w-7xl mx-auto animate-fade-in">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default DashboardLayout;
