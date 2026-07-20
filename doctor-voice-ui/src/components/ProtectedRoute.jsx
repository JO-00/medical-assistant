import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../lib/auth";

export default function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  const location = useLocation();

  // Wait until AuthProvider is done verifying initial state
  if (loading) {
    return (
      <div className="min-h-screen bg-ink flex items-center justify-center text-paper-raised font-mono text-sm">
        <span>Restoring session...</span>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" state={{ from: location.pathname }} replace />;
  }

  return children;
}