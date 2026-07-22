import React, { createContext, useContext, useState, useEffect } from "react";
// Import the shared API configuration and token helpers
import { api, getToken, setToken, clearToken } from "./api"; 

interface AuthContextType {
  user: any;
  loading: boolean;
  login: (credentials: any) => Promise<any>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const initializeAuth = () => {
      const token = getToken(); // Reads "consult_jwt"
      const savedUser = localStorage.getItem("user");

      if (token && savedUser) {
        try {
          setUser(JSON.parse(savedUser));
        } catch (err) {
          console.error("Failed to parse local user session", err);
          logout();
        }
      }
      setLoading(false);
    };

    initializeAuth();
  }, []);

  const logout = () => {
    clearToken(); // Clears "consult_jwt"
    localStorage.removeItem("user");
    setUser(null);
  };

  const login = async (credentials: any) => {
    setLoading(true);
    try {
      const response = await api.post("/auth/login", credentials);
      const { token, user: userData } = response.data;

      setToken(token); // Saves to "consult_jwt"
      localStorage.setItem("user", JSON.stringify(userData));
      setUser(userData);
      
      setLoading(false);
      return userData;
    } catch (error) {
      setLoading(false);
      throw error;
    }
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}