import React, { createContext, useState, useEffect, useContext } from 'react';
import apiClient from '../api/axios';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchUser = async () => {
      const token = localStorage.getItem('token');
      if (token) {
        try {
          const response = await apiClient.get('/auth/me');
          setUser(response.data.data);
        } catch (err) {
          console.error('Failed to fetch user:', err);
          localStorage.removeItem('token');
        }
      }
      setLoading(false);
    };

    fetchUser();
  }, []);

  const extractError = (err, defaultMsg) => {
    if (err.response?.data?.error?.message) return err.response.data.error.message;
    if (Array.isArray(err.response?.data?.detail) && err.response.data.detail.length > 0) {
      return err.response.data.detail[0].msg;
    }
    if (typeof err.response?.data?.detail === 'string') return err.response.data.detail;
    return defaultMsg;
  };

  const login = async (email, password) => {
    setError(null);
    try {
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      const response = await apiClient.post('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });
      
      const token = response.data.data.access_token;
      localStorage.setItem('token', token);
      
      const userRes = await apiClient.get('/auth/me');
      setUser(userRes.data.data);
      return true;
    } catch (err) {
      setError(extractError(err, 'Login failed'));
      return false;
    }
  };

  const register = async (email, password, name) => {
    setError(null);
    try {
      await apiClient.post('/auth/register', { email, password, name });
      return await login(email, password);
    } catch (err) {
      setError(extractError(err, 'Registration failed'));
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, error, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
