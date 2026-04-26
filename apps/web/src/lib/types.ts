export interface Project {
  id: number;
  name: string;
  description?: string;
  status: string;
  created_at: string;
}

export interface Folder {
  id: number;
  project_id: number;
  parent_folder_id?: number;
  name: string;
  created_at: string;
}

export interface Deliverable {
  id: number;
  folder_id: number;
  content_type: string;
  title: string;
  status: string;
  body_md?: string;
  created_at: string;
  updated_at: string;
}

export interface Brief {
  id: number;
  project_id: number;
  deliverable_id?: number;
  brief_md: string;
  toggles_json?: string;
  created_at: string;
}

export interface ScrapeItem {
  id: number;
  source: string;
  source_url: string;
  title: string;
  body?: string;
  author?: string;
  published_at?: string;
  score_relevance?: number;
  score_reasoning?: string;
  dismissed_at?: string;
}

export interface ChatMessage {
  id: number;
  session_id: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  created_at: string;
}

export interface Toggles {
  brief_first: boolean;
  audience: string;
  voice: 'opinionated' | 'thoughtful' | 'objective' | 'technical' | 'founder';
  skills: string[] | 'auto';
  playbook: string | 'auto';
  content_type: string;
}

export const CONTENT_TYPES = [
  'blog', 'email', 'press_release', 'analyst_briefing',
  'social_post', 'case_study', 'launch_copy', 'lifecycle_email',
  'newsletter', 'thought_leadership', 'other'
] as const;
