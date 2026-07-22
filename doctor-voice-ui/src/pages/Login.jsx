import { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { Loader2, AlertCircle } from "lucide-react";
import { useAuth } from "../lib/auth";
import PulseLine from "../components/PulseLine";
import Logo from "../components/Logo";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login({ email, password });
      const dest = location.state?.from || "/";
      navigate(dest, { replace: true });
    } catch (err) {
      console.log(err);
      setError(err?.response?.data?.detail || "Couldn't log you in. Check your credentials.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-ink flex items-center justify-center px-4">
      <div className="w-full max-w-sm animate-rise">
        <div className="mb-6 flex flex-col items-center gap-3 text-paper-raised">
          <Logo tone="paper" />
          <PulseLine tone="paper" className="h-6 w-40 opacity-70" />
        </div>

        <div className="bg-paper-raised rounded-2xl shadow-card p-8">
          <h1 className="font-display text-2xl text-ink mb-1">Welcome back</h1>
          <p className="text-ink-faint text-sm mb-6">
            Log in to pick up your consult queue and call history.
          </p>

          {error && (
            <div className="mb-5 flex items-start gap-2 rounded-lg bg-brick-soft/60 border border-brick/30 px-4 py-3 text-sm text-brick">
              <AlertCircle size={16} className="mt-0.5 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <label className="block">
              <span className="block text-sm text-ink-soft mb-1.5">Email</span>
              <input
                type="email"
                className="input"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@clinic.tn"
                required
                autoFocus
              />
            </label>
            <label className="block">
              <span className="block text-sm text-ink-soft mb-1.5">Password</span>
              <input
                type="password"
                className="input"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </label>

            <button
              type="submit"
              disabled={loading}
              className="w-full inline-flex items-center justify-center gap-2 rounded-lg bg-ink text-paper-raised font-medium py-3 hover:bg-ink-soft transition-colors disabled:opacity-60"
            >
              {loading && <Loader2 size={16} className="animate-spin" />}
              Log in
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-ink-faint">
            New here?{" "}
            <Link to="/signup" className="text-sage font-medium hover:underline">
              Create an account
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
