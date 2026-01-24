//! SummaryConfig - Configuration for personalized article summarization

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use uuid::Uuid;

/// Configuration for how articles should be summarized.
/// 
/// SummaryConfig allows personalization at two levels:
/// - Global: A default config with `room_id = None` applies to all articles
/// - Per-Room: Configs with a `room_id` override the global config for that room
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SummaryConfig {
    pub id: Uuid,
    pub name: String,
    pub system_prompt: String,
    pub room_id: Option<Uuid>,
    pub active: bool,
    pub created_at: DateTime<Utc>,
}

impl SummaryConfig {
    /// Create a new global SummaryConfig
    pub fn new_global(name: impl Into<String>, system_prompt: impl Into<String>) -> Self {
        Self {
            id: Uuid::new_v4(),
            name: name.into(),
            system_prompt: system_prompt.into(),
            room_id: None,
            active: true,
            created_at: Utc::now(),
        }
    }

    /// Create a new room-specific SummaryConfig
    pub fn new_for_room(
        name: impl Into<String>,
        system_prompt: impl Into<String>,
        room_id: Uuid,
    ) -> Self {
        Self {
            id: Uuid::new_v4(),
            name: name.into(),
            system_prompt: system_prompt.into(),
            room_id: Some(room_id),
            active: true,
            created_at: Utc::now(),
        }
    }

    /// Deactivate this config
    pub fn deactivate(&mut self) {
        self.active = false;
    }

    /// Activate this config
    pub fn activate(&mut self) {
        self.active = true;
    }

    /// Check if this is a global config
    pub fn is_global(&self) -> bool {
        self.room_id.is_none()
    }
}

/// Default summary prompt that focuses on understanding "why" first
pub const DEFAULT_SUMMARY_PROMPT: &str = r#"Summarize this article for someone who learns by understanding the "why" first, then concrete examples.

Structure your summary as:
1. **Core Insight** - The fundamental idea or thesis (1-2 sentences)
2. **Why It Matters** - Context and significance 
3. **Key Points** - Bullet points of main arguments/findings
4. **Concrete Examples** - Specific examples or case studies mentioned
5. **Actionable Takeaways** - What can be applied immediately

Keep the tone conversational but precise. Focus on signal over noise."#;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_global_config() {
        let config = SummaryConfig::new_global("Default", DEFAULT_SUMMARY_PROMPT);
        assert!(config.is_global());
        assert!(config.active);
    }

    #[test]
    fn test_room_config() {
        let room_id = Uuid::new_v4();
        let config = SummaryConfig::new_for_room("Technical", "Summarize technically", room_id);
        assert!(!config.is_global());
        assert_eq!(config.room_id, Some(room_id));
    }
}
