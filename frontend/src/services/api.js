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
  list: (params) => api.get("/memberships/", { params }),
  switchCompany: (companyId) => api.post("/memberships/switch/", { company_id: companyId }),
};

export const companyService = {
  context: () => api.get("/companies/companies/context/"),
};

export const painAreaService = {
  list: async (params = {}) => {
    const all = [];
    let page = 1;
    for (;;) {
      const res = await api.get("/ai-intervention-pain-areas/", {
        params: { ...params, page, page_size: 100 },
      });
      if (page === 1 && !Array.isArray(res.data.results)) {
        return res;
      }
      all.push(...(res.data.results || []));
      if (!res.data.next) break;
      page += 1;
    }
    return { data: all };
  },
  create: (data) => api.post("/ai-intervention-pain-areas/", data),
  update: (id, data) => api.put(`/ai-intervention-pain-areas/${id}/`, data),
  remove: (id) => api.delete(`/ai-intervention-pain-areas/${id}/`),
  uploadCsv: (formData, onUploadProgress, signal) =>
    api.post("/ai-intervention-pain-areas/upload-csv/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
      onUploadProgress,
      signal,
    }),
};

export const subscriptionService = {
  features: () => api.get("/subscriptions/subscriptions/features/"),
  usage: () => api.get("/subscriptions/subscriptions/usage/"),
  quotas: () => api.get("/subscriptions/subscriptions/quotas/"),
};

export const contactService = {
  submit: (data) => api.post("/contact/", data),
};

export const taskService = {
  list: (params) => api.get("/tasks/", { params }),
  get: (id) => api.get(`/tasks/${id}/`),
  create: (data) => api.post("/tasks/", data),
  update: (id, data) => api.patch(`/tasks/${id}/`, data),
  delete: (id) => api.delete(`/tasks/${id}/`),
  complete: (id) => api.post(`/tasks/${id}/complete/`),
  comments: (id) => api.get(`/tasks/${id}/task-comments/`),
  addComment: (id, content) =>
    api.post(`/tasks/${id}/task-comments/`, { content }),
  attachments: (id) => api.get(`/tasks/${id}/attachments/`),
  addAttachment: (id, formData) =>
    api.post(`/tasks/${id}/attachments/`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
  deleteAttachment: (attachmentId) =>
    api.delete(`/tasks/attachments/${attachmentId}/`),
};

export const userService = {
  list: (params) => api.get("/accounts/users/", { params }),
  get: (id) => api.get(`/accounts/users/${id}/`),
  update: (id, data) => api.patch(`/accounts/users/${id}/`, data),
  delete: (id) => api.delete(`/accounts/users/${id}/`),
  activate: (id) => api.post(`/accounts/users/${id}/activate/`),
  deactivate: (id) => api.post(`/accounts/users/${id}/deactivate/`),
  bulkImport: (formData) =>
    api.post("/accounts/users/bulk-import/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
  bulkImportJson: (users) => api.post("/accounts/users/bulk-import/", { users }),
  exportCsv: () =>
    api.get("/accounts/users/export/", { responseType: "blob" }),
  invitations: () => api.get("/memberships/invitations/"),
  invite: (data) => api.post("/memberships/invite/", data),
};

export const teamService = {
  list: (params) => api.get("/teams/", { params }),
  create: (data) => api.post("/teams/", data),
  update: (id, data) => api.patch(`/teams/${id}/`, data),
  delete: (id) => api.delete(`/teams/${id}/`),
  members: (params) => api.get("/teams/members/", { params }),
  addMember: (data) => api.post("/teams/members/", data),
  deleteMember: (id) => api.delete(`/teams/members/${id}/`),
};

export const departmentService = {
  list: (params) => api.get("/departments/", { params }),
  create: (data) => api.post("/departments/", data),
  update: (id, data) => api.patch(`/departments/${id}/`, data),
  delete: (id) => api.delete(`/departments/${id}/`),
  members: (params) => api.get("/departments/members/", { params }),
  addMember: (data) => api.post("/departments/members/", data),
  deleteMember: (id) => api.delete(`/departments/members/${id}/`),
};

export const roleService = {
  list: () => api.get("/roles/"),
  create: (data) => api.post("/roles/", data),
  update: (id, data) => api.patch(`/roles/${id}/`, data),
  delete: (id) => api.delete(`/roles/${id}/`),
  assign: (data) => api.post("/roles/assign/", data),
  assignments: () => api.get("/roles/assignments/"),
  mine: () => api.get("/roles/mine/"),
};

export const permissionService = {
  list: () => api.get("/permissions/"),
};

export const fileManagementService = {
  files: (params) => api.get("/file-management/files/", { params }),
  getFile: (id) => api.get(`/file-management/files/${id}/`),
  upload: (formData) =>
    api.post("/file-management/files/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
  updateFile: (id, data) => api.patch(`/file-management/files/${id}/`, data),
  deleteFile: (id) => api.delete(`/file-management/files/${id}/`),
  rescan: (id) => api.post(`/file-management/files/${id}/rescan/`),
  download: (id) =>
    api.get(`/file-management/files/${id}/download/`, {
      responseType: "blob",
    }),
  categories: (params) =>
    api.get("/file-management/categories/", { params }),
  createCategory: (data) => api.post("/file-management/categories/", data),
  updateCategory: (id, data) =>
    api.patch(`/file-management/categories/${id}/`, data),
  deleteCategory: (id) => api.delete(`/file-management/categories/${id}/`),
  quota: () => api.get("/file-management/quota/"),
  updateQuota: (id, data) =>
    api.patch(`/file-management/quota/${id}/`, data),
  scans: (params) => api.get("/file-management/scans/", { params }),
  rescanScan: (id) => api.post(`/file-management/scans/${id}/rescan/`),
  permissions: (params) =>
    api.get("/file-management/permissions/", { params }),
  createPermission: (data) =>
    api.post("/file-management/permissions/", data),
  updatePermission: (id, data) =>
    api.patch(`/file-management/permissions/${id}/`, data),
  deletePermission: (id) => api.delete(`/file-management/permissions/${id}/`),
};

export const workflowService = {
  list: (params) => api.get("/workflows/", { params }),
  get: (id) => api.get(`/workflows/${id}/`),
  create: (data) => api.post("/workflows/", data),
  update: (id, data) => api.patch(`/workflows/${id}/`, data),
  delete: (id) => api.delete(`/workflows/${id}/`),
  activate: (id) => api.post(`/workflows/${id}/activate/`),
  deactivate: (id) => api.post(`/workflows/${id}/deactivate/`),
  addStep: (id, data) => api.post(`/workflows/${id}/add_step/`, data),
  executions: (workflowId) =>
    api.get(`/workflows/${workflowId}/workflow-executions/`),
  workflowHistory: (workflowId) =>
    api.get(`/workflows/${workflowId}/workflow-history/`),
  executionHistory: (executionId) =>
    api.get(`/workflows/executions/${executionId}/history/`),
  completeExecution: (executionId) =>
    api.post(`/workflows/executions/${executionId}/complete/`),
  failExecution: (executionId) =>
    api.post(`/workflows/executions/${executionId}/fail/`),
};

export default api;
