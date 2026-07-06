import axios from 'axios';

// Create a configured Axios instance
const apiClient = axios.create({
  baseURL: 'http://localhost:8080/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor: Attach JWT Token if available
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Handle global errors (like 401 Unauthorized)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // If the token is invalid or expired
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token');
      // Dispatch a custom event so the React app can redirect to login
      window.dispatchEvent(new Event('auth-failed'));
    }
    return Promise.reject(error);
  }
);

export default apiClient;
