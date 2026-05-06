#!/usr/bin/env python3
"""Script to generate README.md from template and data.

This script reads the README_template.md and populates it with
data from data.py to produce the final README.md in the project root.
"""

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Ensure the src directory is in the path
sys.path.insert(0, str(Path(__file__).parent))

from data import PROVIDERS  # noqa: E402


TEMPLATE_PATH = Path(__file__).parent / "README_template.md"
OUTPUT_PATH = Path(__file__).parent.parent / "README.md"


def format_bool(value: bool) -> str:
    """Format a boolean value as a checkmark or cross."""
    return "✅" if value else "❌"


def format_optional(value, formatter=None):
    """Format an optional value, returning '-' if None."""
    if value is None:
        return "-"
    if formatter:
        return formatter(value)
    return str(value)


def build_provider_table(providers: list) -> str:
    """Build a markdown table from a list of provider dictionaries."""
    headers = [
        "Provider",
        "Models",
        "Free Tier",
        "Requires CC",
        "Rate Limits",
        "Notes",
    ]

    rows = []
    for provider in providers:
        name = provider.get("name", "Unknown")
        url = provider.get("url", "")
        models = provider.get("models", "-")
        free_tier = format_bool(provider.get("free_tier", False))
        requires_cc = format_bool(provider.get("requires_credit_card", False))
        rate_limits = format_optional(provider.get("rate_limits"))
        notes = format_optional(provider.get("notes"))

        if url:
            name_cell = f"[{name}]({url})"
        else:
            name_cell = name

        if isinstance(models, list):
            models_cell = ", ".join(models)
        else:
            models_cell = str(models)

        rows.append(
            f"| {name_cell} | {models_cell} | {free_tier} | {requires_cc} | {rate_limits} | {notes} |"
        )

    header_row = "| " + " | ".join(headers) + " |"
    separator_row = "| " + " | ".join(["---"] * len(headers)) + " |"

    return "\n".join([header_row, separator_row] + rows)


def generate_readme() -> str:
    """Generate the README content from template and data."""
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(f"Template not found: {TEMPLATE_PATH}")

    template = TEMPLATE_PATH.read_text(encoding="utf-8")

    # Build provider table
    provider_table = build_provider_table(PROVIDERS)

    # Get current timestamp in UTC
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    # Replace placeholders in template
    content = template.replace("{{ PROVIDER_TABLE }}", provider_table)
    content = content.replace("{{ LAST_UPDATED }}", timestamp)
    content = content.replace("{{ PROVIDER_COUNT }}", str(len(PROVIDERS)))

    return content


def main():
    """Main entry point for README generation."""
    print(f"Reading template from: {TEMPLATE_PATH}")
    print(f"Loading {len(PROVIDERS)} providers from data.py")

    try:
        readme_content = generate_readme()
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error during generation: {e}", file=sys.stderr)
        sys.exit(1)

    OUTPUT_PATH.write_text(readme_content, encoding="utf-8")
    print(f"README.md written to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
