"use client";

import {
  createContext,
  ReactNode,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  clearAuthToken,
  getCurrentUser,
  getErrorMessage,
  getStoredAuthToken,
  login as loginRequest,
  logout as logoutRequest,
  setAuthToken,
  signup as signupRequest,
} from "@/lib/api";
import type { AuthState, LoginPayload, SignupPayload, User } from "@/types/auth";

interface AuthContextValue extends AuthState {
  login: (payload: LoginPayload) => Promise<User>;
  signup: (payload: SignupPayload) => Promise<User>;
  logout: () => Promise<void>;
  refreshCurrentUser: () => Promise<User | null>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const clearAuthState = useCallback(() => {
    clearAuthToken();
    setToken(null);
    setUser(null);
  }, []);

  const refreshCurrentUser = useCallback(async () => {
    try {
      const currentUser = await getCurrentUser();
      setUser(currentUser);
      return currentUser;
    } catch {
      clearAuthState();
      return null;
    }
  }, [clearAuthState]);

  useEffect(() => {
    const storedToken = getStoredAuthToken();
    if (!storedToken) {
      setIsLoading(false);
      return;
    }

    setToken(storedToken);
    setAuthToken(storedToken);

    refreshCurrentUser()
      .catch(() => {
        clearAuthState();
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [clearAuthState, refreshCurrentUser]);

  const login = useCallback(
    async (payload: LoginPayload) => {
      const response = await loginRequest(payload);
      setAuthToken(response.access_token);
      setToken(response.access_token);

      try {
        const currentUser = await getCurrentUser();
        setUser(currentUser);
        return currentUser;
      } catch (error) {
        clearAuthState();
        throw error;
      }
    },
    [clearAuthState],
  );

  const signup = useCallback(
    async (payload: SignupPayload) => {
      await signupRequest(payload);
      return login({
        email_or_username: payload.username,
        password: payload.password,
      });
    },
    [login],
  );

  const logout = useCallback(async () => {
    try {
      await logoutRequest();
    } catch (error) {
      console.warn(getErrorMessage(error));
    } finally {
      clearAuthState();
    }
  }, [clearAuthState]);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      token,
      isAuthenticated: Boolean(user && token),
      isLoading,
      login,
      signup,
      logout,
      refreshCurrentUser,
    }),
    [isLoading, login, logout, refreshCurrentUser, signup, token, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
