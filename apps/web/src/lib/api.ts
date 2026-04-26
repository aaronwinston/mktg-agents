/* eslint-disable @typescript-eslint/no-explicit-any */
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });
  if (!res.ok) throw new Error(`API error ${res.status}: ${await res.text()}`);
  return res.json();
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const api = {
  getProjects: () => apiFetch<any[]>('/api/projects'),
  createProject: (data: { name: string; description?: string }) =>
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    apiFetch<any>('/api/projects', { method: 'POST', body: JSON.stringify(data) }),

  getFolders: (projectId: number) => apiFetch<any[]>(`/api/projects/${projectId}/folders`),
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  createFolder: (data: any) =>
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    apiFetch<any>('/api/folders', { method: 'POST', body: JSON.stringify(data) }),

  getDeliverables: (folderId: number) => apiFetch<any[]>(`/api/folders/${folderId}/deliverables`),
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  createDeliverable: (data: any) =>
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    apiFetch<any>('/api/deliverables', { method: 'POST', body: JSON.stringify(data) }),
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  updateDeliverable: (id: number, data: any) =>
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    apiFetch<any>(`/api/deliverables/${id}`, { method: 'PUT', body: JSON.stringify(data) }),

  getFeed: () => apiFetch<any[]>('/api/intelligence/feed'),
  getItems: () => apiFetch<any[]>('/api/intelligence/items'),
  dismissItem: (id: number) =>
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    apiFetch<any>(`/api/intelligence/items/${id}/dismiss`, { method: 'POST' }),
  useAsContext: (id: number) =>
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    apiFetch<any>(`/api/intelligence/items/${id}/use-as-context`, { method: 'POST' }),
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  triggerScrape: () => apiFetch<any>('/api/intelligence/scrape', { method: 'POST' }),

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  getFileTree: () => apiFetch<any>('/api/files/tree'),
  getSkills: () => apiFetch<any[]>('/api/files/skills'),
  getPlaybooks: () => apiFetch<any[]>('/api/files/playbooks'),
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  readFile: (path: string) => apiFetch<any>(`/api/files/read?path=${encodeURIComponent(path)}`),
  writeFile: (path: string, content: string) =>
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    apiFetch<any>('/api/files/write', { method: 'POST', body: JSON.stringify({ path, content }) }),

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  createChatSession: (projectId?: number) =>
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    apiFetch<any>('/api/chat/session', { method: 'POST', body: JSON.stringify({ project_id: projectId }) }),
  getMessages: (sessionId: number) => apiFetch<any[]>(`/api/chat/session/${sessionId}/messages`),
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  generateBrief: (data: any) =>
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    apiFetch<any>('/api/chat/brief', { method: 'POST', body: JSON.stringify(data) }),
};
