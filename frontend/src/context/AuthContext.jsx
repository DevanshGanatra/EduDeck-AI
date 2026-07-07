import React, { createContext, useContext, useState, useEffect } from 'react';
import apiClient from '../api/axios';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUser = async () => {
      if (!token) {
        setUser(null);
        setLoading(false);
        return;
      }
      try {
        // Use apiClient so we hit the correct backend URL (VITE_API_URL)
        const res = await apiClient.get('/auth/me');
        setUser(res.data.data);
      } catch (error) {
        // Token invalid/expired — clear it
        localStorage.removeItem('token');
        setToken(null);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };
    fetchUser();
  }, [token]);

  const login = async (email, password) => {
    try {
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      const res = await apiClient.post('/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });

      const accessToken = res.data.data.access_token;
      localStorage.setItem('token', accessToken);
      setToken(accessToken);
      return { success: true };
    } catch (err) {
      return { success: false, error: err.response?.data?.detail || err.response?.data?.message || 'Login failed' };
    }
  };

  const register = async (email, password, name) => {
    try {
      await apiClient.post('/auth/register', { email, password, name });
      return await login(email, password);
    } catch (err) {
      return { success: false, error: err.response?.data?.detail || err.response?.data?.message || 'Registration failed' };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  const refreshUser = async () => {
    if (!token) return;
    try {
      const res = await apiClient.get('/auth/me');
      setUser(res.data.data);
    } catch (e) {
      console.error('refreshUser failed', e);
    }
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
