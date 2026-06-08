import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authApi } from '../services/authApi';
import { AuthContext } from '../contexts/AuthContext';

// Time (ms) before auto-logout when tab is hidden (5 minutes)
const TAB_HIDDEN_TIMEOUT_MS = 5 * 60 * 1000;

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const hiddenTimerRef = useRef(null);

  const doLogout = useCallback(() => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
    navigate('/login');
  }, [navigate]);

  const checkAuth = useCallback(async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      setLoading(false);
      return;
    }
    try {
      const res = await authApi.getMe();
      setUser(res.data);
    } catch {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    queueMicrotask(() => { checkAuth(); });
  }, [checkAuth]);

  // Tab visibility timeout: sign out when tab is hidden for TAB_HIDDEN_TIMEOUT_MS
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'hidden') {
        hiddenTimerRef.current = setTimeout(() => {
          if (localStorage.getItem('access_token')) {
            doLogout();
          }
        }, TAB_HIDDEN_TIMEOUT_MS);
      } else {
        // Tab became visible again — cancel the timer
        if (hiddenTimerRef.current) {
          clearTimeout(hiddenTimerRef.current);
          hiddenTimerRef.current = null;
        }
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      if (hiddenTimerRef.current) clearTimeout(hiddenTimerRef.current);
    };
  }, [doLogout]);

  const login = useCallback(async (email, password) => {
    const res = await authApi.login({ email, password });
    localStorage.setItem('access_token', res.data.access_token);
    localStorage.removeItem('refresh_token');
    const me = await authApi.getMe();
    setUser(me.data);
    return res.data;
  }, []);

  const register = useCallback(async (userData) => {
    const res = await authApi.register(userData);
    return res.data;
  }, []);

  const logout = useCallback(async () => {
    try {
      await authApi.logout();
    } catch {
      // ignore
    } finally {
      doLogout();
    }
  }, [doLogout]);

  const value = useMemo(
    () => ({ user, loading, login, register, logout, checkAuth }),
    [user, loading, login, register, logout, checkAuth]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
