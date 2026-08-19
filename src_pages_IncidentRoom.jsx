// SafeSignal - src/pages/IncidentRoom.jsx
import { useEffect, useState, useCallback, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { incidentApi } from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function IncidentRoom() {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [incident, setIncident] = useState(null);
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState("");
  const [responding, setResponding] = useState(false);
  const bottomRef = useRef(null);

  const fetchIncident = useCallback(async () => {
    try {
      const { data } = await incidentApi.detail(id);
      setIncident(data);
    } catch {
      /* non-fatal */
    }
  }, [id]);

  const fetchMessages = useCallback(async () => {
    try {
      const { data } = await incidentApi.messages(id);
      setMessages(data);
    } catch {
      /* non-fatal */
    }
  }, [id]);

  useEffect(() => {
    fetchIncident();
    fetchMessages();
    const interval = setInterval(() => {
      fetchIncident();
      fetchMessages();
    }, 4000);
    return () => clearInterval(interval);
  }, [fetchIncident, fetchMessages]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleRespond = async () => {
    setResponding(true);
    try {
      await incidentApi.respond(id, { status: "acknowledged" });
      await fetchIncident();
    } catch {
      /* non-fatal */
    } finally {
      setResponding(false);
    }
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!text.trim()) return;
    const value = text;
    setText("");
    try {
      await incidentApi.sendMessage(id, value);
      fetchMessages();
    } catch {
      /* non-fatal */
    }
  };

  if (!incident) return <div className="loading-screen">Loading incident…</div>;

  return (
    <div className="incident-room">
      <header className="topbar">
        <button className="btn-ghost" onClick={() => navigate("/")}>← Back</button>
        <div className={`severity-badge sev-${incident.severity || "unknown"}`}>
          {incident.severity || "assessing"}
        </div>
      </header>

      <section className="incident-summary">
        <h2>{incident.type} emergency</h2>
        <p>{incident.description}</p>
        {incident.ai_summary && <p className="ai-summary">AI triage: {incident.ai_summary}</p>}
        <div className="incident-stats">
          <span>{incident.responder_count} responding</span>
          <span>Status: {incident.status.replace("_", " ")}</span>
          <span>Reported by {incident.reporter_username}</span>
        </div>
        <button className="btn-primary" onClick={handleRespond} disabled={responding}>
          {responding ? "Marking…" : "I'm responding"}
        </button>
      </section>

      <section className="chat-panel">
        <div className="chat-messages">
          {messages.map((m) => (
            <div
              key={m.id}
              className={`chat-bubble ${m.sender_username === user?.username ? "mine" : ""}`}
            >
              <span className="chat-sender">{m.sender_username}</span>
              <span className="chat-text">{m.text}</span>
            </div>
          ))}
          <div ref={bottomRef} />
        </div>
        <form onSubmit={handleSend} className="chat-input-row">
          <input
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Coordinate with other responders…"
          />
          <button type="submit" className="btn-primary">Send</button>
        </form>
      </section>
    </div>
  );
}
