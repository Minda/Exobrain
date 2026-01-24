//! Database migrations for MinMind

use rusqlite::Connection;

use crate::StoreResult;

/// Run all database migrations
pub fn run_migrations(conn: &Connection) -> StoreResult<()> {
    // Create migrations table if it doesn't exist
    conn.execute(
        "CREATE TABLE IF NOT EXISTS _migrations (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            applied_at TEXT NOT NULL
        )",
        [],
    )?;

    // Run each migration in order
    let migrations: &[(&str, &str)] = &[
        ("001_initial_schema", include_str!("../migrations/001_initial_schema.sql")),
        ("002_articles", include_str!("../migrations/002_articles.sql")),
        ("003_user_actions", include_str!("../migrations/003_user_actions.sql")),
    ];

    for (name, sql) in migrations {
        let already_applied: bool = conn.query_row(
            "SELECT EXISTS(SELECT 1 FROM _migrations WHERE name = ?)",
            [name],
            |row| row.get(0),
        )?;

        if !already_applied {
            conn.execute_batch(sql)?;
            conn.execute(
                "INSERT INTO _migrations (name, applied_at) VALUES (?, datetime('now'))",
                [name],
            )?;
        }
    }

    Ok(())
}
