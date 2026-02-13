//! Room - A conceptual space for organizing related thoughts and work

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use uuid::Uuid;

/// A Room is a conceptual space for organizing related thoughts and work.
/// Rooms can nest to create hierarchical organization.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Room {
    pub id: Uuid,
    pub name: String,
    pub description: Option<String>,
    pub parent_id: Option<Uuid>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

impl Room {
    /// Create a new Room with the given name
    pub fn new(name: impl Into<String>) -> Self {
        let now = Utc::now();
        Self {
            id: Uuid::new_v4(),
            name: name.into(),
            description: None,
            parent_id: None,
            created_at: now,
            updated_at: now,
        }
    }

    /// Set the description for this Room
    pub fn with_description(mut self, description: impl Into<String>) -> Self {
        self.description = Some(description.into());
        self
    }

    /// Set the parent Room for nesting
    pub fn with_parent(mut self, parent_id: Uuid) -> Self {
        self.parent_id = Some(parent_id);
        self
    }

    /// Update the Room's name
    pub fn rename(&mut self, name: impl Into<String>) {
        self.name = name.into();
        self.updated_at = Utc::now();
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_new_room() {
        let room = Room::new("Work");
        assert_eq!(room.name, "Work");
        assert!(room.description.is_none());
        assert!(room.parent_id.is_none());
    }

    #[test]
    fn test_room_with_description() {
        let room = Room::new("Learning").with_description("A place for learning new things");
        assert_eq!(room.description.as_deref(), Some("A place for learning new things"));
    }
}
