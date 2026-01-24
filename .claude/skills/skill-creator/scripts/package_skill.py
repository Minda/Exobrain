#!/usr/bin/env python3
"""
Package and validate a Claude Code skill for distribution.

Usage:
    python package_skill.py <skill-path> [--output <output-dir>]

Example:
    python package_skill.py .claude/skills/my-skill
    python package_skill.py .claude/skills/my-skill --output dist/
"""

import argparse
import sys
import re
import zipfile
from pathlib import Path
from typing import List, Tuple, Optional


class SkillValidator:
    """Validates skill structure and content."""

    REQUIRED_FRONTMATTER = ['name', 'description']
    MAX_NAME_LENGTH = 64
    MAX_DESCRIPTION_LENGTH = 1024
    MAX_SKILL_SIZE = 500  # lines

    def __init__(self, skill_path: Path):
        self.skill_path = skill_path
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate(self) -> bool:
        """Run all validations. Returns True if valid."""
        self.errors = []
        self.warnings = []

        # Check basic structure
        if not self.skill_path.exists():
            self.errors.append(f"Skill path does not exist: {self.skill_path}")
            return False

        if not self.skill_path.is_dir():
            self.errors.append(f"Skill path is not a directory: {self.skill_path}")
            return False

        # Check for SKILL.md
        skill_file = self.skill_path / "SKILL.md"
        if not skill_file.exists():
            self.errors.append("SKILL.md not found")
            return False

        # Validate SKILL.md content
        self._validate_skill_md(skill_file)

        # Validate directory structure
        self._validate_structure()

        # Check file sizes
        self._validate_file_sizes()

        return len(self.errors) == 0

    def _validate_skill_md(self, skill_file: Path):
        """Validate SKILL.md content and frontmatter."""
        try:
            content = skill_file.read_text()
        except Exception as e:
            self.errors.append(f"Cannot read SKILL.md: {e}")
            return

        # Check for frontmatter
        if not content.startswith('---'):
            self.errors.append("SKILL.md missing YAML frontmatter")
            return

        # Extract frontmatter
        parts = content.split('---', 2)
        if len(parts) < 3:
            self.errors.append("SKILL.md has malformed frontmatter")
            return

        frontmatter = parts[1].strip()
        body = parts[2].strip()

        # Parse frontmatter
        self._validate_frontmatter(frontmatter)

        # Validate body
        self._validate_body(body)

    def _validate_frontmatter(self, frontmatter: str):
        """Validate frontmatter fields."""
        # Parse frontmatter (simple YAML parsing)
        fields = {}
        for line in frontmatter.split('\n'):
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                fields[key.strip()] = value.strip()

        # Check required fields
        for field in self.REQUIRED_FRONTMATTER:
            if field not in fields:
                self.errors.append(f"Missing required frontmatter field: {field}")
            elif not fields[field]:
                self.errors.append(f"Empty required frontmatter field: {field}")

        # Validate name
        if 'name' in fields:
            name = fields['name'].strip('"\'')
            if len(name) > self.MAX_NAME_LENGTH:
                self.errors.append(f"Name too long (max {self.MAX_NAME_LENGTH} chars): {len(name)} chars")

            if not name.islower():
                self.errors.append(f"Name must be lowercase: {name}")

            if not all(c.isalnum() or c == '-' for c in name):
                self.errors.append(f"Name can only contain lowercase letters, numbers, and hyphens: {name}")

            if name.startswith('anthropic-') or name.startswith('claude-'):
                self.errors.append(f"Name cannot start with 'anthropic-' or 'claude-': {name}")

            if any(word in name for word in ['helper', 'utils', 'tools']):
                self.warnings.append(f"Consider using a more specific name instead of generic terms: {name}")

        # Validate description
        if 'description' in fields:
            desc = fields['description'].strip('"\'')
            if len(desc) > self.MAX_DESCRIPTION_LENGTH:
                self.errors.append(f"Description too long (max {self.MAX_DESCRIPTION_LENGTH} chars): {len(desc)} chars")

            if len(desc) < 20:
                self.warnings.append(f"Description is very short ({len(desc)} chars). Consider adding more detail about when to use this skill.")

            # Check for trigger keywords
            generic_words = ['helpful', 'useful', 'assists', 'helps']
            if any(word in desc.lower() for word in generic_words):
                self.warnings.append("Description contains generic words. Consider adding specific trigger keywords.")

    def _validate_body(self, body: str):
        """Validate SKILL.md body content."""
        lines = body.split('\n')

        # Check length
        if len(lines) > self.MAX_SKILL_SIZE:
            self.warnings.append(f"SKILL.md is long ({len(lines)} lines). Consider moving content to references/ (recommended max: {self.MAX_SKILL_SIZE} lines)")

        # Check for XML tags (anti-pattern)
        if re.search(r'<[a-zA-Z][^>]*>', body):
            xml_tags = re.findall(r'<([a-zA-Z][^>]*)>', body)
            if xml_tags:
                self.warnings.append(f"Found XML-like tags in body (use markdown instead): {', '.join(set(xml_tags))}")

        # Check for Windows paths
        if re.search(r'[A-Z]:\\|\\\\', body):
            self.warnings.append("Found Windows-style paths. Use forward slashes for cross-platform compatibility.")

        # Check for time-sensitive language
        time_patterns = ['in 2024', 'in 2025', 'currently', 'right now', 'today']
        for pattern in time_patterns:
            if pattern in body.lower():
                self.warnings.append(f"Found time-sensitive language: '{pattern}'. Consider using 'historical pattern:' or similar.")
                break

    def _validate_structure(self):
        """Validate directory structure."""
        # Check for common directories
        dirs_to_check = ['scripts', 'references', 'examples']
        found_dirs = []

        for dir_name in dirs_to_check:
            dir_path = self.skill_path / dir_name
            if dir_path.exists() and dir_path.is_dir():
                found_dirs.append(dir_name)

                # Check for nested directories (anti-pattern)
                subdirs = [d for d in dir_path.iterdir() if d.is_dir()]
                if subdirs:
                    self.warnings.append(f"Found nested directories in {dir_name}/. Keep references flat (one level max).")

        # Check scripts are executable
        scripts_dir = self.skill_path / "scripts"
        if scripts_dir.exists():
            for script in scripts_dir.glob("*.py"):
                if not script.stat().st_mode & 0o111:
                    self.warnings.append(f"Script is not executable: {script.name}")

            for script in scripts_dir.glob("*.sh"):
                if not script.stat().st_mode & 0o111:
                    self.warnings.append(f"Script is not executable: {script.name}")

    def _validate_file_sizes(self):
        """Check for overly large files."""
        max_file_size = 1024 * 1024  # 1MB

        for file_path in self.skill_path.rglob("*"):
            if file_path.is_file():
                size = file_path.stat().st_size
                if size > max_file_size:
                    self.warnings.append(f"Large file detected ({size // 1024}KB): {file_path.relative_to(self.skill_path)}")

    def print_results(self):
        """Print validation results."""
        if self.errors:
            print("\n❌ Errors:")
            for error in self.errors:
                print(f"   • {error}")

        if self.warnings:
            print("\n⚠️  Warnings:")
            for warning in self.warnings:
                print(f"   • {warning}")

        if not self.errors and not self.warnings:
            print("\n✓ No issues found")


def package_skill(skill_path: Path, output_dir: Optional[Path] = None) -> Optional[Path]:
    """Package a skill into a zip file."""

    # Validate first
    validator = SkillValidator(skill_path)
    is_valid = validator.validate()

    validator.print_results()

    if not is_valid:
        print("\n❌ Skill validation failed. Fix errors before packaging.", file=sys.stderr)
        return None

    # Determine output path
    if output_dir is None:
        output_dir = skill_path.parent

    output_dir.mkdir(parents=True, exist_ok=True)

    skill_name = skill_path.name
    zip_path = output_dir / f"{skill_name}.zip"

    try:
        # Create zip file
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add all files in skill directory
            for file_path in skill_path.rglob("*"):
                if file_path.is_file():
                    # Skip hidden files and __pycache__
                    if file_path.name.startswith('.') or '__pycache__' in file_path.parts:
                        continue

                    arcname = file_path.relative_to(skill_path.parent)
                    zipf.write(file_path, arcname)

        print(f"\n✓ Packaged skill: {zip_path}")
        print(f"   Size: {zip_path.stat().st_size // 1024}KB")

        return zip_path

    except Exception as e:
        print(f"\n❌ Error packaging skill: {e}", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Package and validate a Claude Code skill",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python package_skill.py .claude/skills/my-skill
  python package_skill.py .claude/skills/my-skill --output dist/
  python package_skill.py .claude/skills/my-skill --validate-only
        """
    )

    parser.add_argument(
        "skill_path",
        type=Path,
        help="Path to the skill directory"
    )

    parser.add_argument(
        "--output",
        type=Path,
        help="Output directory for the zip file (default: same as skill parent)"
    )

    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate, don't create zip file"
    )

    args = parser.parse_args()

    if args.validate_only:
        # Just validate
        validator = SkillValidator(args.skill_path)
        is_valid = validator.validate()
        validator.print_results()
        sys.exit(0 if is_valid else 1)
    else:
        # Validate and package
        zip_path = package_skill(args.skill_path, args.output)
        sys.exit(0 if zip_path else 1)


if __name__ == "__main__":
    main()
