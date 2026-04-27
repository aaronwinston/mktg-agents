-- ForgeOS migration 0003
-- Purpose: Persist audit trail for all data modifications.

CREATE TABLE IF NOT EXISTS auditlog (
  id TEXT PRIMARY KEY NOT NULL,
  organization_id TEXT NOT NULL,
  user_id TEXT,
  operation TEXT NOT NULL,
  table_name TEXT NOT NULL,
  record_id TEXT,
  old_values_json TEXT,
  new_values_json TEXT,
  request_method TEXT,
  request_path TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  CONSTRAINT fk_auditlog_org FOREIGN KEY (organization_id) REFERENCES organization(id) ON DELETE CASCADE,
  CONSTRAINT ck_auditlog_operation CHECK (operation IN ('CREATE','UPDATE','DELETE'))
);

CREATE INDEX IF NOT EXISTS idx_auditlog_org_time ON auditlog(organization_id, created_at);
CREATE INDEX IF NOT EXISTS idx_auditlog_table_record ON auditlog(table_name, record_id, created_at);
CREATE INDEX IF NOT EXISTS idx_auditlog_user_time ON auditlog(user_id, created_at);
