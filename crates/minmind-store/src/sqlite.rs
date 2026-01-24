//! SQLite implementation of MinMind storage

use std::path::Path;

use chrono::{DateTime, Utc};
use minmind_core::{
    ActionStatus, Article, ArticleStatus, Genius, Link, Note, NoteType, Provider, Room,
    SourceMetadata, Status, SummaryConfig, UserAction,
};
use rusqlite::{params, Connection, OptionalExtension};
use uuid::Uuid;

use crate::{migrations, StoreError, StoreResult};

/// SQLite-backed store for MinMind
pub struct Store {
    conn: Connection,
}

impl Store {
    /// Open or create a MinMind database at the given path
    pub fn open(path: impl AsRef<Path>) -> StoreResult<Self> {
        let conn = Connection::open(path)?;
        conn.execute_batch("PRAGMA foreign_keys = ON;")?;
        migrations::run_migrations(&conn)?;
        Ok(Self { conn })
    }

    /// Create an in-memory database (useful for testing)
    pub fn in_memory() -> StoreResult<Self> {
        let conn = Connection::open_in_memory()?;
        conn.execute_batch("PRAGMA foreign_keys = ON;")?;
        migrations::run_migrations(&conn)?;
        Ok(Self { conn })
    }

    // ==================== Room Operations ====================

    /// Create a new Room
    pub fn create_room(&self, room: &Room) -> StoreResult<()> {
        self.conn.execute(
            "INSERT INTO rooms (id, name, description, parent_id, created_at, updated_at)
             VALUES (?1, ?2, ?3, ?4, ?5, ?6)",
            params![
                room.id.to_string(),
                room.name,
                room.description,
                room.parent_id.map(|id| id.to_string()),
                room.created_at.to_rfc3339(),
                room.updated_at.to_rfc3339(),
            ],
        )?;
        Ok(())
    }

    /// Get a Room by ID
    pub fn get_room(&self, id: Uuid) -> StoreResult<Option<Room>> {
        self.conn
            .query_row(
                "SELECT id, name, description, parent_id, created_at, updated_at
                 FROM rooms WHERE id = ?",
                [id.to_string()],
                |row| {
                    Ok(Room {
                        id: parse_uuid(row.get::<_, String>(0)?),
                        name: row.get(1)?,
                        description: row.get(2)?,
                        parent_id: row.get::<_, Option<String>>(3)?.map(parse_uuid),
                        created_at: parse_datetime(row.get::<_, String>(4)?),
                        updated_at: parse_datetime(row.get::<_, String>(5)?),
                    })
                },
            )
            .optional()
            .map_err(StoreError::from)
    }

    /// List all Rooms
    pub fn list_rooms(&self) -> StoreResult<Vec<Room>> {
        let mut stmt = self.conn.prepare(
            "SELECT id, name, description, parent_id, created_at, updated_at
             FROM rooms ORDER BY name",
        )?;

        let rooms = stmt
            .query_map([], |row| {
                Ok(Room {
                    id: parse_uuid(row.get::<_, String>(0)?),
                    name: row.get(1)?,
                    description: row.get(2)?,
                    parent_id: row.get::<_, Option<String>>(3)?.map(parse_uuid),
                    created_at: parse_datetime(row.get::<_, String>(4)?),
                    updated_at: parse_datetime(row.get::<_, String>(5)?),
                })
            })?
            .collect::<Result<Vec<_>, _>>()?;

        Ok(rooms)
    }

    /// Update a Room
    pub fn update_room(&self, room: &Room) -> StoreResult<()> {
        let rows = self.conn.execute(
            "UPDATE rooms SET name = ?2, description = ?3, parent_id = ?4, updated_at = ?5
             WHERE id = ?1",
            params![
                room.id.to_string(),
                room.name,
                room.description,
                room.parent_id.map(|id| id.to_string()),
                room.updated_at.to_rfc3339(),
            ],
        )?;

        if rows == 0 {
            return Err(StoreError::NotFound(format!("Room {}", room.id)));
        }
        Ok(())
    }

    /// Delete a Room
    pub fn delete_room(&self, id: Uuid) -> StoreResult<()> {
        let rows = self
            .conn
            .execute("DELETE FROM rooms WHERE id = ?", [id.to_string()])?;

        if rows == 0 {
            return Err(StoreError::NotFound(format!("Room {}", id)));
        }
        Ok(())
    }

    // ==================== Note Operations ====================

    /// Create a new Note
    pub fn create_note(&self, note: &Note) -> StoreResult<()> {
        self.conn.execute(
            "INSERT INTO notes (id, room_id, title, content, note_type, status, created_at, updated_at)
             VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8)",
            params![
                note.id.to_string(),
                note.room_id.to_string(),
                note.title,
                note.content,
                note.note_type.to_string(),
                note.status.map(|s| s.to_string()),
                note.created_at.to_rfc3339(),
                note.updated_at.to_rfc3339(),
            ],
        )?;
        Ok(())
    }

    /// Get a Note by ID
    pub fn get_note(&self, id: Uuid) -> StoreResult<Option<Note>> {
        self.conn
            .query_row(
                "SELECT id, room_id, title, content, note_type, status, created_at, updated_at
                 FROM notes WHERE id = ?",
                [id.to_string()],
                |row| {
                    Ok(Note {
                        id: parse_uuid(row.get::<_, String>(0)?),
                        room_id: parse_uuid(row.get::<_, String>(1)?),
                        title: row.get(2)?,
                        content: row.get(3)?,
                        note_type: row
                            .get::<_, String>(4)?
                            .parse::<NoteType>()
                            .unwrap_or(NoteType::Idea),
                        status: row
                            .get::<_, Option<String>>(5)?
                            .and_then(|s| s.parse::<Status>().ok()),
                        created_at: parse_datetime(row.get::<_, String>(6)?),
                        updated_at: parse_datetime(row.get::<_, String>(7)?),
                    })
                },
            )
            .optional()
            .map_err(StoreError::from)
    }

    /// List Notes in a Room
    pub fn list_notes_in_room(&self, room_id: Uuid) -> StoreResult<Vec<Note>> {
        let mut stmt = self.conn.prepare(
            "SELECT id, room_id, title, content, note_type, status, created_at, updated_at
             FROM notes WHERE room_id = ? ORDER BY updated_at DESC",
        )?;

        let notes = stmt
            .query_map([room_id.to_string()], |row| {
                Ok(Note {
                    id: parse_uuid(row.get::<_, String>(0)?),
                    room_id: parse_uuid(row.get::<_, String>(1)?),
                    title: row.get(2)?,
                    content: row.get(3)?,
                    note_type: row
                        .get::<_, String>(4)?
                        .parse::<NoteType>()
                        .unwrap_or(NoteType::Idea),
                    status: row
                        .get::<_, Option<String>>(5)?
                        .and_then(|s| s.parse::<Status>().ok()),
                    created_at: parse_datetime(row.get::<_, String>(6)?),
                    updated_at: parse_datetime(row.get::<_, String>(7)?),
                })
            })?
            .collect::<Result<Vec<_>, _>>()?;

        Ok(notes)
    }

    /// Search Notes by content
    pub fn search_notes(&self, query: &str) -> StoreResult<Vec<Note>> {
        let mut stmt = self.conn.prepare(
            "SELECT n.id, n.room_id, n.title, n.content, n.note_type, n.status, n.created_at, n.updated_at
             FROM notes n
             JOIN notes_fts fts ON n.rowid = fts.rowid
             WHERE notes_fts MATCH ?
             ORDER BY rank",
        )?;

        let notes = stmt
            .query_map([query], |row| {
                Ok(Note {
                    id: parse_uuid(row.get::<_, String>(0)?),
                    room_id: parse_uuid(row.get::<_, String>(1)?),
                    title: row.get(2)?,
                    content: row.get(3)?,
                    note_type: row
                        .get::<_, String>(4)?
                        .parse::<NoteType>()
                        .unwrap_or(NoteType::Idea),
                    status: row
                        .get::<_, Option<String>>(5)?
                        .and_then(|s| s.parse::<Status>().ok()),
                    created_at: parse_datetime(row.get::<_, String>(6)?),
                    updated_at: parse_datetime(row.get::<_, String>(7)?),
                })
            })?
            .collect::<Result<Vec<_>, _>>()?;

        Ok(notes)
    }

    /// Update a Note
    pub fn update_note(&self, note: &Note) -> StoreResult<()> {
        let rows = self.conn.execute(
            "UPDATE notes SET title = ?2, content = ?3, note_type = ?4, status = ?5, updated_at = ?6
             WHERE id = ?1",
            params![
                note.id.to_string(),
                note.title,
                note.content,
                note.note_type.to_string(),
                note.status.map(|s| s.to_string()),
                note.updated_at.to_rfc3339(),
            ],
        )?;

        if rows == 0 {
            return Err(StoreError::NotFound(format!("Note {}", note.id)));
        }
        Ok(())
    }

    /// Delete a Note
    pub fn delete_note(&self, id: Uuid) -> StoreResult<()> {
        // First delete any links involving this note
        self.conn.execute(
            "DELETE FROM links WHERE source_id = ? OR target_id = ?",
            [id.to_string(), id.to_string()],
        )?;

        let rows = self
            .conn
            .execute("DELETE FROM notes WHERE id = ?", [id.to_string()])?;

        if rows == 0 {
            return Err(StoreError::NotFound(format!("Note {}", id)));
        }
        Ok(())
    }

    // ==================== Link Operations ====================

    /// Create a new Link
    pub fn create_link(&self, link: &Link) -> StoreResult<()> {
        self.conn.execute(
            "INSERT INTO links (id, source_id, target_id, link_type, created_at)
             VALUES (?1, ?2, ?3, ?4, ?5)",
            params![
                link.id.to_string(),
                link.source_id.to_string(),
                link.target_id.to_string(),
                link.link_type,
                link.created_at.to_rfc3339(),
            ],
        )?;
        Ok(())
    }

    /// Get Links for a Note (both directions)
    pub fn get_links_for_note(&self, note_id: Uuid) -> StoreResult<Vec<Link>> {
        let mut stmt = self.conn.prepare(
            "SELECT id, source_id, target_id, link_type, created_at
             FROM links WHERE source_id = ? OR target_id = ?",
        )?;

        let links = stmt
            .query_map([note_id.to_string(), note_id.to_string()], |row| {
                Ok(Link {
                    id: parse_uuid(row.get::<_, String>(0)?),
                    source_id: parse_uuid(row.get::<_, String>(1)?),
                    target_id: parse_uuid(row.get::<_, String>(2)?),
                    link_type: row.get(3)?,
                    created_at: parse_datetime(row.get::<_, String>(4)?),
                })
            })?
            .collect::<Result<Vec<_>, _>>()?;

        Ok(links)
    }

    /// Delete a Link
    pub fn delete_link(&self, id: Uuid) -> StoreResult<()> {
        let rows = self
            .conn
            .execute("DELETE FROM links WHERE id = ?", [id.to_string()])?;

        if rows == 0 {
            return Err(StoreError::NotFound(format!("Link {}", id)));
        }
        Ok(())
    }

    // ==================== Genius Operations ====================

    /// Create a new Genius
    pub fn create_genius(&self, genius: &Genius) -> StoreResult<()> {
        self.conn.execute(
            "INSERT INTO geniuses (id, name, provider, model, system_prompt, config)
             VALUES (?1, ?2, ?3, ?4, ?5, ?6)",
            params![
                genius.id.to_string(),
                genius.name,
                genius.provider.to_string(),
                genius.model,
                genius.system_prompt,
                genius.config.to_string(),
            ],
        )?;
        Ok(())
    }

    /// Get a Genius by ID
    pub fn get_genius(&self, id: Uuid) -> StoreResult<Option<Genius>> {
        self.conn
            .query_row(
                "SELECT id, name, provider, model, system_prompt, config
                 FROM geniuses WHERE id = ?",
                [id.to_string()],
                |row| {
                    Ok(Genius {
                        id: parse_uuid(row.get::<_, String>(0)?),
                        name: row.get(1)?,
                        provider: row
                            .get::<_, String>(2)?
                            .parse::<Provider>()
                            .unwrap_or(Provider::Custom),
                        model: row.get(3)?,
                        system_prompt: row.get(4)?,
                        config: serde_json::from_str(&row.get::<_, String>(5)?)
                            .unwrap_or(serde_json::json!({})),
                    })
                },
            )
            .optional()
            .map_err(StoreError::from)
    }

    /// List all Geniuses
    pub fn list_geniuses(&self) -> StoreResult<Vec<Genius>> {
        let mut stmt = self.conn.prepare(
            "SELECT id, name, provider, model, system_prompt, config
             FROM geniuses ORDER BY name",
        )?;

        let geniuses = stmt
            .query_map([], |row| {
                Ok(Genius {
                    id: parse_uuid(row.get::<_, String>(0)?),
                    name: row.get(1)?,
                    provider: row
                        .get::<_, String>(2)?
                        .parse::<Provider>()
                        .unwrap_or(Provider::Custom),
                    model: row.get(3)?,
                    system_prompt: row.get(4)?,
                    config: serde_json::from_str(&row.get::<_, String>(5)?)
                        .unwrap_or(serde_json::json!({})),
                })
            })?
            .collect::<Result<Vec<_>, _>>()?;

        Ok(geniuses)
    }

    /// Delete a Genius
    pub fn delete_genius(&self, id: Uuid) -> StoreResult<()> {
        let rows = self
            .conn
            .execute("DELETE FROM geniuses WHERE id = ?", [id.to_string()])?;

        if rows == 0 {
            return Err(StoreError::NotFound(format!("Genius {}", id)));
        }
        Ok(())
    }

    // ==================== Article Operations ====================

    /// Create a new Article
    pub fn create_article(&self, article: &Article) -> StoreResult<()> {
        let metadata_json = serde_json::to_string(&article.source_metadata)?;
        self.conn.execute(
            "INSERT INTO articles (id, url, title, raw_content, summary, room_id, status, source_metadata, created_at, updated_at)
             VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10)",
            params![
                article.id.to_string(),
                article.url,
                article.title,
                article.raw_content,
                article.summary,
                article.room_id.map(|id| id.to_string()),
                article.status.to_string(),
                metadata_json,
                article.created_at.to_rfc3339(),
                article.updated_at.to_rfc3339(),
            ],
        )?;
        Ok(())
    }

    /// Get an Article by ID
    pub fn get_article(&self, id: Uuid) -> StoreResult<Option<Article>> {
        self.conn
            .query_row(
                "SELECT id, url, title, raw_content, summary, room_id, status, source_metadata, created_at, updated_at
                 FROM articles WHERE id = ?",
                [id.to_string()],
                |row| {
                    let metadata: SourceMetadata = row
                        .get::<_, Option<String>>(7)?
                        .and_then(|s| serde_json::from_str(&s).ok())
                        .unwrap_or_default();
                    Ok(Article {
                        id: parse_uuid(row.get::<_, String>(0)?),
                        url: row.get(1)?,
                        title: row.get(2)?,
                        raw_content: row.get(3)?,
                        summary: row.get(4)?,
                        room_id: row.get::<_, Option<String>>(5)?.map(parse_uuid),
                        status: row
                            .get::<_, String>(6)?
                            .parse::<ArticleStatus>()
                            .unwrap_or(ArticleStatus::Pending),
                        source_metadata: metadata,
                        created_at: parse_datetime(row.get::<_, String>(8)?),
                        updated_at: parse_datetime(row.get::<_, String>(9)?),
                    })
                },
            )
            .optional()
            .map_err(StoreError::from)
    }

    /// Get an Article by URL
    pub fn get_article_by_url(&self, url: &str) -> StoreResult<Option<Article>> {
        self.conn
            .query_row(
                "SELECT id, url, title, raw_content, summary, room_id, status, source_metadata, created_at, updated_at
                 FROM articles WHERE url = ?",
                [url],
                |row| {
                    let metadata: SourceMetadata = row
                        .get::<_, Option<String>>(7)?
                        .and_then(|s| serde_json::from_str(&s).ok())
                        .unwrap_or_default();
                    Ok(Article {
                        id: parse_uuid(row.get::<_, String>(0)?),
                        url: row.get(1)?,
                        title: row.get(2)?,
                        raw_content: row.get(3)?,
                        summary: row.get(4)?,
                        room_id: row.get::<_, Option<String>>(5)?.map(parse_uuid),
                        status: row
                            .get::<_, String>(6)?
                            .parse::<ArticleStatus>()
                            .unwrap_or(ArticleStatus::Pending),
                        source_metadata: metadata,
                        created_at: parse_datetime(row.get::<_, String>(8)?),
                        updated_at: parse_datetime(row.get::<_, String>(9)?),
                    })
                },
            )
            .optional()
            .map_err(StoreError::from)
    }

    /// List Articles by status
    pub fn list_articles_by_status(&self, status: ArticleStatus) -> StoreResult<Vec<Article>> {
        let mut stmt = self.conn.prepare(
            "SELECT id, url, title, raw_content, summary, room_id, status, source_metadata, created_at, updated_at
             FROM articles WHERE status = ? ORDER BY updated_at DESC",
        )?;

        let articles = stmt
            .query_map([status.to_string()], |row| {
                let metadata: SourceMetadata = row
                    .get::<_, Option<String>>(7)?
                    .and_then(|s| serde_json::from_str(&s).ok())
                    .unwrap_or_default();
                Ok(Article {
                    id: parse_uuid(row.get::<_, String>(0)?),
                    url: row.get(1)?,
                    title: row.get(2)?,
                    raw_content: row.get(3)?,
                    summary: row.get(4)?,
                    room_id: row.get::<_, Option<String>>(5)?.map(parse_uuid),
                    status: row
                        .get::<_, String>(6)?
                        .parse::<ArticleStatus>()
                        .unwrap_or(ArticleStatus::Pending),
                    source_metadata: metadata,
                    created_at: parse_datetime(row.get::<_, String>(8)?),
                    updated_at: parse_datetime(row.get::<_, String>(9)?),
                })
            })?
            .collect::<Result<Vec<_>, _>>()?;

        Ok(articles)
    }

    /// List all Articles
    pub fn list_articles(&self) -> StoreResult<Vec<Article>> {
        let mut stmt = self.conn.prepare(
            "SELECT id, url, title, raw_content, summary, room_id, status, source_metadata, created_at, updated_at
             FROM articles ORDER BY updated_at DESC",
        )?;

        let articles = stmt
            .query_map([], |row| {
                let metadata: SourceMetadata = row
                    .get::<_, Option<String>>(7)?
                    .and_then(|s| serde_json::from_str(&s).ok())
                    .unwrap_or_default();
                Ok(Article {
                    id: parse_uuid(row.get::<_, String>(0)?),
                    url: row.get(1)?,
                    title: row.get(2)?,
                    raw_content: row.get(3)?,
                    summary: row.get(4)?,
                    room_id: row.get::<_, Option<String>>(5)?.map(parse_uuid),
                    status: row
                        .get::<_, String>(6)?
                        .parse::<ArticleStatus>()
                        .unwrap_or(ArticleStatus::Pending),
                    source_metadata: metadata,
                    created_at: parse_datetime(row.get::<_, String>(8)?),
                    updated_at: parse_datetime(row.get::<_, String>(9)?),
                })
            })?
            .collect::<Result<Vec<_>, _>>()?;

        Ok(articles)
    }

    /// Search Articles
    pub fn search_articles(&self, query: &str) -> StoreResult<Vec<Article>> {
        let mut stmt = self.conn.prepare(
            "SELECT a.id, a.url, a.title, a.raw_content, a.summary, a.room_id, a.status, a.source_metadata, a.created_at, a.updated_at
             FROM articles a
             JOIN articles_fts fts ON a.rowid = fts.rowid
             WHERE articles_fts MATCH ?
             ORDER BY rank",
        )?;

        let articles = stmt
            .query_map([query], |row| {
                let metadata: SourceMetadata = row
                    .get::<_, Option<String>>(7)?
                    .and_then(|s| serde_json::from_str(&s).ok())
                    .unwrap_or_default();
                Ok(Article {
                    id: parse_uuid(row.get::<_, String>(0)?),
                    url: row.get(1)?,
                    title: row.get(2)?,
                    raw_content: row.get(3)?,
                    summary: row.get(4)?,
                    room_id: row.get::<_, Option<String>>(5)?.map(parse_uuid),
                    status: row
                        .get::<_, String>(6)?
                        .parse::<ArticleStatus>()
                        .unwrap_or(ArticleStatus::Pending),
                    source_metadata: metadata,
                    created_at: parse_datetime(row.get::<_, String>(8)?),
                    updated_at: parse_datetime(row.get::<_, String>(9)?),
                })
            })?
            .collect::<Result<Vec<_>, _>>()?;

        Ok(articles)
    }

    /// Update an Article
    pub fn update_article(&self, article: &Article) -> StoreResult<()> {
        let metadata_json = serde_json::to_string(&article.source_metadata)?;
        let rows = self.conn.execute(
            "UPDATE articles SET title = ?2, raw_content = ?3, summary = ?4, room_id = ?5, status = ?6, source_metadata = ?7, updated_at = ?8
             WHERE id = ?1",
            params![
                article.id.to_string(),
                article.title,
                article.raw_content,
                article.summary,
                article.room_id.map(|id| id.to_string()),
                article.status.to_string(),
                metadata_json,
                article.updated_at.to_rfc3339(),
            ],
        )?;

        if rows == 0 {
            return Err(StoreError::NotFound(format!("Article {}", article.id)));
        }
        Ok(())
    }

    /// Delete an Article
    pub fn delete_article(&self, id: Uuid) -> StoreResult<()> {
        let rows = self
            .conn
            .execute("DELETE FROM articles WHERE id = ?", [id.to_string()])?;

        if rows == 0 {
            return Err(StoreError::NotFound(format!("Article {}", id)));
        }
        Ok(())
    }

    // ==================== SummaryConfig Operations ====================

    /// Create a new SummaryConfig
    pub fn create_summary_config(&self, config: &SummaryConfig) -> StoreResult<()> {
        self.conn.execute(
            "INSERT INTO summary_configs (id, name, system_prompt, room_id, active, created_at)
             VALUES (?1, ?2, ?3, ?4, ?5, ?6)",
            params![
                config.id.to_string(),
                config.name,
                config.system_prompt,
                config.room_id.map(|id| id.to_string()),
                config.active as i32,
                config.created_at.to_rfc3339(),
            ],
        )?;
        Ok(())
    }

    /// Get a SummaryConfig by ID
    pub fn get_summary_config(&self, id: Uuid) -> StoreResult<Option<SummaryConfig>> {
        self.conn
            .query_row(
                "SELECT id, name, system_prompt, room_id, active, created_at
                 FROM summary_configs WHERE id = ?",
                [id.to_string()],
                |row| {
                    Ok(SummaryConfig {
                        id: parse_uuid(row.get::<_, String>(0)?),
                        name: row.get(1)?,
                        system_prompt: row.get(2)?,
                        room_id: row.get::<_, Option<String>>(3)?.map(parse_uuid),
                        active: row.get::<_, i32>(4)? != 0,
                        created_at: parse_datetime(row.get::<_, String>(5)?),
                    })
                },
            )
            .optional()
            .map_err(StoreError::from)
    }

    /// Get the active SummaryConfig for a room (falls back to global if none)
    pub fn get_active_summary_config(&self, room_id: Option<Uuid>) -> StoreResult<Option<SummaryConfig>> {
        // First try room-specific config
        if let Some(rid) = room_id {
            let room_config = self.conn
                .query_row(
                    "SELECT id, name, system_prompt, room_id, active, created_at
                     FROM summary_configs WHERE room_id = ? AND active = 1 LIMIT 1",
                    [rid.to_string()],
                    |row| {
                        Ok(SummaryConfig {
                            id: parse_uuid(row.get::<_, String>(0)?),
                            name: row.get(1)?,
                            system_prompt: row.get(2)?,
                            room_id: row.get::<_, Option<String>>(3)?.map(parse_uuid),
                            active: row.get::<_, i32>(4)? != 0,
                            created_at: parse_datetime(row.get::<_, String>(5)?),
                        })
                    },
                )
                .optional()?;

            if room_config.is_some() {
                return Ok(room_config);
            }
        }

        // Fall back to global config
        self.conn
            .query_row(
                "SELECT id, name, system_prompt, room_id, active, created_at
                 FROM summary_configs WHERE room_id IS NULL AND active = 1 LIMIT 1",
                [],
                |row| {
                    Ok(SummaryConfig {
                        id: parse_uuid(row.get::<_, String>(0)?),
                        name: row.get(1)?,
                        system_prompt: row.get(2)?,
                        room_id: row.get::<_, Option<String>>(3)?.map(parse_uuid),
                        active: row.get::<_, i32>(4)? != 0,
                        created_at: parse_datetime(row.get::<_, String>(5)?),
                    })
                },
            )
            .optional()
            .map_err(StoreError::from)
    }

    /// List all SummaryConfigs
    pub fn list_summary_configs(&self) -> StoreResult<Vec<SummaryConfig>> {
        let mut stmt = self.conn.prepare(
            "SELECT id, name, system_prompt, room_id, active, created_at
             FROM summary_configs ORDER BY room_id IS NULL DESC, name",
        )?;

        let configs = stmt
            .query_map([], |row| {
                Ok(SummaryConfig {
                    id: parse_uuid(row.get::<_, String>(0)?),
                    name: row.get(1)?,
                    system_prompt: row.get(2)?,
                    room_id: row.get::<_, Option<String>>(3)?.map(parse_uuid),
                    active: row.get::<_, i32>(4)? != 0,
                    created_at: parse_datetime(row.get::<_, String>(5)?),
                })
            })?
            .collect::<Result<Vec<_>, _>>()?;

        Ok(configs)
    }

    /// Update a SummaryConfig
    pub fn update_summary_config(&self, config: &SummaryConfig) -> StoreResult<()> {
        let rows = self.conn.execute(
            "UPDATE summary_configs SET name = ?2, system_prompt = ?3, room_id = ?4, active = ?5
             WHERE id = ?1",
            params![
                config.id.to_string(),
                config.name,
                config.system_prompt,
                config.room_id.map(|id| id.to_string()),
                config.active as i32,
            ],
        )?;

        if rows == 0 {
            return Err(StoreError::NotFound(format!("SummaryConfig {}", config.id)));
        }
        Ok(())
    }

    /// Delete a SummaryConfig
    pub fn delete_summary_config(&self, id: Uuid) -> StoreResult<()> {
        let rows = self
            .conn
            .execute("DELETE FROM summary_configs WHERE id = ?", [id.to_string()])?;

        if rows == 0 {
            return Err(StoreError::NotFound(format!("SummaryConfig {}", id)));
        }
        Ok(())
    }

    // ==================== UserAction Operations ====================

    /// Create a new UserAction
    pub fn create_user_action(&self, action: &UserAction) -> StoreResult<()> {
        self.conn.execute(
            "INSERT INTO user_actions (id, plan_id, source_file, line_number, title, description, status, created_at, completed_at)
             VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9)",
            params![
                action.id.to_string(),
                action.plan_id.map(|id| id.to_string()),
                action.source_file,
                action.line_number,
                action.title,
                action.description,
                action.status.to_string(),
                action.created_at.to_rfc3339(),
                action.completed_at.map(|dt| dt.to_rfc3339()),
            ],
        )?;
        Ok(())
    }

    /// Get a UserAction by ID
    pub fn get_user_action(&self, id: Uuid) -> StoreResult<Option<UserAction>> {
        self.conn
            .query_row(
                "SELECT id, plan_id, source_file, line_number, title, description, status, created_at, completed_at
                 FROM user_actions WHERE id = ?",
                [id.to_string()],
                |row| {
                    Ok(UserAction {
                        id: parse_uuid(row.get::<_, String>(0)?),
                        plan_id: row.get::<_, Option<String>>(1)?.map(parse_uuid),
                        source_file: row.get(2)?,
                        line_number: row.get(3)?,
                        title: row.get(4)?,
                        description: row.get(5)?,
                        status: row
                            .get::<_, String>(6)?
                            .parse::<ActionStatus>()
                            .unwrap_or(ActionStatus::Pending),
                        created_at: parse_datetime(row.get::<_, String>(7)?),
                        completed_at: row.get::<_, Option<String>>(8)?.map(parse_datetime),
                    })
                },
            )
            .optional()
            .map_err(StoreError::from)
    }

    /// List all UserActions
    pub fn list_user_actions(&self) -> StoreResult<Vec<UserAction>> {
        let mut stmt = self.conn.prepare(
            "SELECT id, plan_id, source_file, line_number, title, description, status, created_at, completed_at
             FROM user_actions ORDER BY created_at DESC",
        )?;

        let actions = stmt
            .query_map([], |row| {
                Ok(UserAction {
                    id: parse_uuid(row.get::<_, String>(0)?),
                    plan_id: row.get::<_, Option<String>>(1)?.map(parse_uuid),
                    source_file: row.get(2)?,
                    line_number: row.get(3)?,
                    title: row.get(4)?,
                    description: row.get(5)?,
                    status: row
                        .get::<_, String>(6)?
                        .parse::<ActionStatus>()
                        .unwrap_or(ActionStatus::Pending),
                    created_at: parse_datetime(row.get::<_, String>(7)?),
                    completed_at: row.get::<_, Option<String>>(8)?.map(parse_datetime),
                })
            })?
            .collect::<Result<Vec<_>, _>>()?;

        Ok(actions)
    }

    /// List UserActions by status
    pub fn list_user_actions_by_status(&self, status: ActionStatus) -> StoreResult<Vec<UserAction>> {
        let mut stmt = self.conn.prepare(
            "SELECT id, plan_id, source_file, line_number, title, description, status, created_at, completed_at
             FROM user_actions WHERE status = ? ORDER BY created_at DESC",
        )?;

        let actions = stmt
            .query_map([status.to_string()], |row| {
                Ok(UserAction {
                    id: parse_uuid(row.get::<_, String>(0)?),
                    plan_id: row.get::<_, Option<String>>(1)?.map(parse_uuid),
                    source_file: row.get(2)?,
                    line_number: row.get(3)?,
                    title: row.get(4)?,
                    description: row.get(5)?,
                    status: row
                        .get::<_, String>(6)?
                        .parse::<ActionStatus>()
                        .unwrap_or(ActionStatus::Pending),
                    created_at: parse_datetime(row.get::<_, String>(7)?),
                    completed_at: row.get::<_, Option<String>>(8)?.map(parse_datetime),
                })
            })?
            .collect::<Result<Vec<_>, _>>()?;

        Ok(actions)
    }

    /// List UserActions by source file
    pub fn list_user_actions_by_source(&self, source_file: &str) -> StoreResult<Vec<UserAction>> {
        let mut stmt = self.conn.prepare(
            "SELECT id, plan_id, source_file, line_number, title, description, status, created_at, completed_at
             FROM user_actions WHERE source_file = ? ORDER BY line_number ASC",
        )?;

        let actions = stmt
            .query_map([source_file], |row| {
                Ok(UserAction {
                    id: parse_uuid(row.get::<_, String>(0)?),
                    plan_id: row.get::<_, Option<String>>(1)?.map(parse_uuid),
                    source_file: row.get(2)?,
                    line_number: row.get(3)?,
                    title: row.get(4)?,
                    description: row.get(5)?,
                    status: row
                        .get::<_, String>(6)?
                        .parse::<ActionStatus>()
                        .unwrap_or(ActionStatus::Pending),
                    created_at: parse_datetime(row.get::<_, String>(7)?),
                    completed_at: row.get::<_, Option<String>>(8)?.map(parse_datetime),
                })
            })?
            .collect::<Result<Vec<_>, _>>()?;

        Ok(actions)
    }

    /// Update a UserAction
    pub fn update_user_action(&self, action: &UserAction) -> StoreResult<()> {
        let rows = self.conn.execute(
            "UPDATE user_actions SET plan_id = ?2, source_file = ?3, line_number = ?4, title = ?5, description = ?6, status = ?7, completed_at = ?8
             WHERE id = ?1",
            params![
                action.id.to_string(),
                action.plan_id.map(|id| id.to_string()),
                action.source_file,
                action.line_number,
                action.title,
                action.description,
                action.status.to_string(),
                action.completed_at.map(|dt| dt.to_rfc3339()),
            ],
        )?;

        if rows == 0 {
            return Err(StoreError::NotFound(format!("UserAction {}", action.id)));
        }
        Ok(())
    }

    /// Delete a UserAction
    pub fn delete_user_action(&self, id: Uuid) -> StoreResult<()> {
        let rows = self
            .conn
            .execute("DELETE FROM user_actions WHERE id = ?", [id.to_string()])?;

        if rows == 0 {
            return Err(StoreError::NotFound(format!("UserAction {}", id)));
        }
        Ok(())
    }

    /// Delete all UserActions from a source file (useful when re-syncing)
    pub fn delete_user_actions_by_source(&self, source_file: &str) -> StoreResult<usize> {
        let rows = self
            .conn
            .execute("DELETE FROM user_actions WHERE source_file = ?", [source_file])?;
        Ok(rows)
    }
}

// Helper functions for parsing stored values
fn parse_uuid(s: String) -> Uuid {
    Uuid::parse_str(&s).unwrap_or_else(|_| Uuid::nil())
}

fn parse_datetime(s: String) -> DateTime<Utc> {
    DateTime::parse_from_rfc3339(&s)
        .map(|dt| dt.with_timezone(&Utc))
        .unwrap_or_else(|_| Utc::now())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_room_crud() -> StoreResult<()> {
        let store = Store::in_memory()?;

        // Create
        let room = Room::new("Test Room").with_description("A test room");
        store.create_room(&room)?;

        // Read
        let fetched = store.get_room(room.id)?.expect("Room should exist");
        assert_eq!(fetched.name, "Test Room");

        // List
        let rooms = store.list_rooms()?;
        assert_eq!(rooms.len(), 1);

        // Delete
        store.delete_room(room.id)?;
        assert!(store.get_room(room.id)?.is_none());

        Ok(())
    }

    #[test]
    fn test_note_crud() -> StoreResult<()> {
        let store = Store::in_memory()?;

        // Create a room first
        let room = Room::new("Notes Room");
        store.create_room(&room)?;

        // Create a note
        let note =
            Note::new(room.id, "Test Note", minmind_core::NoteType::Idea).with_content("Some content");
        store.create_note(&note)?;

        // Read
        let fetched = store.get_note(note.id)?.expect("Note should exist");
        assert_eq!(fetched.title, "Test Note");
        assert_eq!(fetched.content, "Some content");

        // Search
        let results = store.search_notes("content")?;
        assert_eq!(results.len(), 1);

        Ok(())
    }

    #[test]
    fn test_article_crud() -> StoreResult<()> {
        let store = Store::in_memory()?;

        // Create
        let article = Article::new(
            "https://example.com/article",
            "Test Article",
            "Article content here",
        );
        store.create_article(&article)?;

        // Read
        let fetched = store.get_article(article.id)?.expect("Article should exist");
        assert_eq!(fetched.title, "Test Article");
        assert_eq!(fetched.status, ArticleStatus::Pending);

        // Read by URL
        let by_url = store.get_article_by_url("https://example.com/article")?;
        assert!(by_url.is_some());

        // List by status
        let pending = store.list_articles_by_status(ArticleStatus::Pending)?;
        assert_eq!(pending.len(), 1);

        // Update
        let mut article = fetched;
        article.set_summary("A summary");
        store.update_article(&article)?;
        let updated = store.get_article(article.id)?.unwrap();
        assert_eq!(updated.status, ArticleStatus::Summarized);

        Ok(())
    }

    #[test]
    fn test_summary_config() -> StoreResult<()> {
        let store = Store::in_memory()?;

        // Create global config
        let global = SummaryConfig::new_global("Default", "Summarize for learning");
        store.create_summary_config(&global)?;

        // Create a room and room-specific config
        let room = Room::new("Technical");
        store.create_room(&room)?;
        let room_config = SummaryConfig::new_for_room("Technical", "Summarize technically", room.id);
        store.create_summary_config(&room_config)?;

        // Get active config for room (should return room-specific)
        let active = store.get_active_summary_config(Some(room.id))?.unwrap();
        assert_eq!(active.name, "Technical");

        // Get active config for no room (should return global)
        let global_active = store.get_active_summary_config(None)?.unwrap();
        assert_eq!(global_active.name, "Default");

        Ok(())
    }

    #[test]
    fn test_user_action_crud() -> StoreResult<()> {
        let store = Store::in_memory()?;

        // Create
        let action = UserAction::from_plan(
            "Configure API keys",
            "plans/001-foundation.md",
            42,
        );
        store.create_user_action(&action)?;

        // Read
        let fetched = store.get_user_action(action.id)?.expect("Action should exist");
        assert_eq!(fetched.title, "Configure API keys");
        assert_eq!(fetched.status, ActionStatus::Pending);

        // List
        let actions = store.list_user_actions()?;
        assert_eq!(actions.len(), 1);

        // List by status
        let pending = store.list_user_actions_by_status(ActionStatus::Pending)?;
        assert_eq!(pending.len(), 1);

        // List by source
        let by_source = store.list_user_actions_by_source("plans/001-foundation.md")?;
        assert_eq!(by_source.len(), 1);

        // Update (complete the action)
        let mut action = fetched;
        action.complete();
        store.update_user_action(&action)?;
        let updated = store.get_user_action(action.id)?.unwrap();
        assert_eq!(updated.status, ActionStatus::Completed);
        assert!(updated.completed_at.is_some());

        // Delete
        store.delete_user_action(action.id)?;
        assert!(store.get_user_action(action.id)?.is_none());

        Ok(())
    }
}
