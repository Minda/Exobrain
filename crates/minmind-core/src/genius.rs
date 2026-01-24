//! Genius - AI agents that can be consulted

use serde::{Deserialize, Serialize};
use uuid::Uuid;

/// The AI provider for a Genius
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Provider {
    Anthropic,
    OpenAI,
    Ollama,
    Custom,
}

impl std::fmt::Display for Provider {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Provider::Anthropic => write!(f, "anthropic"),
            Provider::OpenAI => write!(f, "openai"),
            Provider::Ollama => write!(f, "ollama"),
            Provider::Custom => write!(f, "custom"),
        }
    }
}

impl std::str::FromStr for Provider {
    type Err = String;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.to_lowercase().as_str() {
            "anthropic" => Ok(Provider::Anthropic),
            "openai" => Ok(Provider::OpenAI),
            "ollama" => Ok(Provider::Ollama),
            "custom" => Ok(Provider::Custom),
            _ => Err(format!("Unknown provider: {}", s)),
        }
    }
}

/// A Genius is an AI agent that can be consulted for help.
/// Geniuses live in the "basement" of the Mind Palace.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Genius {
    pub id: Uuid,
    pub name: String,
    pub provider: Provider,
    pub model: String,
    pub system_prompt: Option<String>,
    pub config: serde_json::Value,
}

impl Genius {
    /// Create a new Genius with the given name, provider, and model
    pub fn new(name: impl Into<String>, provider: Provider, model: impl Into<String>) -> Self {
        Self {
            id: Uuid::new_v4(),
            name: name.into(),
            provider,
            model: model.into(),
            system_prompt: None,
            config: serde_json::json!({}),
        }
    }

    /// Set the system prompt for this Genius
    pub fn with_system_prompt(mut self, prompt: impl Into<String>) -> Self {
        self.system_prompt = Some(prompt.into());
        self
    }

    /// Set additional configuration for this Genius
    pub fn with_config(mut self, config: serde_json::Value) -> Self {
        self.config = config;
        self
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_new_genius() {
        let genius = Genius::new("Claude", Provider::Anthropic, "claude-3-opus-20240229");
        assert_eq!(genius.name, "Claude");
        assert_eq!(genius.provider, Provider::Anthropic);
        assert_eq!(genius.model, "claude-3-opus-20240229");
    }

    #[test]
    fn test_genius_with_system_prompt() {
        let genius = Genius::new("Helper", Provider::OpenAI, "gpt-4")
            .with_system_prompt("You are a helpful assistant.");
        
        assert_eq!(
            genius.system_prompt.as_deref(),
            Some("You are a helpful assistant.")
        );
    }
}
