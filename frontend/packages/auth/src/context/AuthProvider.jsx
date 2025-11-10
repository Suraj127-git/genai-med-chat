import React, { createContext, useContext, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchMe, loginUser, registerUser, logout } from '@genai-med-chat/store';
import { getItem } from '@genai-med-chat/shared';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

const AuthProvider = ({ children }) => {
  const dispatch = useDispatch();
  const user = useSelector((state) => state.auth.user);
  const loading = useSelector((state) => state.auth.loading);

  useEffect(() => {
    const token = getItem('token');
    if (token) {
      dispatch(fetchMe());
    }
    // When no token, loading remains false by default slice; keep UI consistent
  }, []);

  const login = async (credentials) => {
    const res = await dispatch(loginUser(credentials));
    if (res.error) throw new Error(res.error.message || 'Login failed');
    return res.payload;
  };

  const register = async (userData) => {
    const res = await dispatch(registerUser(userData));
    if (res.error) throw new Error(res.error.message || 'Register failed');
    return res.payload;
  };

  const doLogout = () => {
    dispatch(logout());
  };

  const value = {
    user,
    loading,
    login,
    register,
    logout: doLogout
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

export default AuthProvider;