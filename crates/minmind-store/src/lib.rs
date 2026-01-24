//! MinMind Store - SQLite persistence layer
//!
//! This crate provides local-first persistence for MinMind using SQLite.

mod error;
mod migrations;
mod sqlite;

pub use error::*;
pub use sqlite::*;
