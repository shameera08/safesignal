// SafeSignal - src/pages/Dashboard.jsx
import { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { MapContainer, TileLayer, Marker, Popup, Circle } from "react-leaflet";
import L from "leaflet";
import { useAuth } from "../context/AuthContext";
import { authApi, incidentApi } from "../api/client";
import SOSModal from "../components/SOSModal";

// Fix default marker icons (Leaflet + bundlers issue)
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

const severityColor = {
  critical: "#e11d2e",
  high: "#f0603a",
  medium: "#f0a63a",
  low: "#3aa8f0",
  "": "#9a9a9a",
};

export default function Dashboard() {
  const { user, logout, refreshUser } = useAuth();
  const [position, setPosition] = useState(null);
  const [incidents, setIncidents] = useState([]);
  const [showSOS, setShowSOS] = useState(false);
  const [locError, setLocError] = useState("");
  const navigate = useNavigate();

  // Get + push live location
  useEffect(() => {
    if (!navigator.geolocation) {
      setLocError("Location not available on this device.");
      return;
    }
    const watchId = navigator.geolocation.watchPosition(
      async (pos) => {
        const { latitude, longitude } = pos.coords;
        setPosition([latitude, longitude]);
        try {
          await authApi.updateMe({ latitude, longitude });
        } catch {
          /* non-fatal */
        }
      },
      () => setLocError("Location permission denied — enable it to see nearby incidents."),
      { enableHighAccuracy: true }
    );
    return () => navigator.geolocation.clearWatch(watchId);
  }, []);

  const fetchNearby = useCallback(async () => {
    if (!position) return;
    try {
      const { data } = await incidentApi.nearby(position[0], position[1], 10000);
      setIncidents(data);
    } catch {
      /* non-fatal */
    }
  }, [position]);

  useEffect(() => {
    fetchNearby();
    const interval = setInterval(fetchNearby, 8000); // poll for live updates
    return () => clearInterval(interval);
  }, [fetchNearby]);

  const handleSOSCreated = () => {
    setShowSOS(false);
    fetchNearby();
  };

  return (
    <div className="dashboard">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark">●</span>
          <span className="brand-name">SafeSignal</span>
        </div>
        <div className="topbar-right">
          <span className="user-chip">{user?.username} · {user?.role}</span>
          <button className="btn-ghost" onClick={logout}>Log out</button>
        </div>
      </header>

      {locError && <div className="banner-warning">{locError}</div>}

      <div className="dashboard-body">
        <aside className="incident-feed">
          <h2>Nearby incidents</h2>
          {incidents.length === 0 && <p className="muted">No active incidents within 10 km.</p>}
          <ul>
            {incidents.map((inc) => (
              <li
                key={inc.id}
                className="incident-item"
                onClick={() => navigate(`/incident/${inc.id}`)}
              >
                <span
                  className="severity-dot"
                  style={{ background: severityColor[inc.severity] }}
                />
                <div>
                  <div className="incident-type">{inc.type}</div>
                  <div className="incident-desc">{inc.description}</div>
                  <div className="incident-meta">
                    {inc.responder_count} responding · {inc.status.replace("_", " ")}
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </aside>

        <main className="map-wrap">
          {position ? (
            <MapContainer center={position} zoom={13} style={{ height: "100%", width: "100%" }}>
              <TileLayer
                attribution='&copy; OpenStreetMap contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              <Marker position={position}>
                <Popup>You are here</Popup>
              </Marker>
              {incidents.map((inc) => (
                <Circle
                  key={inc.id}
                  center={[inc.latitude, inc.longitude]}
                  radius={200}
                  pathOptions={{ color: severityColor[inc.severity], fillOpacity: 0.5 }}
                  eventHandlers={{ click: () => navigate(`/incident/${inc.id}`) }}
                >
                  <Popup>
                    <strong>{inc.type}</strong>
                    <br />
                    {inc.description}
                  </Popup>
                </Circle>
              ))}
            </MapContainer>
          ) : (
            <div className="map-loading">Getting your location…</div>
          )}
        </main>
      </div>

      <button className="sos-button" onClick={() => setShowSOS(true)}>
        SOS
      </button>

      {showSOS && (
        <SOSModal
          position={position}
          onClose={() => setShowSOS(false)}
          onCreated={handleSOSCreated}
        />
      )}
    </div>
  );
}
