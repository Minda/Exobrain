//! Note - The atomic unit of thought/information

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use uuid::Uuid;

/// The type of a Note, determining its purpose and behavior
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum NoteType {
    /// A thought to develop
    Idea,
    /// Something to execute
    Task,
    /// Information to recall
    Reference,
    /// A record of what happened
    Log,
}

impl std::fmt::Display for NoteType {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            NoteType::Idea => write!(f, "idea"),
            NoteType::Task => write!(f, "task"),
            NoteType::Reference => write!(f, "reference"),
            NoteType::Log => write!(f, "log"),
        }
    }
}

impl std::str::FromStr for NoteType {
    type Err = String;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.to_lowercase().as_str() {
            "idea" => Ok(NoteType::Idea),
            "task" => Ok(NoteType::Task),
            "reference" => Ok(NoteType::Reference),
            "log" => Ok(NoteType::Log),
            _ => Err(format!("Unknown note type: {}", s)),
        }
    }
}

/// The status of an actionable Note
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Status {
    Active,
    Completed,
    Archived,
}

impl std::fmt::Display for Status {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Status::Active => write!(f, "active"),
            Status::Completed => write!(f, "completed"),
            Status::Archived => write!(f, "archived"),
        }
    }
}

impl std::str::FromStr for Status {
    type Err = String;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.to_lowercase().as_str() {
            "active" => Ok(Status::Active),
            "completed" => Ok(Status::Completed),
            "archived" => Ok(Status::Archived),
            _ => Err(format!("Unknown status: {}", s)),
        }
    }
}

/// A Note is the atomic unit of thought/information in MinMind.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Note {
    pub id: Uuid,
    pub room_id: Uuid,
    pub title: String,
    pub content: String,
    pub note_type: NoteType,
    pub status: Option<Status>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

impl Note {
    /// Create a new Note in a Room
    pub fn new(room_id: Uuid, title: impl Into<String>, note_type: NoteType) -> Self {
        let now = Utc::now();
        Self {
            id: Uuid::new_v4(),
            room_id,
            title: title.into(),
            content: String::new(),
            note_type,
            status: None,
            created_at: now,
            updated_at: now,
        }
    }

    /// Set the content of this Note
    pub fn with_content(mut self, content: impl Into<String>) -> Self {
        self.content = content.into();
        self
    }

    /// Set the status of this Note (for actionable notes)
    pub fn with_status(mut self, status: Status) -> Self {
        self.status = Some(status);
        self
    }

    /// Update the Note's content
    pub fn update_content(&mut self, content: impl Into<String>) {
        self.content = content.into();
        self.updated_at = Utc::now();
    }

    /// Mark a task as completed
    pub fn complete(&mut self) {
        self.status = Some(Status::Completed);
        self.updated_at = Utc::now();
    }

    /// Archive this Note
    pub fn archive(&mut self) {
        self.status = Some(Status::Archived);
        self.updated_at = Utc::now();
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_new_note() {
        let room_id = Uuid::new_v4();
        let note = Note::new(room_id, "My Idea", NoteType::Idea);
        assert_eq!(note.title, "My Idea");
        assert_eq!(note.note_type, NoteType::Idea);
        assert!(note.content.is_empty());
    }

    #[test]
    fn test_task_completion() {
        let room_id = Uuid::new_v4();
        let mut note = Note::new(room_id, "Do something", NoteType::Task)
            .with_status(Status::Active);
        
        assert_eq!(note.status, Some(Status::Active));
        note.complete();
        assert_eq!(note.status, Some(Status::Completed));
    }
}
