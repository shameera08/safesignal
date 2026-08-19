// SafeSignal - src/pages/Register.jsx
import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const ROLES = [
  { value: "citizen", label: "Citizen" },
  { value: "medical", label: "Medical responder" },
  { value: "police", label: "Police" },
  { value: "fire", label: "Fire responder" },
  { value: "volunteer", label: "Trained volunteer" },
];

export default function Register() {
  const [form, setForm] = useState({
    username: "",
    phone: "",
    password: "",
    role: "citizen",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await register(form);
      navigate("/");
    } catch (err) {
      setError(err.response?.data?.phone?.[0] || "Could not create account. Try a different username.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-screen">
      <div className="auth-card">
        <div className="brand">
          <span className="brand-mark">●</span>
          <span className="brand-name">SafeSignal</span>
        </div>
        <p className="auth-subtitle">Join the response network in your area.</p>

        <form onSubmit={handleSubmit} className="auth-form">
          <label>
            Username
            <input value={form.username} onChange={update("username")} required />
          </label>
          <label>
            Phone number
            <input value={form.phone} onChange={update("phone")} required />
          </label>
          <label>
            Password
            <input type="password" value={form.password} onChange={update("password")} required />
          </label>
          <label>
            I am a
            <select value={form.role} onChange={update("role")}>
              {ROLES.map((r) => (
                <option key={r.value} value={r.value}>
                  {r.label}
                </option>
              ))}
            </select>
          </label>
          {error && <p className="form-error">{error}</p>}
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? "Creating account…" : "Create account"}
          </button>
        </form>

        <p className="auth-switch">
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
