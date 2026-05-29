#!/usr/bin/env python3
"""Extract parent work item IDs from child work item relations.

Reads a JSON array of work items from stdin (as output by
fetch_child_stories.py) and extracts parent IDs from
System.LinkTypes.Hierarchy-Reverse relations.

Usage:
    cat stories.json | python extract_parent_ids.py
    python extract_parent_ids.py <<'EOF'
    [{"id": 123, "relations": [{"rel": "System.LinkTypes.Hierarchy-Reverse", "url": ".../_apis/wit/workItems/99"}]}]
    EOF

Philosophy:
- Standard library only
- Reads from stdin to avoid shell quoting issues with large JSON
- Self-contained and regeneratable
"""

import json
import sys


def extract_parent_ids(work_items: list[dict]) -> list[int]:
    """Extract parent IDs from Hierarchy-Reverse relations.

    Args:
        work_items: List of work item dicts with relations

    Returns:
        Sorted list of unique parent work item IDs
    """
    parent_ids: set[int] = set()

    for item in work_items:
        for rel in item.get("relations") or []:
            if rel.get("rel") == "System.LinkTypes.Hierarchy-Reverse":
                url = rel.get("url", "")
                if url:
                    try:
                        parent_id = int(url.rstrip("/").split("/")[-1])
                        parent_ids.add(parent_id)
                    except ValueError:
                        pass

    return sorted(parent_ids)


def main() -> None:
    """Main entry point."""
    text = sys.stdin.read().strip()
    if not text:
        print("")
        return

    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        print("")
        return

    if not isinstance(data, list):
        data = [data]

    parent_ids = extract_parent_ids(data)
    print(",".join(str(pid) for pid in parent_ids))

    if parent_ids:
        print(
            f"Found {len(parent_ids)} parent work item(s)",
            file=sys.stderr,
        )
    else:
        print("No parent relations found", file=sys.stderr)


if __name__ == "__main__":
    main()


__all__ = ["extract_parent_ids", "main"]
