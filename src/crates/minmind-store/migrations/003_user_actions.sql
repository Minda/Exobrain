-- User Actions table
-- Stores tasks that require human intervention, extracted from plan files
-- or created manually via CLI

CREATE TABLE user_actions (
    id TEXT PRIMARY KEY,
    plan_id TEXT REFERENCES notes(id) ON DELETE SET NULL,
    source_file TEXT,
    line_number INTEGER,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TEXT NOT NULL,
    completed_at TEXT
);

-- Index for filtering by status (most common query)
CREATE INDEX idx_user_actions_status ON user_actions(status);

-- Index for filtering by source file
CREATE INDEX idx_user_actions_source ON user_actions(source_file);

-- Index for filtering by plan
CREATE INDEX idx_user_actions_plan ON user_actions(plan_id);
