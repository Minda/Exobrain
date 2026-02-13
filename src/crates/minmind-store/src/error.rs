//! Error types for MinMind Store

use thiserror::Error;

/// Store error type for MinMind persistence operations
#[derive(Error, Debug)]
pub enum StoreError {
    #[error("Database error: {0}")]
    Database(#[from] rusqlite::Error),

    #[error("Entity not found: {0}")]
    NotFound(String),

    #[error("Serialization error: {0}")]
    Serialization(#[from] serde_json::Error),

    #[error("Migration error: {0}")]
    Migration(String),

    #[error("Core error: {0}")]
    Core(#[from] minmind_core::CoreError),
}

pub type StoreResult<T> = Result<T, StoreError>;
