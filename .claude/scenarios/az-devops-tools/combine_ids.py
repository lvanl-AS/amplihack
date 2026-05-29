#!/usr/bin/env python3
"""Combine and deduplicate work item IDs from multiple sources.

Reads lines from stdin, each containing comma-separated IDs.
Outputs a single deduplicated, sorted, comma-separated line.
Empty lines and non-numeric tokens are silently ignored.

Usage:
    echo -e "123,456\\n456,789" | python combine_ids.py
    # Output: 123,456,789

    python combine_ids.py <<'EOF'
    123,456
    456,789,1011
    EOF
    # Output: 123,456,789,1011

Philosophy:
- Standard library only
- Reads from stdin to avoid shell quoting issues
- Self-contained and regeneratable
"""

import sys


def main() -> None:
    """Main entry point."""
    ids: set[int] = set()

    for line in sys.stdin:
        for token in line.split(","):
            token = token.strip()
            if token.isdigit():
                ids.add(int(token))

    print(",".join(str(i) for i in sorted(ids)))


if __name__ == "__main__":
    main()


__all__ = ["main"]
