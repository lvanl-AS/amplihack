#!/usr/bin/env python3
"""
Tool: fill_template.py

Purpose: Deterministic template filler. Takes an ADO work item template
         (from get_templates.py) and section content, produces properly
         filled HTML matching the template's structure.

Usage:
    # Fill from sections JSON
    python fill_template.py \
        --template-file /tmp/feat_template.json \
        --sections-file /tmp/sections.json \
        --output-dir /tmp/ado_filled/

    # List sections detected in a template
    python fill_template.py \
        --template-file /tmp/feat_template.json \
        --list-sections

sections.json format:
{
    "System.Description": {
        "what": "Problem statement here...",
        "why": "**Without** this... **With** this...",
        "guest_wins": "- Win one\\n- Win two",
        "_preserve": ["dor_reminders", "dod_reminders"]
    },
    "Microsoft.VSTS.Common.AcceptanceCriteria": {
        "outcome": "Business outcome...",
        "additional_context": "1. First criterion\\n2. Second",
        "_preserve": ["release_readiness"]
    }
}

Philosophy:
- Deterministic: same input always produces same output
- Template-driven: output follows the template's section order
- Agents draft content, this tool does HTML assembly
- Standard library + format_html for markdown→HTML
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from format_html import markdown_to_html


# ---------------------------------------------------------------------------
# Section parsing
# ---------------------------------------------------------------------------

@dataclass
class Section:
    key: str            # normalized key: "what", "guest_wins", etc.
    header_text: str    # cleaned header text: "WHAT", "Guest Wins"
    start: int          # position in original HTML
    end: int            # end position (next section start or len)
    original_html: str  # full original HTML for this section


def normalize_key(text: str) -> str:
    """Normalize bold header text to a section key.

    Examples:
        "WHAT" → "what"
        "Guest Wins" → "guest_wins"
        "Quality Measure AC&nbsp;" → "quality_measure_ac"
        "Release Readiness – Answer During Acceptance Demo" → "release_readiness"
    """
    # Strip HTML tags
    text = re.sub(r"<[^>]+>", "", text)
    # Replace HTML entities and unicode
    text = text.replace("&nbsp;", " ").replace("&amp;", "&")
    text = text.replace("\u00a0", " ")
    # Strip trailing punctuation
    text = text.strip().rstrip(":….,")
    # Truncate at long separators for readability
    for sep in [" – ", " — ", " - "]:
        if sep in text:
            text = text.split(sep)[0]
            break
    # Collapse whitespace, lowercase, underscores
    text = re.sub(r"\s+", "_", text.strip().lower())
    return text


def clean_header_text(text: str) -> str:
    """Extract clean display text from a bold header."""
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("&nbsp;", " ").replace("\u00a0", " ")
    text = text.strip().rstrip(":")
    return text


# Patterns for bold/strong headers at the start of block elements
_HEADER_PATTERN = re.compile(
    r"(<(?:div|p|td)[^>]*>"  # container open
    r"(?:\s|&nbsp;)*"  # optional whitespace/entities
    r"(?:<(?!b\b|strong\b)[^/>]+>\s*)*?"  # optional non-bold wrapper tags
    r"<(?:b|strong)[^>]*>)"  # bold/strong open (end of group 1 = header_start)
    r"(.*?)"  # header text (group 2)
    r"(</(?:b|strong)>)",  # bold/strong close (group 3)
    re.DOTALL | re.IGNORECASE,
)

# Keys to skip (not real section headers)
_SKIP_PREFIXES = ("by_providing", "invest")


def parse_sections(html: str) -> list[Section]:
    """Parse HTML into sections based on bold/strong headers."""
    raw = []
    for m in _HEADER_PATTERN.finditer(html):
        header_text = m.group(2)
        key = normalize_key(header_text)

        if not key or len(key) < 2:
            continue
        if any(key.startswith(p) for p in _SKIP_PREFIXES):
            continue
        # Skip if the "header" is just <br> or empty
        if key in ("br", ""):
            continue

        raw.append((key, clean_header_text(header_text), m.start()))

    if not raw:
        return []

    sections = []
    for i, (key, header_text, start) in enumerate(raw):
        end = raw[i + 1][2] if i + 1 < len(raw) else len(html)
        sections.append(
            Section(
                key=key,
                header_text=header_text,
                start=start,
                end=end,
                original_html=html[start:end],
            )
        )

    return sections


def list_sections(html: str) -> list[dict]:
    """List sections found in template HTML (for debugging/introspection)."""
    sections = parse_sections(html)
    result = []
    for s in sections:
        result.append(
            {
                "key": s.key,
                "header": s.header_text,
                "length": len(s.original_html),
            }
        )
    # Check for preamble
    if sections and sections[0].start > 0:
        preamble = html[: sections[0].start].strip()
        if preamble:
            result.insert(0, {"key": "preamble", "header": "(before first section)", "length": len(preamble)})
    return result


# ---------------------------------------------------------------------------
# Template filling
# ---------------------------------------------------------------------------

def _format_content(content: str) -> str:
    """Convert section content to HTML. Pass through if already HTML."""
    content = content.strip()
    if not content:
        return ""
    # If content starts with an HTML tag, assume it's already HTML
    if content.startswith("<"):
        return content
    # Otherwise convert from markdown
    return markdown_to_html(content)


def _build_section(header_text: str, content_html: str, is_description: bool = True) -> str:
    """Build a filled section's HTML.

    For Description fields (div/b style):
        <div><b>HEADER</b></div>
        <div>content...</div>
        <div><br></div>

    For AC fields (p/strong style):
        <p><strong>HEADER</strong></p>
        content...
    """
    if is_description:
        return f"<div><b>{header_text}</b></div>\n{content_html}\n<div><br></div>\n"
    else:
        return f"<p><strong>{header_text}</strong></p>\n{content_html}\n"


def fill_field(
    template_html: str,
    sections_content: dict[str, str],
    preserve_keys: set[str] | None = None,
    is_description: bool = True,
) -> str:
    """Fill a template field's HTML with section content.

    Args:
        template_html: Original template HTML for this field
        sections_content: {section_key: content_text} — markdown or HTML
        preserve_keys: section keys to copy verbatim from template
        is_description: True for Description fields (div/b), False for AC (p/strong)

    Returns:
        Filled HTML string
    """
    preserve_keys = preserve_keys or set()
    sections = parse_sections(template_html)

    if not sections:
        # No sections found — just format whatever content we have
        all_content = "\n\n".join(v for v in sections_content.values() if v and not v.startswith("_"))
        if all_content:
            return _format_content(all_content)
        return template_html

    parts = []

    # Handle preamble (content before first section, e.g. story connextra)
    preamble_html = template_html[: sections[0].start]
    if "preamble" in sections_content and sections_content["preamble"]:
        content = _format_content(sections_content["preamble"])
        parts.append(f"{content}\n<div><br></div>\n")
    elif preamble_html.strip():
        parts.append(preamble_html)

    for section in sections:
        if section.key in preserve_keys:
            # Keep original HTML verbatim
            parts.append(section.original_html)
        elif section.key in sections_content and sections_content[section.key]:
            # Fill with new content
            content_html = _format_content(sections_content[section.key])
            parts.append(_build_section(section.header_text, content_html, is_description))
        else:
            # Keep template placeholder
            parts.append(section.original_html)

    return "".join(parts)


def fill_template(
    template_fields: dict[str, str],
    sections_map: dict[str, dict[str, str]],
) -> dict[str, str]:
    """Fill multiple template fields with section content.

    Args:
        template_fields: {field_name: template_html} from get_templates.py
        sections_map: {field_name: {section_key: content}} — content to fill

    Returns:
        {field_name: filled_html} for fields that were filled
    """
    result = {}

    for field_name, sections_content in sections_map.items():
        template_html = template_fields.get(field_name, "")
        if not template_html and not sections_content:
            continue

        # Extract _preserve list if present
        preserve_keys = set(sections_content.pop("_preserve", []))
        # Remove internal keys starting with _
        clean_content = {k: v for k, v in sections_content.items() if not k.startswith("_")}

        is_desc = "description" in field_name.lower()

        if template_html:
            result[field_name] = fill_field(
                template_html, clean_content, preserve_keys, is_desc
            )
        else:
            # No template for this field — just format the content
            all_content = "\n\n".join(v for v in clean_content.values() if v)
            if all_content:
                result[field_name] = _format_content(all_content)

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fill ADO work item template with section content",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List sections in a template
  %(prog)s --template-file /tmp/template.json --list-sections

  # Fill template and write output files
  %(prog)s --template-file /tmp/template.json \\
           --sections-file /tmp/sections.json \\
           --output-dir /tmp/filled/

  # Fill and print to stdout (single field)
  %(prog)s --template-file /tmp/template.json \\
           --sections-file /tmp/sections.json \\
           --field System.Description
""",
    )

    parser.add_argument(
        "--template-file",
        required=True,
        help="JSON file with template fields (from get_templates.py --fields-only)",
    )
    parser.add_argument(
        "--sections-file",
        help='JSON file: {field_name: {section_key: content, "_preserve": [keys]}}',
    )
    parser.add_argument(
        "--list-sections",
        action="store_true",
        help="List detected sections in the template and exit",
    )
    parser.add_argument(
        "--field",
        help="Output only this field to stdout (instead of writing files)",
    )
    parser.add_argument(
        "--output-dir",
        help="Directory to write filled HTML files",
    )

    args = parser.parse_args()

    # Load template
    try:
        template_fields = json.loads(Path(args.template_file).read_text())
    except (OSError, json.JSONDecodeError) as e:
        print(f"Error loading template: {e}", file=sys.stderr)
        sys.exit(1)

    # List sections mode
    if args.list_sections:
        for field_name in ("System.Description", "Microsoft.VSTS.Common.AcceptanceCriteria"):
            html = template_fields.get(field_name, "")
            if html:
                sections = list_sections(html)
                print(f"\n{field_name}:")
                for s in sections:
                    print(f"  {s['key']:40s}  {s['header']}")
        return

    # Fill mode
    if not args.sections_file:
        print("Error: --sections-file required for fill mode", file=sys.stderr)
        sys.exit(1)

    try:
        sections_map = json.loads(Path(args.sections_file).read_text())
    except (OSError, json.JSONDecodeError) as e:
        print(f"Error loading sections: {e}", file=sys.stderr)
        sys.exit(1)

    filled = fill_template(template_fields, sections_map)

    if args.field:
        # Print single field to stdout
        if args.field in filled:
            print(filled[args.field])
        else:
            print(f"Field '{args.field}' not in output", file=sys.stderr)
            sys.exit(1)
    elif args.output_dir:
        # Write files
        out_dir = Path(args.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        field_to_filename = {
            "System.Description": "description.html",
            "Microsoft.VSTS.Common.AcceptanceCriteria": "ac.html",
        }

        for field_name, html in filled.items():
            filename = field_to_filename.get(field_name, f"{field_name}.html")
            out_path = out_dir / filename
            out_path.write_text(html)
            print(f"Wrote: {out_path}", file=sys.stderr)
    else:
        # Print all as JSON
        print(json.dumps(filled, indent=2))


if __name__ == "__main__":
    main()
