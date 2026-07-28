import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000/api",
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Token ${token}`;
  return config;
});

export const projectService = {
  list: () => api.get("/projects/"),
  get: (id) => api.get(`/projects/${id}/`),
  create: (data) => api.post("/projects/", data),
  update: (id, data) => api.put(`/projects/${id}/`, data),
  patch: (id, data) => api.patch(`/projects/${id}/`, data),
  delete: (id) => api.delete(`/projects/${id}/`),
  requiredDocStatus: (id) => api.get(`/projects/${id}/required_doc_status/`),
};

export const documentService = {
  upload: (projectId, formData) =>
    api.post(`/projects/${projectId}/documents/`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
};

export const verificationService = {
  verifyAll: (projectId, useAi = false) =>
    api.post(`/projects/${projectId}/verify_all/`, { use_ai: useAi }),
  validateDiscovery: (projectId) =>
    api.post(`/projects/${projectId}/validate_discovery/`),
};

export const chatService = {
  ask: (projectId, question) =>
    api.post(`/projects/${projectId}/chat/`, { question }),
};

export const deliverableService = {
  generate: (projectId) =>
    api.post(`/projects/${projectId}/generate_deliverables/`),
};

export const levelModuleService = {
  getAll: () => api.get("/projects/level-modules/"),
  get: (level) => api.get(`/projects/level-modules/?level=${level}`),
};

export const useCaseService = {
  generate: (projectId, data) =>
    api.post(`/projects/${projectId}/use-case-generate/`, data),
};

export default api;
