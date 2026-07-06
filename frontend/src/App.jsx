import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import DashboardLayout from './components/layout/DashboardLayout';
import ProtectedRoute from './components/layout/ProtectedRoute';
import { AuthProvider } from './context/AuthContext';
import Login from './pages/Login';
import Projects from './pages/Projects';
import ProjectDetail from './pages/ProjectDetail';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          
          <Route element={<ProtectedRoute />}>
            <Route element={<DashboardLayout />}>
              <Route path="/" element={<Navigate to="/projects" replace />} />
              <Route path="/projects" element={<Projects />} />
              <Route path="/projects/:id" element={<ProjectDetail />} />
              <Route path="/knowledge" element={<div className="glass-panel p-12 text-center h-[calc(100vh-8rem)] flex flex-col items-center justify-center"><h3 className="text-xl font-bold mb-2">Global Knowledge Base</h3><p className="text-gray-500 max-w-md">To manage documents, please select a specific Workspace from the Projects tab. A global document view is coming soon.</p></div>} />
              <Route path="/analytics" element={<div className="glass-panel p-8 h-[calc(100vh-8rem)]">Analytics Coming Soon</div>} />
              <Route path="/settings" element={<div className="glass-panel p-8 h-[calc(100vh-8rem)]">Settings Coming Soon</div>} />
            </Route>
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
