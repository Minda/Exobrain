//! Error types for MinMind Core

use thiserror::Error;

/// Core error type for MinMind operations
#[derive(Error, Debug)]
pub enum CoreError {
    #[error("Entity not found: {0}")]
    NotFound(String),

    #[error("Invalid input: {0}")]
    InvalidInput(String),

    #[error("Serialization error: {0}")]
    Serialization(#[from] serde_json::Error),

    #[error("Internal error: {0}")]
    Internal(String),
}

pub type CoreResult<T> = Result<T, CoreError>;
