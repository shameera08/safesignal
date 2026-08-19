// SafeSignal - src/api/client.js
import axios from "axios";

const API_BASE = "http://127.0.0.1:8000/api";

const client = axios.create({ baseURL: API_BASE });

client.interceptors.request.use((config) => {
  const token = localStorage.getItem("access");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Auto-refresh expired access tokens once, then retry the request.
client.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      const refresh = localStorage.getItem("refresh");
      if (refresh) {
        try {
          const { data } = await axios.post(`${API_BASE}/auth/login/refresh/`, { refresh });
          localStorage.setItem("access", data.access);
          original.headers.Authorization = `Bearer ${data.access}`;
          return client(original);
        } catch {
          localStorage.removeItem("access");
          localStorage.removeItem("refresh");
          window.location.href = "/login";
        }
      }
    }
    return Promise.reject(error);
  }
);

export default client;

export const authApi = {
  register: (data) => client.post("/auth/register/", data),
  login: (data) => client.post("/auth/login/", data),
  me: () => client.get("/auth/me/"),
  updateMe: (data) => client.patch("/auth/me/", data),
};

export const incidentApi = {
  create: (data) => client.post("/incidents/", data),
  nearby: (lat, lng, radius = 5000) =>
    client.get("/incidents/nearby/", { params: { lat, lng, radius } }),
  detail: (id) => client.get(`/incidents/${id}/`),
  respond: (id, data) => client.post(`/incidents/${id}/respond/`, data),
  escalate: (id) => client.post(`/incidents/${id}/escalate/`),
  messages: (id) => client.get(`/incidents/${id}/messages/`),
  sendMessage: (id, text) => client.post(`/incidents/${id}/messages/`, { text }),
};
