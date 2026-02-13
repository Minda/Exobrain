//! UserAction - Tasks that require human action
//!
//! UserActions are extracted from plan files (marked with `[USER]`) and stored
//! in the database for tracking. They sync bidirectionally between markdown
//! files and SQLite.

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use uuid::Uuid;

/// The status of a user action
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum ActionStatus {
    /// Not yet started
    Pending,
    /// Currently being worked on
    InProgress,
    /// Successfully completed
    Completed,
    /// Intentionally skipped
    Skipped,
}

impl Default for ActionStatus {
    fn default() -> Self {
        ActionStatus::Pending
    }
}

impl std::fmt::Display for ActionStatus {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            ActionStatus::Pending => write!(f, "pending"),
            ActionStatus::InProgress => write!(f, "in_progress"),
            ActionStatus::Completed => write!(f, "completed"),
            ActionStatus::Skipped => write!(f, "skipped"),
        }
    }
}

impl std::str::FromStr for ActionStatus {
    type Err = String;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.to_lowercase().as_str() {
            "pending" => Ok(ActionStatus::Pending),
            "in_progress" | "inprogress" => Ok(ActionStatus::InProgress),
            "completed" | "done" => Ok(ActionStatus::Completed),
            "skipped" | "skip" => Ok(ActionStatus::Skipped),
            _ => Err(format!("Unknown action status: {}", s)),
        }
    }
}

/// A UserAction represents a task that requires human intervention.
/// 
/// These are typically extracted from plan files where they're marked with
/// `- [USER]` syntax, but can also be created manually via CLI.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UserAction {
    pub id: Uuid,
    /// Optional link to a plan Note
    pub plan_id: Option<Uuid>,
    /// Source file path (e.g., "plans/001-foundation.md")
    pub source_file: Option<String>,
    /// Line number in the source file (for syncing back)
    pub line_number: Option<u32>,
    /// The action title/description
    pub title: String,
    /// Optional longer description
    pub description: Option<String>,
    /// Current status of the action
    pub status: ActionStatus,
    /// When this action was created
    pub created_at: DateTime<Utc>,
    /// When this action was completed (if completed)
    pub completed_at: Option<DateTime<Utc>>,
}

impl UserAction {
    /// Create a new UserAction with a title
    pub fn new(title: impl Into<String>) -> Self {
        let now = Utc::now();
        Self {
            id: Uuid::new_v4(),
            plan_id: None,
            source_file: None,
            line_number: None,
            title: title.into(),
            description: None,
            status: ActionStatus::Pending,
            created_at: now,
            completed_at: None,
        }
    }

    /// Create a UserAction from a plan file
    pub fn from_plan(
        title: impl Into<String>,
        source_file: impl Into<String>,
        line_number: u32,
    ) -> Self {
        Self {
            source_file: Some(source_file.into()),
            line_number: Some(line_number),
            ..Self::new(title)
        }
    }

    /// Set the plan ID
    pub fn with_plan_id(mut self, plan_id: Uuid) -> Self {
        self.plan_id = Some(plan_id);
        self
    }

    /// Set the description
    pub fn with_description(mut self, description: impl Into<String>) -> Self {
        self.description = Some(description.into());
        self
    }

    /// Mark this action as in progress
    pub fn start(&mut self) {
        self.status = ActionStatus::InProgress;
    }

    /// Mark this action as completed
    pub fn complete(&mut self) {
        self.status = ActionStatus::Completed;
        self.completed_at = Some(Utc::now());
    }

    /// Mark this action as skipped
    pub fn skip(&mut self) {
        self.status = ActionStatus::Skipped;
    }

    /// Check if this action is done (completed or skipped)
    pub fn is_done(&self) -> bool {
        matches!(self.status, ActionStatus::Completed | ActionStatus::Skipped)
    }

    /// Check if this action is pending
    pub fn is_pending(&self) -> bool {
        matches!(self.status, ActionStatus::Pending)
    }

    /// Get the marker string for this action's status in markdown
    pub fn marker(&self) -> &'static str {
        match self.status {
            ActionStatus::Pending => "[USER]",
            ActionStatus::InProgress => "[USER:wip]",
            ActionStatus::Completed => "[USER:done]",
            ActionStatus::Skipped => "[USER:skip]",
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_new_user_action() {
        let action = UserAction::new("Configure API keys");
        assert_eq!(action.title, "Configure API keys");
        assert_eq!(action.status, ActionStatus::Pending);
        assert!(action.is_pending());
        assert!(!action.is_done());
    }

    #[test]
    fn test_from_plan() {
        let action = UserAction::from_plan(
            "Review design",
            "plans/001-foundation.md",
            42,
        );
        assert_eq!(action.source_file.as_deref(), Some("plans/001-foundation.md"));
        assert_eq!(action.line_number, Some(42));
    }

    #[test]
    fn test_complete_action() {
        let mut action = UserAction::new("Do something");
        assert!(action.completed_at.is_none());
        
        action.complete();
        
        assert_eq!(action.status, ActionStatus::Completed);
        assert!(action.completed_at.is_some());
        assert!(action.is_done());
    }

    #[test]
    fn test_action_status_display() {
        assert_eq!(ActionStatus::Pending.to_string(), "pending");
        assert_eq!(ActionStatus::InProgress.to_string(), "in_progress");
        assert_eq!(ActionStatus::Completed.to_string(), "completed");
        assert_eq!(ActionStatus::Skipped.to_string(), "skipped");
    }

    #[test]
    fn test_action_status_parse() {
        assert_eq!("pending".parse::<ActionStatus>().unwrap(), ActionStatus::Pending);
        assert_eq!("in_progress".parse::<ActionStatus>().unwrap(), ActionStatus::InProgress);
        assert_eq!("done".parse::<ActionStatus>().unwrap(), ActionStatus::Completed);
        assert_eq!("skip".parse::<ActionStatus>().unwrap(), ActionStatus::Skipped);
    }

    #[test]
    fn test_marker() {
        let mut action = UserAction::new("Test");
        assert_eq!(action.marker(), "[USER]");
        
        action.start();
        assert_eq!(action.marker(), "[USER:wip]");
        
        action.complete();
        assert_eq!(action.marker(), "[USER:done]");
    }
}
