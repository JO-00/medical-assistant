import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Stethoscope, Loader2, AlertCircle } from "lucide-react";
import { useAuth } from "../lib/auth";
import PulseLine from "../components/PulseLine";
import Logo from "../components/Logo";

const QUALIFICATIONS = ["MBBS", "MD", "DO", "MBChB", "DNB", "MS", "Other"];

const initialState = {
  full_name: "",
  email: "",
  password: "",
  confirm_password: "",
  qualification: "",
  specialty: "",
  license_number: "",
  years_of_experience: "",
  clinic_name: "",
  phone_number: "",
  languages_spoken: "",
  timezone: "",
  bio: "",
};

export default function Signup() {
  const [form, setForm] = useState(initialState);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { signup } = useAuth();
  const navigate = useNavigate();

  const update = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (form.password !== form.confirm_password) {
      setError("Passwords don't match.");
      return;
    }
    if (!form.full_name || !form.email || !form.password || !form.qualification) {
      setError("Fill in your name, email, password, and qualification to continue.");
      return;
    }

    setLoading(true);
    try {
      const { confirm_password, ...payload } = form;
      await signup({
        ...payload,
        years_of_experience: payload.years_of_experience
          ? Number(payload.years_of_experience)
          : null,
        languages_spoken: payload.languages_spoken
          ? payload.languages_spoken.split(",").map((s) => s.trim()).filter(Boolean)
          : [],
      });
      navigate("/", { replace: true });
    } catch (err) {
      setError(err?.response?.data?.detail || "Couldn't create your account. Try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-ink flex items-center justify-center px-4 py-10">
      <div className="w-full max-w-2xl animate-rise">
        <div className="mb-6 flex flex-col items-center gap-3 text-paper-raised">
          <Logo tone="paper" />
          <PulseLine tone="paper" className="h-6 w-40 opacity-70" />
        </div>

        <div className="bg-paper-raised rounded-2xl shadow-card p-8 sm:p-10">
          <div className="mb-8">
            <div className="inline-flex items-center gap-2 text-sage text-xs font-mono uppercase tracking-widest mb-2">
              <Stethoscope size={14} />
              Clinician registration
            </div>
            <h1 className="font-display text-2xl text-ink">Set up your practice profile</h1>
            <p className="text-ink-faint text-sm mt-1">
              This is what lets the voice assistant recognize you and speak to your patient list.
            </p>
          </div>

          {error && (
            <div className="mb-6 flex items-start gap-2 rounded-lg bg-brick-soft/60 border border-brick/30 px-4 py-3 text-sm text-brick">
              <AlertCircle size={16} className="mt-0.5 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-8">
            <section className="space-y-4">
              <h2 className="text-xs font-mono uppercase tracking-widest text-ink-faint">
                Account
              </h2>
              <div className="grid sm:grid-cols-2 gap-4">
                <Field label="Full name" required>
                  <input
                    className="input"
                    placeholder="Dr. Amina Haddad"
                    value={form.full_name}
                    onChange={update("full_name")}
                    required
                  />
                </Field>
                <Field label="Email" required>
                  <input
                    type="email"
                    className="input"
                    placeholder="amina@clinic.tn"
                    value={form.email}
                    onChange={update("email")}
                    required
                  />
                </Field>
                <Field label="Password" required>
                  <input
                    type="password"
                    className="input"
                    value={form.password}
                    onChange={update("password")}
                    required
                  />
                </Field>
                <Field label="Confirm password" required>
                  <input
                    type="password"
                    className="input"
                    value={form.confirm_password}
                    onChange={update("confirm_password")}
                    required
                  />
                </Field>
                <Field label="Phone number">
                  <input
                    type="tel"
                    className="input"
                    placeholder="+216 XX XXX XXX"
                    value={form.phone_number}
                    onChange={update("phone_number")}
                  />
                </Field>
                <Field label="Timezone">
                  <input
                    className="input"
                    placeholder="Africa/Tunis"
                    value={form.timezone}
                    onChange={update("timezone")}
                  />
                </Field>
              </div>
            </section>

            <section className="space-y-4">
              <h2 className="text-xs font-mono uppercase tracking-widest text-ink-faint">
                Credentials
              </h2>
              <div className="grid sm:grid-cols-2 gap-4">
                <Field label="Qualification" required>
                  <select
                    className="input"
                    value={form.qualification}
                    onChange={update("qualification")}
                    required
                  >
                    <option value="" disabled>
                      Select qualification
                    </option>
                    {QUALIFICATIONS.map((q) => (
                      <option key={q} value={q}>
                        {q}
                      </option>
                    ))}
                  </select>
                </Field>
                <Field label="Specialty">
                  <input
                    className="input"
                    placeholder="General practice, cardiology…"
                    value={form.specialty}
                    onChange={update("specialty")}
                  />
                </Field>
                <Field label="License number">
                  <input
                    className="input"
                    placeholder="Medical board registration no."
                    value={form.license_number}
                    onChange={update("license_number")}
                  />
                </Field>
                <Field label="Years of experience">
                  <input
                    type="number"
                    min="0"
                    className="input"
                    value={form.years_of_experience}
                    onChange={update("years_of_experience")}
                  />
                </Field>
              </div>
            </section>

            <section className="space-y-4">
              <h2 className="text-xs font-mono uppercase tracking-widest text-ink-faint">
                Practice details <span className="normal-case text-ink-faint/70">(optional)</span>
              </h2>
              <div className="grid sm:grid-cols-2 gap-4">
                <Field label="Clinic or hospital">
                  <input
                    className="input"
                    placeholder="Clinique Ibn Khaldoun"
                    value={form.clinic_name}
                    onChange={update("clinic_name")}
                  />
                </Field>
                <Field label="Languages spoken">
                  <input
                    className="input"
                    placeholder="French, Arabic, English"
                    value={form.languages_spoken}
                    onChange={update("languages_spoken")}
                  />
                </Field>
              </div>
              <Field label="Short bio">
                <textarea
                  className="input min-h-[80px] resize-none"
                  placeholder="Anything the assistant should know about your practice."
                  value={form.bio}
                  onChange={update("bio")}
                />
              </Field>
            </section>

            <button
              type="submit"
              disabled={loading}
              className="w-full inline-flex items-center justify-center gap-2 rounded-lg bg-ink text-paper-raised font-medium py-3 hover:bg-ink-soft transition-colors disabled:opacity-60"
            >
              {loading && <Loader2 size={16} className="animate-spin" />}
              Create account
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-ink-faint">
            Already registered?{" "}
            <Link to="/login" className="text-sage font-medium hover:underline">
              Log in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}

function Field({ label, required, children }) {
  return (
    <label className="block">
      <span className="block text-sm text-ink-soft mb-1.5">
        {label} {required && <span className="text-brick">*</span>}
      </span>
      {children}
    </label>
  );
}
