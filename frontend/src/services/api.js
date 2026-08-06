import axios from "axios";

const API_BASE = "http://127.0.0.1:8000/api";

const api = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
});

export const TOKEN_KEY = "access_token";
export const REFRESH_KEY = "refresh_token";

export function getApiError(error, fallback = "Something went wrong.") {
  const data = error?.response?.data;
  if (!data) return error?.message || fallback;
  if (typeof data === "string") return data;
  if (typeof data.detail === "string") return data.detail;
  if (typeof data.message === "string") return data.message;
  if (Array.isArray(data.non_field_errors) && data.non_field_errors.length) {
    return data.non_field_errors.join(", ");
  }
  if (data.errors) {
    if (typeof data.errors === "string") return data.errors;
    if (Array.isArray(data.errors)) return data.errors.join(", ");
    if (typeof data.errors === "object") {
      const key = Object.keys(data.errors)[0];
      const value = data.errors[key];
      if (Array.isArray(value)) return `${key}: ${value.join(", ")}`;
      return `${key}: ${value}`;
    }
  }
  const field = Object.keys(data)[0];
  if (field && Array.isArray(data[field])) return data[field].join(", ");
  return fallback;
}

api.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY);
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

let refreshPromise = null;

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;
    if (
      error.response?.status === 401 &&
      !original?._retry &&
      original?.url !== "/auth/login/" &&
      localStorage.getItem(REFRESH_KEY)
    ) {
      original._retry = true;
      try {
        if (!refreshPromise) {
          refreshPromise = axios
            .post(`${API_BASE}/auth/refresh/`, {
              refresh: localStorage.getItem(REFRESH_KEY),
            })
            .then((res) => {
              const data = res.data.data || res.data;
              localStorage.setItem(TOKEN_KEY, data.access);
              if (data.refresh) localStorage.setItem(REFRESH_KEY, data.refresh);
              return data.access;
            })
            .finally(() => {
              refreshPromise = null;
            });
        }
        const newToken = await refreshPromise;
        original.headers.Authorization = `Bearer ${newToken}`;
        return api(original);
      } catch (refreshError) {
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(REFRESH_KEY);
        localStorage.removeItem("user");
        if (window.location.pathname !== "/") {
          window.location.href = "/";
        }
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

export const authService = {
  login: (email, password) => api.post("/auth/login/", { email, password }),
  register: (data) => api.post("/auth/register/", data),
  me: () => api.get("/auth/me/"),
  requestPasswordReset: (email) =>
    api.post("/auth/password-reset/request/", { email }),
  verifyOtp: (email, otp) =>
    api.post("/auth/password-reset/verify-otp/", { email, otp }),
  resetPassword: (uid, token, newPassword, confirmPassword) =>
    api.post("/auth/password-reset/confirm/", {
      uid,
      token,
      new_password: newPassword,
      confirm_password: confirmPassword,
    }),
  logout: () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_KEY);
    localStorage.removeItem("user");
  },
};

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

export const membershipService = {
  current: () => api.get("/memberships/current/"),
  list: () => api.get("/memberships/"),
  switchCompany: (companyId) => api.post("/memberships/switch/", { company_id: companyId }),
};

export const companyService = {
  context: () => api.get("/companies/context/"),
};

export const subscriptionService = {
  features: () => api.get("/subscriptions/subscriptions/features/"),
  usage: () => api.get("/subscriptions/subscriptions/usage/"),
  quotas: () => api.get("/subscriptions/subscriptions/quotas/"),
};

export default api;
