//! Link - Bidirectional connections between notes

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use uuid::Uuid;

/// A Link represents a bidirectional connection between two Notes.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Link {
    pub id: Uuid,
    pub source_id: Uuid,
    pub target_id: Uuid,
    pub link_type: Option<String>,
    pub created_at: DateTime<Utc>,
}

impl Link {
    /// Create a new Link between two Notes
    pub fn new(source_id: Uuid, target_id: Uuid) -> Self {
        Self {
            id: Uuid::new_v4(),
            source_id,
            target_id,
            link_type: None,
            created_at: Utc::now(),
        }
    }

    /// Set the type of this Link (e.g., "related", "blocks", "supports")
    pub fn with_type(mut self, link_type: impl Into<String>) -> Self {
        self.link_type = Some(link_type.into());
        self
    }
}

/// Common link types for semantic connections
pub mod link_types {
    pub const RELATED: &str = "related";
    pub const BLOCKS: &str = "blocks";
    pub const SUPPORTS: &str = "supports";
    pub const REFERENCES: &str = "references";
    pub const DERIVED_FROM: &str = "derived_from";
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_new_link() {
        let source = Uuid::new_v4();
        let target = Uuid::new_v4();
        let link = Link::new(source, target);
        
        assert_eq!(link.source_id, source);
        assert_eq!(link.target_id, target);
        assert!(link.link_type.is_none());
    }

    #[test]
    fn test_link_with_type() {
        let source = Uuid::new_v4();
        let target = Uuid::new_v4();
        let link = Link::new(source, target).with_type(link_types::BLOCKS);
        
        assert_eq!(link.link_type.as_deref(), Some("blocks"));
    }
}
