import React, { useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';

const DashboardLayout = () => {
  useEffect(() => {
    const handleAuthFail = () => window.location.replace('/login');
    window.addEventListener('auth-failed', handleAuthFail);
    return () => window.removeEventListener('auth-failed', handleAuthFail);
  }, []);

  return (
    <div className="flex min-h-screen bg-background relative overflow-hidden">
      {/* Ambient blobs — subtle background glow */}
      <div className="pointer-events-none fixed -top-48 -left-48 w-[500px] h-[500px] rounded-full bg-violet-600/10 blur-[120px]" />
      <div className="pointer-events-none fixed top-1/2 -right-64 w-[400px] h-[400px] rounded-full bg-blue-600/8 blur-[100px]" />
      <div className="pointer-events-none fixed -bottom-48 left-1/3 w-[350px] h-[350px] rounded-full bg-purple-600/8 blur-[100px]" />

      {/* Sidebar */}
      <Sidebar />

      {/* Main content */}
      <main className="flex-1 h-screen overflow-y-auto">
        <div className="max-w-7xl mx-auto px-8 py-8 animate-[fadeIn_0.4s_ease-out]">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default DashboardLayout;
