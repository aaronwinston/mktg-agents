-- ForgeOS migration 0001
-- Purpose: Enforce data integrity at the database level (FKs, UNIQUE, NOT NULL, CHECK).
--
-- This file is the documented source-of-truth for the target schema. The migration
-- runner may rebuild existing tables to apply these constraints.

-- table: organization
CREATE TABLE organization (
  id TEXT PRIMARY KEY NOT NULL,
  name TEXT NOT NULL,
  slug TEXT NOT NULL,
  plan TEXT NOT NULL DEFAULT 'free',
  trial_ends_at TEXT,
  stripe_customer_id TEXT,
  stripe_subscription_id TEXT,
  subscription_status TEXT,
  current_period_end TEXT,
  onboarding_completed_steps TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now')),
  CONSTRAINT uq_organization_slug UNIQUE (slug),
  CONSTRAINT ck_organization_plan CHECK (plan IN ('free','pro','team')),
  CONSTRAINT ck_organization_subscription_status CHECK (
    (subscription_status IN ('active','past_due','canceled')) OR subscription_status IS NULL
  )
);

-- table: membership
CREATE TABLE membership (
  id TEXT PRIMARY KEY NOT NULL,
  user_id TEXT NOT NULL,
  organization_id TEXT NOT NULL,
  role TEXT NOT NULL DEFAULT 'member',
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  CONSTRAINT fk_membership_org FOREIGN KEY (organization_id) REFERENCES organization(id) ON DELETE CASCADE,
  CONSTRAINT uq_membership_user_org UNIQUE (user_id, organization_id),
  CONSTRAINT ck_membership_role CHECK (role IN ('owner','admin','member'))
);
CREATE INDEX idx_membership_org ON membership(organization_id);
CREATE INDEX idx_membership_user ON membership(user_id);

-- table: project
CREATE TABLE project (
  id INTEGER PRIMARY KEY,
  organization_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  status TEXT NOT NULL DEFAULT 'active',
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  CONSTRAINT fk_project_org FOREIGN KEY (organization_id) REFERENCES organization(id) ON DELETE CASCADE,
  CONSTRAINT uq_project_org_name UNIQUE (organization_id, name),
  CONSTRAINT ck_project_status CHECK (status IN ('active','archived'))
);
CREATE INDEX idx_project_org ON project(organization_id);
CREATE INDEX idx_project_org_user ON project(organization_id, user_id);

-- table: folder
CREATE TABLE folder (
  id INTEGER PRIMARY KEY,
  organization_id TEXT NOT NULL,
  project_id INTEGER NOT NULL,
  parent_folder_id INTEGER,
  name TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  CONSTRAINT fk_folder_org FOREIGN KEY (organization_id) REFERENCES organization(id) ON DELETE CASCADE,
  CONSTRAINT fk_folder_project FOREIGN KEY (project_id) REFERENCES project(id) ON DELETE CASCADE,
  CONSTRAINT fk_folder_parent FOREIGN KEY (parent_folder_id) REFERENCES folder(id) ON DELETE SET NULL,
  CONSTRAINT uq_folder_org_project_parent_name UNIQUE (organization_id, project_id, parent_folder_id, name)
);
CREATE INDEX idx_folder_org_project ON folder(organization_id, project_id);

-- table: deliverable
CREATE TABLE deliverable (
  id INTEGER PRIMARY KEY,
  organization_id TEXT NOT NULL,
  folder_id INTEGER NOT NULL,
  content_type TEXT NOT NULL,
  title TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'draft',
  body_md TEXT,
  metadata_json TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now')),
  CONSTRAINT fk_deliverable_org FOREIGN KEY (organization_id) REFERENCES organization(id) ON DELETE CASCADE,
  CONSTRAINT fk_deliverable_folder FOREIGN KEY (folder_id) REFERENCES folder(id) ON DELETE CASCADE,
  CONSTRAINT uq_deliverable_org_folder_title UNIQUE (organization_id, folder_id, title),
  CONSTRAINT ck_deliverable_status CHECK (status IN ('draft','active','complete','archived','published'))
);
CREATE INDEX idx_deliverable_org_folder ON deliverable(organization_id, folder_id);

-- table: brief
CREATE TABLE brief (
  id INTEGER PRIMARY KEY,
  organization_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  project_id INTEGER NOT NULL,
  deliverable_id INTEGER,
  title TEXT NOT NULL,
  audience TEXT,
  description TEXT,
  brief_md TEXT,
  toggles_json TEXT,
  context_layers_json TEXT,
  skills_json TEXT,
  intelligence_items_json TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now')),
  CONSTRAINT fk_brief_org FOREIGN KEY (organization_id) REFERENCES organization(id) ON DELETE CASCADE,
  CONSTRAINT fk_brief_project FOREIGN KEY (project_id) REFERENCES project(id) ON DELETE CASCADE,
  CONSTRAINT fk_brief_deliverable FOREIGN KEY (deliverable_id) REFERENCES deliverable(id) ON DELETE SET NULL
);
CREATE INDEX idx_brief_org_project ON brief(organization_id, project_id);
CREATE INDEX idx_brief_org_deliverable ON brief(organization_id, deliverable_id);

-- table: chatsession
CREATE TABLE chatsession (
  id INTEGER PRIMARY KEY,
  organization_id TEXT NOT NULL,
  project_id INTEGER,
  folder_id INTEGER,
  deliverable_id INTEGER,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  CONSTRAINT fk_chatsession_org FOREIGN KEY (organization_id) REFERENCES organization(id) ON DELETE CASCADE,
  CONSTRAINT fk_chatsession_project FOREIGN KEY (project_id) REFERENCES project(id) ON DELETE SET NULL,
  CONSTRAINT fk_chatsession_folder FOREIGN KEY (folder_id) REFERENCES folder(id) ON DELETE SET NULL,
  CONSTRAINT fk_chatsession_deliverable FOREIGN KEY (deliverable_id) REFERENCES deliverable(id) ON DELETE SET NULL
);
CREATE INDEX idx_chatsession_org_created ON chatsession(organization_id, created_at);

-- table: chatmessage
CREATE TABLE chatmessage (
  id INTEGER PRIMARY KEY,
  organization_id TEXT NOT NULL,
  session_id INTEGER NOT NULL,
  role TEXT NOT NULL,
  content TEXT NOT NULL,
  metadata_json TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  CONSTRAINT fk_chatmessage_org FOREIGN KEY (organization_id) REFERENCES organization(id) ON DELETE CASCADE,
  CONSTRAINT fk_chatmessage_session FOREIGN KEY (session_id) REFERENCES chatsession(id) ON DELETE CASCADE,
  CONSTRAINT ck_chatmessage_role CHECK (role IN ('user','assistant','system','tool'))
);
CREATE INDEX idx_chatmessage_org_session ON chatmessage(organization_id, session_id);

-- table: scrapeitem
CREATE TABLE scrapeitem (
  id INTEGER PRIMARY KEY,
  organization_id TEXT NOT NULL,
  source TEXT NOT NULL,
  source_url TEXT NOT NULL,
  title TEXT NOT NULL,
  body TEXT,
  author TEXT,
  published_at TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  fetched_at TEXT NOT NULL DEFAULT (datetime('now')),
  raw_json TEXT,
  score REAL,
  score_relevance REAL,
  score_reasoning TEXT,
  why_relevant TEXT,
  content_angle TEXT,
  surfaced_to_user_at TEXT,
  dismissed_at TEXT,
  CONSTRAINT fk_scrapeitem_org FOREIGN KEY (organization_id) REFERENCES organization(id) ON DELETE CASCADE,
  CONSTRAINT uq_scrapeitem_org_source_url UNIQUE (organization_id, source_url)
);
CREATE INDEX idx_scrape_org_score ON scrapeitem(organization_id, score);
CREATE INDEX idx_scrape_org_created ON scrapeitem(organization_id, created_at);

-- table: pipelinerun
CREATE TABLE pipelinerun (
  id INTEGER PRIMARY KEY,
  organization_id TEXT NOT NULL,
  brief_id INTEGER NOT NULL,
  deliverable_id INTEGER,
  title TEXT NOT NULL,
  type TEXT NOT NULL DEFAULT 'blog',
  audience TEXT,
  description TEXT,
  status TEXT NOT NULL DEFAULT 'pending',
  current_agent TEXT,
  progress INTEGER NOT NULL DEFAULT 0,
  deleted INTEGER NOT NULL DEFAULT 0,
  started_at TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now')),
  CONSTRAINT fk_pipelinerun_org FOREIGN KEY (organization_id) REFERENCES organization(id) ON DELETE CASCADE,
  CONSTRAINT fk_pipelinerun_brief FOREIGN KEY (brief_id) REFERENCES brief(id) ON DELETE CASCADE,
  CONSTRAINT fk_pipelinerun_deliverable FOREIGN KEY (deliverable_id) REFERENCES deliverable(id) ON DELETE SET NULL,
  CONSTRAINT ck_pipelinerun_status CHECK (status IN ('pending','active','complete','failed','cancelled')),
  CONSTRAINT ck_pipelinerun_progress CHECK (progress >= 0 AND progress <= 100)
);
CREATE INDEX idx_pipelinerun_org_created ON pipelinerun(organization_id, created_at);

-- table: pipelinestep
CREATE TABLE pipelinestep (
  id INTEGER PRIMARY KEY,
  organization_id TEXT NOT NULL,
  pipeline_run_id INTEGER NOT NULL,
  agent_name TEXT NOT NULL,
  input_text TEXT NOT NULL,
  output_text TEXT NOT NULL,
  started_at TEXT NOT NULL DEFAULT (datetime('now')),
  completed_at TEXT,
  tokens_used INTEGER,
  CONSTRAINT fk_pipelinestep_org FOREIGN KEY (organization_id) REFERENCES organization(id) ON DELETE CASCADE,
  CONSTRAINT fk_pipelinestep_run FOREIGN KEY (pipeline_run_id) REFERENCES pipelinerun(id) ON DELETE CASCADE,
  CONSTRAINT ck_pipelinestep_tokens CHECK (tokens_used >= 0 OR tokens_used IS NULL)
);
CREATE INDEX idx_pipelinestep_org_run ON pipelinestep(organization_id, pipeline_run_id);

-- table: calendarintegration
CREATE TABLE calendarintegration (
  id INTEGER PRIMARY KEY,
  organization_id TEXT NOT NULL,
  user_id TEXT NOT NULL DEFAULT 'system',
  access_token_encrypted TEXT NOT NULL DEFAULT '',
  refresh_token_encrypted TEXT NOT NULL DEFAULT '',
  expires_at TEXT NOT NULL,
  calendar_id TEXT NOT NULL,
  last_synced_at TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now')),
  CONSTRAINT fk_calendarintegration_org FOREIGN KEY (organization_id) REFERENCES organization(id) ON DELETE CASCADE,
  CONSTRAINT uq_calendarintegration_org UNIQUE (organization_id)
);
CREATE INDEX idx_calendarintegration_org ON calendarintegration(organization_id);

-- table: calendarevent
CREATE TABLE calendarevent (
  id INTEGER PRIMARY KEY,
  organization_id TEXT NOT NULL,
  deliverable_id INTEGER,
  project_id INTEGER,
  google_event_id TEXT,
  title TEXT NOT NULL,
  content_type TEXT NOT NULL DEFAULT 'blog',
  description TEXT,
  notes TEXT,
  start_at TEXT NOT NULL,
  end_at TEXT,
  all_day INTEGER NOT NULL DEFAULT 1,
  status TEXT NOT NULL DEFAULT 'confirmed',
  sync_status TEXT NOT NULL DEFAULT 'offline',
  last_synced_at TEXT,
  synced_to_google_at TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now')),
  CONSTRAINT fk_calendarevent_org FOREIGN KEY (organization_id) REFERENCES organization(id) ON DELETE CASCADE,
  CONSTRAINT fk_calendarevent_deliverable FOREIGN KEY (deliverable_id) REFERENCES deliverable(id) ON DELETE SET NULL,
  CONSTRAINT fk_calendarevent_project FOREIGN KEY (project_id) REFERENCES project(id) ON DELETE SET NULL,
  CONSTRAINT uq_calendarevent_org_google_event_id UNIQUE (organization_id, google_event_id),
  CONSTRAINT ck_calendarevent_status CHECK (status IN ('pending','confirmed','cancelled','active','archived')),
  CONSTRAINT ck_calendarevent_sync_status CHECK (sync_status IN ('synced','syncing','offline'))
);
CREATE INDEX idx_calendarevent_org_start ON calendarevent(organization_id, start_at);

-- table: calendarsynclog
CREATE TABLE calendarsynclog (
  id INTEGER PRIMARY KEY,
  organization_id TEXT NOT NULL,
  event_id INTEGER,
  operation TEXT NOT NULL,
  status TEXT NOT NULL,
  error_message TEXT,
  details_json TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  CONSTRAINT fk_calendarsynclog_org FOREIGN KEY (organization_id) REFERENCES organization(id) ON DELETE CASCADE,
  CONSTRAINT fk_calendarsynclog_event FOREIGN KEY (event_id) REFERENCES calendarevent(id) ON DELETE SET NULL,
  CONSTRAINT ck_calendarsynclog_status CHECK (
    status IN ('success','error','pending','resolved_local','resolved_remote','skipped')
  )
);
CREATE INDEX idx_calendarsynclog_org_created ON calendarsynclog(organization_id, created_at);

-- table: keywordcluster
CREATE TABLE keywordcluster (
  id INTEGER PRIMARY KEY,
  organization_id TEXT NOT NULL,
  user_id TEXT NOT NULL DEFAULT 'system',
  keyword TEXT NOT NULL,
  region TEXT NOT NULL DEFAULT 'US',
  active INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now')),
  CONSTRAINT fk_keywordcluster_org FOREIGN KEY (organization_id) REFERENCES organization(id) ON DELETE CASCADE,
  CONSTRAINT uq_keywordcluster_org_keyword_region UNIQUE (organization_id, keyword, region)
);
CREATE INDEX idx_keywordcluster_org_active ON keywordcluster(organization_id, active);
CREATE INDEX idx_keywordcluster_org_keyword ON keywordcluster(organization_id, keyword);

-- table: gscquery
CREATE TABLE gscquery (
  id INTEGER PRIMARY KEY,
  organization_id TEXT NOT NULL,
  user_id TEXT NOT NULL DEFAULT 'system',
  query TEXT NOT NULL,
  page TEXT NOT NULL,
  clicks INTEGER NOT NULL,
  impressions INTEGER NOT NULL,
  ctr REAL NOT NULL,
  position REAL NOT NULL,
  date_range_start TEXT NOT NULL,
  date_range_end TEXT NOT NULL,
  fetched_at TEXT NOT NULL DEFAULT (datetime('now')),
  CONSTRAINT fk_gscquery_org FOREIGN KEY (organization_id) REFERENCES organization(id) ON DELETE CASCADE,
  CONSTRAINT ck_gscquery_clicks CHECK (clicks >= 0),
  CONSTRAINT ck_gscquery_impressions CHECK (impressions >= 0)
);
CREATE INDEX idx_gscquery_org_fetched ON gscquery(organization_id, fetched_at);

-- table: trendsdata
CREATE TABLE trendsdata (
  id INTEGER PRIMARY KEY,
  organization_id TEXT NOT NULL,
  user_id TEXT NOT NULL DEFAULT 'system',
  keyword TEXT NOT NULL,
  region TEXT NOT NULL DEFAULT 'US',
  interest_over_time_json TEXT,
  related_queries_json TEXT,
  fetched_at TEXT NOT NULL DEFAULT (datetime('now')),
  CONSTRAINT fk_trendsdata_org FOREIGN KEY (organization_id) REFERENCES organization(id) ON DELETE CASCADE
);
CREATE INDEX idx_trendsdata_org_fetched ON trendsdata(organization_id, fetched_at);
CREATE INDEX idx_trendsdata_org_keyword ON trendsdata(organization_id, keyword);

-- table: searchinsight
CREATE TABLE searchinsight (
  id INTEGER PRIMARY KEY,
  organization_id TEXT NOT NULL,
  user_id TEXT NOT NULL DEFAULT 'system',
  topic TEXT NOT NULL,
  source_item_ids TEXT NOT NULL,
  our_gsc_position REAL,
  our_gsc_clicks INTEGER,
  trends_momentum TEXT NOT NULL DEFAULT 'no_data',
  insight_text TEXT NOT NULL,
  generated_at TEXT NOT NULL DEFAULT (datetime('now')),
  CONSTRAINT fk_searchinsight_org FOREIGN KEY (organization_id) REFERENCES organization(id) ON DELETE CASCADE,
  CONSTRAINT ck_searchinsight_trends_momentum CHECK (trends_momentum IN ('rising','falling','steady','no_data'))
);
CREATE INDEX idx_searchinsight_org_generated ON searchinsight(organization_id, generated_at);
CREATE INDEX idx_searchinsight_org_momentum ON searchinsight(organization_id, trends_momentum);

-- table: runtimecredential
CREATE TABLE runtimecredential (
  id TEXT PRIMARY KEY NOT NULL,
  organization_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  runtime TEXT NOT NULL,
  encrypted_api_key TEXT NOT NULL,
  key_hash TEXT NOT NULL,
  is_valid INTEGER NOT NULL DEFAULT 0,
  last_validated_at TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  CONSTRAINT fk_runtimecredential_org FOREIGN KEY (organization_id) REFERENCES organization(id) ON DELETE CASCADE,
  CONSTRAINT uq_runtimecredential_org_user_runtime UNIQUE (organization_id, user_id, runtime),
  CONSTRAINT ck_runtimecredential_runtime CHECK (runtime IN ('anthropic','openai','copilot'))
);
CREATE INDEX idx_runtimecredential_org_user ON runtimecredential(organization_id, user_id);

-- table: usageevent
CREATE TABLE usageevent (
  id TEXT PRIMARY KEY NOT NULL,
  organization_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  event_type TEXT NOT NULL,
  tokens_input INTEGER NOT NULL DEFAULT 0,
  tokens_output INTEGER NOT NULL DEFAULT 0,
  runtime TEXT NOT NULL,
  cost_usd_estimate REAL,
  occurred_at TEXT NOT NULL DEFAULT (datetime('now')),
  CONSTRAINT fk_usageevent_org FOREIGN KEY (organization_id) REFERENCES organization(id) ON DELETE CASCADE,
  CONSTRAINT ck_usageevent_tokens_input CHECK (tokens_input >= 0),
  CONSTRAINT ck_usageevent_tokens_output CHECK (tokens_output >= 0),
  CONSTRAINT ck_usageevent_runtime CHECK (runtime IN ('anthropic','openai','copilot')),
  CONSTRAINT ck_usageevent_event_type CHECK (event_type IN ('chat_message','pipeline_run','briefing_synthesis'))
);
CREATE INDEX idx_usageevent_org_time ON usageevent(organization_id, occurred_at);

-- table: featureflag
CREATE TABLE featureflag (
  id TEXT PRIMARY KEY NOT NULL,
  organization_id TEXT NOT NULL,
  flag_name TEXT NOT NULL,
  enabled INTEGER NOT NULL DEFAULT 0,
  expires_at TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  CONSTRAINT fk_featureflag_org FOREIGN KEY (organization_id) REFERENCES organization(id) ON DELETE CASCADE,
  CONSTRAINT uq_featureflag_org_flag UNIQUE (organization_id, flag_name)
);

-- table: auditevent
CREATE TABLE auditevent (
  id TEXT PRIMARY KEY NOT NULL,
  organization_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  action TEXT NOT NULL,
  resource_type TEXT NOT NULL,
  resource_id TEXT,
  details_json TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  CONSTRAINT fk_auditevent_org FOREIGN KEY (organization_id) REFERENCES organization(id) ON DELETE CASCADE,
  CONSTRAINT ck_auditevent_resource_type CHECK (resource_type IN ('runtime_credential','subscription','user_data'))
);
CREATE INDEX idx_auditevent_org_time ON auditevent(organization_id, created_at);
CREATE INDEX idx_auditevent_action ON auditevent(action, created_at);

-- table: doctrineversion
CREATE TABLE doctrineversion (
  id TEXT PRIMARY KEY NOT NULL,
  organization_id TEXT NOT NULL,
  file_path TEXT NOT NULL,
  content_hash TEXT NOT NULL,
  content TEXT NOT NULL,
  saved_by_user_id TEXT NOT NULL,
  locked_by_user_id TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  CONSTRAINT fk_doctrineversion_org FOREIGN KEY (organization_id) REFERENCES organization(id) ON DELETE CASCADE
);
CREATE INDEX idx_doctrine_org_path_time ON doctrineversion(organization_id, file_path, created_at);
CREATE INDEX idx_doctrine_org_time ON doctrineversion(organization_id, created_at);
