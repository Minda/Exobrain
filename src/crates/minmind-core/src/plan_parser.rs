//! PlanParser - Extract user actions from plan markdown files
//!
//! Parses markdown files for `[USER]` markers and extracts them as UserActions.
//! Supports various marker states: `[USER]`, `[USER:wip]`, `[USER:done]`, `[USER:skip]`

use std::path::Path;

use crate::{ActionStatus, UserAction};

/// A parsed user action from a markdown file
#[derive(Debug, Clone)]
pub struct ParsedAction {
    /// The action title (text after the marker)
    pub title: String,
    /// The line number in the source file (1-based)
    pub line_number: u32,
    /// The parsed status from the marker
    pub status: ActionStatus,
}

/// Result of parsing a plan file
#[derive(Debug)]
pub struct ParseResult {
    /// The source file path
    pub source_file: String,
    /// All parsed actions from the file
    pub actions: Vec<ParsedAction>,
}

impl ParseResult {
    /// Convert parsed actions to UserAction entities
    pub fn into_user_actions(self) -> Vec<UserAction> {
        self.actions
            .into_iter()
            .map(|parsed| {
                let mut action = UserAction::from_plan(
                    parsed.title,
                    self.source_file.clone(),
                    parsed.line_number,
                );
                action.status = parsed.status;
                action
            })
            .collect()
    }
}

/// Parse a markdown string for [USER] markers
///
/// Supported markers:
/// - `- [USER]` or `- [USER] ` - Pending action
/// - `- [USER:wip]` - In progress
/// - `- [USER:done]` - Completed
/// - `- [USER:skip]` - Skipped
///
/// # Examples
///
/// ```
/// use minmind_core::parse_plan_content;
///
/// let content = r#"
/// ## Steps
/// - [ ] AI does this
/// - [USER] Configure API keys
/// - [USER:done] Review the design
/// "#;
///
/// let result = parse_plan_content(content, "plans/test.md");
/// assert_eq!(result.actions.len(), 2);
/// ```
pub fn parse_plan_content(content: &str, source_file: impl Into<String>) -> ParseResult {
    let source_file = source_file.into();
    let mut actions = Vec::new();

    for (idx, line) in content.lines().enumerate() {
        let line_number = (idx + 1) as u32;
        let trimmed = line.trim();

        // Match various [USER] patterns
        if let Some(action) = parse_user_marker(trimmed, line_number) {
            actions.push(action);
        }
    }

    ParseResult {
        source_file,
        actions,
    }
}

/// Parse a single line for a [USER] marker
fn parse_user_marker(line: &str, line_number: u32) -> Option<ParsedAction> {
    // Pattern: starts with "- [USER" (possibly after whitespace)
    let line = line.trim_start_matches(|c: char| c == '-' || c.is_whitespace());
    
    if !line.starts_with("[USER") {
        return None;
    }

    // Find the closing bracket
    let close_bracket = line.find(']')?;
    let marker = &line[..=close_bracket];
    let title = line[close_bracket + 1..].trim().to_string();

    if title.is_empty() {
        return None;
    }

    let status = match marker.to_lowercase().as_str() {
        "[user]" => ActionStatus::Pending,
        "[user:wip]" | "[user:inprogress]" | "[user:in_progress]" => ActionStatus::InProgress,
        "[user:done]" | "[user:completed]" => ActionStatus::Completed,
        "[user:skip]" | "[user:skipped]" => ActionStatus::Skipped,
        _ => ActionStatus::Pending,
    };

    Some(ParsedAction {
        title,
        line_number,
        status,
    })
}

/// Parse a plan file from the filesystem
///
/// # Errors
///
/// Returns an error if the file cannot be read.
pub fn parse_plan_file(path: impl AsRef<Path>) -> std::io::Result<ParseResult> {
    let path = path.as_ref();
    let content = std::fs::read_to_string(path)?;
    let source_file = path.to_string_lossy().to_string();
    Ok(parse_plan_content(&content, source_file))
}

/// Update a plan file's markers based on action statuses
///
/// Given a map of (line_number -> new_status), updates the markers in the file content.
pub fn update_plan_markers(
    content: &str,
    updates: &[(u32, ActionStatus)],
) -> String {
    let updates_map: std::collections::HashMap<u32, ActionStatus> = 
        updates.iter().cloned().collect();
    
    content
        .lines()
        .enumerate()
        .map(|(idx, line)| {
            let line_number = (idx + 1) as u32;
            if let Some(&new_status) = updates_map.get(&line_number) {
                update_line_marker(line, new_status)
            } else {
                line.to_string()
            }
        })
        .collect::<Vec<_>>()
        .join("\n")
}

/// Update a single line's [USER] marker to a new status
fn update_line_marker(line: &str, new_status: ActionStatus) -> String {
    let new_marker = match new_status {
        ActionStatus::Pending => "[USER]",
        ActionStatus::InProgress => "[USER:wip]",
        ActionStatus::Completed => "[USER:done]",
        ActionStatus::Skipped => "[USER:skip]",
    };

    // Find and replace the [USER...] pattern
    if let Some(start) = line.find("[USER") {
        if let Some(end) = line[start..].find(']') {
            let before = &line[..start];
            let after = &line[start + end + 1..];
            return format!("{}{}{}", before, new_marker, after);
        }
    }

    line.to_string()
}

/// Scan a directory for plan files and parse them all
///
/// Looks for `*.md` files in the given directory.
pub fn scan_plans_directory(dir: impl AsRef<Path>) -> std::io::Result<Vec<ParseResult>> {
    let dir = dir.as_ref();
    let mut results = Vec::new();

    if !dir.is_dir() {
        return Ok(results);
    }

    for entry in std::fs::read_dir(dir)? {
        let entry = entry?;
        let path = entry.path();
        
        if path.is_file() && path.extension().map_or(false, |ext| ext == "md") {
            match parse_plan_file(&path) {
                Ok(result) if !result.actions.is_empty() => {
                    results.push(result);
                }
                Ok(_) => {} // No actions, skip
                Err(e) => {
                    eprintln!("Warning: Failed to parse {}: {}", path.display(), e);
                }
            }
        }
    }

    Ok(results)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_user_marker() {
        let cases = vec![
            ("- [USER] Configure API keys", Some((ActionStatus::Pending, "Configure API keys"))),
            ("- [USER:wip] Working on it", Some((ActionStatus::InProgress, "Working on it"))),
            ("- [USER:done] Completed task", Some((ActionStatus::Completed, "Completed task"))),
            ("- [USER:skip] Not needed", Some((ActionStatus::Skipped, "Not needed"))),
            ("- [ ] Regular checkbox", None),
            ("- [x] Checked item", None),
            ("Some regular text", None),
            ("  - [USER] Indented action", Some((ActionStatus::Pending, "Indented action"))),
        ];

        for (line, expected) in cases {
            let result = parse_user_marker(line, 1);
            match expected {
                Some((status, title)) => {
                    let parsed = result.expect(&format!("Expected to parse: {}", line));
                    assert_eq!(parsed.status, status, "Status mismatch for: {}", line);
                    assert_eq!(parsed.title, title, "Title mismatch for: {}", line);
                }
                None => {
                    assert!(result.is_none(), "Should not parse: {}", line);
                }
            }
        }
    }

    #[test]
    fn test_parse_plan_content() {
        let content = r#"# Plan 001

## Overview
Some description

## Implementation Steps
- [ ] AI does this
- [USER] Configure API keys
- [ ] More AI work
- [USER:done] Review the design
- [USER] Approve deployment
"#;

        let result = parse_plan_content(content, "plans/001-test.md");
        assert_eq!(result.source_file, "plans/001-test.md");
        assert_eq!(result.actions.len(), 3);

        assert_eq!(result.actions[0].title, "Configure API keys");
        assert_eq!(result.actions[0].status, ActionStatus::Pending);
        assert_eq!(result.actions[0].line_number, 8);

        assert_eq!(result.actions[1].title, "Review the design");
        assert_eq!(result.actions[1].status, ActionStatus::Completed);

        assert_eq!(result.actions[2].title, "Approve deployment");
        assert_eq!(result.actions[2].status, ActionStatus::Pending);
    }

    #[test]
    fn test_update_plan_markers() {
        let content = r#"- [USER] Task one
- [USER] Task two
- [USER:wip] Task three"#;

        let updates = vec![
            (1, ActionStatus::Completed),
            (3, ActionStatus::Skipped),
        ];

        let updated = update_plan_markers(content, &updates);
        
        assert!(updated.contains("[USER:done] Task one"));
        assert!(updated.contains("[USER] Task two")); // Unchanged
        assert!(updated.contains("[USER:skip] Task three"));
    }

    #[test]
    fn test_into_user_actions() {
        let content = "- [USER] Test action";
        let result = parse_plan_content(content, "test.md");
        let actions = result.into_user_actions();
        
        assert_eq!(actions.len(), 1);
        assert_eq!(actions[0].title, "Test action");
        assert_eq!(actions[0].source_file.as_deref(), Some("test.md"));
        assert_eq!(actions[0].line_number, Some(1));
    }
}
