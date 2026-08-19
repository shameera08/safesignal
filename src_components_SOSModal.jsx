// SafeSignal - src/components/SOSModal.jsx
import { useState } from "react";
import { incidentApi } from "../api/client";

const TYPES = [
  { value: "medical", label: "Medical emergency" },
  { value: "fire", label: "Fire" },
  { value: "accident", label: "Accident" },
  { value: "crime", label: "Crime / safety threat" },
  { value: "disaster", label: "Natural disaster" },
];

export default function SOSModal({ position, onClose, onCreated }) {
  const [type, setType] = useState("medical");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!position) {
      setError("Waiting for your location — try again in a moment.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      await incidentApi.create({
        type,
        description,
        latitude: position[0],
        longitude: position[1],
        radius_meters: 5000,
      });
      onCreated();
    } catch {
      setError("Could not send SOS. Check your connection and try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-card sos-modal" onClick={(e) => e.stopPropagation()}>
        <h2>Raise SOS</h2>
        <p className="muted">This alerts every verified responder within 5 km.</p>

        <form onSubmit={handleSubmit} className="auth-form">
          <label>
            Type of emergency
            <select value={type} onChange={(e) => setType(e.target.value)}>
              {TYPES.map((t) => (
                <option key={t.value} value={t.value}>
                  {t.label}
                </option>
              ))}
            </select>
          </label>
          <label>
            What's happening?
            <textarea
              rows={4}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="e.g. Man collapsed near the bus stand, not breathing"
              required
            />
          </label>
          {error && <p className="form-error">{error}</p>}
          <div className="modal-actions">
            <button type="button" className="btn-ghost" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn-sos" disabled={loading}>
              {loading ? "Sending…" : "Send SOS"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
