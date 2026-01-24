-- Article ingestion and summarization tables

-- Articles table
CREATE TABLE articles (
    id TEXT PRIMARY KEY,
    url TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    raw_content TEXT NOT NULL,
    summary TEXT,
    room_id TEXT REFERENCES rooms(id),
    status TEXT NOT NULL DEFAULT 'pending',
    source_metadata TEXT,  -- JSON
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Summary configs table
CREATE TABLE summary_configs (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    system_prompt TEXT NOT NULL,
    room_id TEXT REFERENCES rooms(id),  -- NULL = global
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL
);

-- Indexes
CREATE INDEX idx_articles_status ON articles(status);
CREATE INDEX idx_articles_room ON articles(room_id);
CREATE INDEX idx_articles_url ON articles(url);
CREATE INDEX idx_summary_configs_room ON summary_configs(room_id);
CREATE INDEX idx_summary_configs_active ON summary_configs(active);

-- Full-text search for articles
CREATE VIRTUAL TABLE articles_fts USING fts5(
    title, raw_content, summary, content='articles', content_rowid='rowid'
);

-- Triggers to keep FTS in sync
CREATE TRIGGER articles_ai AFTER INSERT ON articles BEGIN
    INSERT INTO articles_fts(rowid, title, raw_content, summary) 
    VALUES (new.rowid, new.title, new.raw_content, new.summary);
END;

CREATE TRIGGER articles_ad AFTER DELETE ON articles BEGIN
    INSERT INTO articles_fts(articles_fts, rowid, title, raw_content, summary) 
    VALUES('delete', old.rowid, old.title, old.raw_content, old.summary);
END;

CREATE TRIGGER articles_au AFTER UPDATE ON articles BEGIN
    INSERT INTO articles_fts(articles_fts, rowid, title, raw_content, summary) 
    VALUES('delete', old.rowid, old.title, old.raw_content, old.summary);
    INSERT INTO articles_fts(rowid, title, raw_content, summary) 
    VALUES (new.rowid, new.title, new.raw_content, new.summary);
END;
