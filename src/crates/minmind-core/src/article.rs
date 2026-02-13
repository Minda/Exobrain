//! Article - Content captured from external sources for summarization and review

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use uuid::Uuid;

/// The status of an Article in the processing pipeline
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum ArticleStatus {
    /// Fetched, awaiting summarization
    Pending,
    /// Has summary, awaiting review
    Summarized,
    /// Approved, converted to Note
    Reviewed,
    /// Dismissed or saved for later
    Archived,
}

impl Default for ArticleStatus {
    fn default() -> Self {
        Self::Pending
    }
}

impl std::fmt::Display for ArticleStatus {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            ArticleStatus::Pending => write!(f, "pending"),
            ArticleStatus::Summarized => write!(f, "summarized"),
            ArticleStatus::Reviewed => write!(f, "reviewed"),
            ArticleStatus::Archived => write!(f, "archived"),
        }
    }
}

impl std::str::FromStr for ArticleStatus {
    type Err = String;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.to_lowercase().as_str() {
            "pending" => Ok(ArticleStatus::Pending),
            "summarized" => Ok(ArticleStatus::Summarized),
            "reviewed" => Ok(ArticleStatus::Reviewed),
            "archived" => Ok(ArticleStatus::Archived),
            _ => Err(format!("Unknown article status: {}", s)),
        }
    }
}

/// Metadata about the source of an article
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct SourceMetadata {
    /// Author of the article
    pub author: Option<String>,
    /// Publication date
    pub published_at: Option<DateTime<Utc>>,
    /// Site name (e.g., "Every")
    pub site_name: Option<String>,
    /// Description/excerpt
    pub description: Option<String>,
    /// Featured image URL
    pub image_url: Option<String>,
}

/// An Article represents content captured from an external source for processing.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Article {
    pub id: Uuid,
    pub url: String,
    pub title: String,
    pub raw_content: String,
    pub summary: Option<String>,
    pub room_id: Option<Uuid>,
    pub status: ArticleStatus,
    pub source_metadata: SourceMetadata,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

impl Article {
    /// Create a new Article from a URL
    pub fn new(url: impl Into<String>, title: impl Into<String>, content: impl Into<String>) -> Self {
        let now = Utc::now();
        Self {
            id: Uuid::new_v4(),
            url: url.into(),
            title: title.into(),
            raw_content: content.into(),
            summary: None,
            room_id: None,
            status: ArticleStatus::Pending,
            source_metadata: SourceMetadata::default(),
            created_at: now,
            updated_at: now,
        }
    }

    /// Set the room this article belongs to
    pub fn with_room(mut self, room_id: Uuid) -> Self {
        self.room_id = Some(room_id);
        self
    }

    /// Set source metadata
    pub fn with_metadata(mut self, metadata: SourceMetadata) -> Self {
        self.source_metadata = metadata;
        self
    }

    /// Add a summary to this article
    pub fn set_summary(&mut self, summary: impl Into<String>) {
        self.summary = Some(summary.into());
        self.status = ArticleStatus::Summarized;
        self.updated_at = Utc::now();
    }

    /// Mark as reviewed
    pub fn mark_reviewed(&mut self) {
        self.status = ArticleStatus::Reviewed;
        self.updated_at = Utc::now();
    }

    /// Archive this article
    pub fn archive(&mut self) {
        self.status = ArticleStatus::Archived;
        self.updated_at = Utc::now();
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_new_article() {
        let article = Article::new(
            "https://example.com/article",
            "Test Article",
            "Article content here",
        );
        assert_eq!(article.status, ArticleStatus::Pending);
        assert!(article.summary.is_none());
    }

    #[test]
    fn test_article_summarization() {
        let mut article = Article::new(
            "https://example.com/article",
            "Test Article",
            "Article content here",
        );
        article.set_summary("This is a summary");
        assert_eq!(article.status, ArticleStatus::Summarized);
        assert_eq!(article.summary.as_deref(), Some("This is a summary"));
    }
}
