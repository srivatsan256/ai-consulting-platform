export const VIEWS = {
  LOGIN: 'login',
  DASHBOARD: 'dashboard',
  PROJECTS: 'projects',
  PROJECT_DETAIL: 'project-detail',
  UPLOAD: 'upload',
  VERIFICATION: 'verification',
  AI_CHAT: 'ai-chat',
  DELIVERABLES: 'deliverables',
  REPORTS: 'reports',

  CLIENT_DASHBOARD: 'client-dashboard',
  CLIENT_PROJECTS: 'client-projects',
  CLIENT_CHAT: 'client-chat',
  CLIENT_DOWNLOADS: 'client-downloads',
  LEVEL: 'level',
};

export const PAGE_TITLES = {
  [VIEWS.DASHBOARD]: 'Dashboard',
  [VIEWS.PROJECTS]: 'Projects',
  [VIEWS.PROJECT_DETAIL]: 'Project Detail',
  [VIEWS.UPLOAD]: 'Upload Documents',
  [VIEWS.VERIFICATION]: 'Document Verification',
  [VIEWS.AI_CHAT]: 'AI Assistant',
  [VIEWS.DELIVERABLES]: 'Deliverables',
  [VIEWS.REPORTS]: 'Reports',

  [VIEWS.CLIENT_DASHBOARD]: 'Client Dashboard',
  [VIEWS.CLIENT_PROJECTS]: 'My Projects',
  [VIEWS.CLIENT_CHAT]: 'AI Assistant',
  [VIEWS.CLIENT_DOWNLOADS]: 'Downloads',
  1: 'Level 1: Discovery & Requirements',
  2: 'Level 2: Gated Verification',
  3: 'Level 3: Architecture & Tech Stack',
  4: 'Level 4: Development Completion',
  5: 'Level 5: Testing & Quality Engineering',
  6: 'Level 6: Deployment & Release',
  7: 'Level 7: Adoption & Training',
  8: 'Level 8: Governance & Compliance',
  9: 'Level 9: Delivery Readiness',
  10: 'Level 10: Client Acceptance',
  11: 'Level 11: Closure & Archival',
};

export function getPageTitle(view, activeLevel) {
  if (view === VIEWS.LEVEL) return PAGE_TITLES[activeLevel] || 'Project';
  return PAGE_TITLES[view] || 'RequirementAI';
}
