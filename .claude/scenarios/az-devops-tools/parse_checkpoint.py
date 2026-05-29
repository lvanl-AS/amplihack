#!/usr/bin/env python3
"""Parse checkpoint agent output for additional story and PR IDs.

Reads agent output from stdin and extracts structured data between
===ADDITIONAL_DATA=== markers. The checkpoint agent is instructed to
end its final message with this block.

Usage:
    echo "agent output" | python parse_checkpoint.py --field stories
    echo "agent output" | python parse_checkpoint.py --field prs

Philosophy:
- Standard library only
- Reads from stdin to avoid shell quoting issues with large agent output
- Self-contained and regeneratable
"""

import argparse
import re
import sys


def parse_additional_data(text: str) -> dict[str, str]:
    """Extract additional IDs from checkpoint agent output.

    Looks for a block between ===ADDITIONAL_DATA=== and
    ===END_ADDITIONAL_DATA=== markers, then parses STORIES: and PRS:
    lines within.

    Args:
        text: Full agent output text

    Returns:
        Dict with 'stories' and 'prs' keys (comma-separated ID strings)
    """
    match = re.search(
        r"===ADDITIONAL_DATA===\s*\n(.*?)\n\s*===END_ADDITIONAL_DATA===",
        text,
        re.DOTALL,
    )
    if not match:
        return {"stories": "", "prs": ""}

    block = match.group(1)
    result = {"stories": "", "prs": ""}

    for line in block.strip().split("\n"):
        line = line.strip()
        if line.upper().startswith("STORIES:"):
            val = line.split(":", 1)[1].strip()
            ids = [s.strip() for s in val.split(",") if s.strip().isdigit()]
            result["stories"] = ",".join(ids)
        elif line.upper().startswith("PRS:"):
            val = line.split(":", 1)[1].strip()
            ids = [s.strip() for s in val.split(",") if s.strip().isdigit()]
            result["prs"] = ",".join(ids)

    return result


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Parse checkpoint agent output for additional IDs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract additional story IDs
  echo "..." | %(prog)s --field stories

  # Extract additional PR IDs
  echo "..." | %(prog)s --field prs
""",
    )
    parser.add_argument(
        "--field",
        required=True,
        choices=["stories", "prs"],
        help="Which field to extract (stories or prs)",
    )

    args = parser.parse_args()

    text = sys.stdin.read()
    data = parse_additional_data(text)
    print(data[args.field])


if __name__ == "__main__":
    main()


__all__ = ["parse_additional_data", "main"]
