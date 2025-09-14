# scripts/print_tree.py
# Usage examples (PowerShell):
#   python scripts/print_tree.py
#   python scripts/print_tree.py --root . --max-depth 4 --out structure.txt
#   python scripts/print_tree.py --exclude ".venv,__pycache__,.pytest_cache,.git,.mypy_cache,.ruff_cache,dist,build,.vscode,.idea"

from __future__ import annotations
import argparse
import sys
from pathlib import Path

DEFAULT_EXCLUDES = {
    ".venv", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    ".git", ".tox", "dist", "build", ".vscode", ".idea"
}

def should_skip(path: Path, exclude: set[str]) -> bool:
    """Return True if any part of the path matches excluded names."""
    for part in path.parts:
        if part in exclude:
            return True
    return False

def iter_tree(root: Path, exclude: set[str], max_depth: int | None):
    """Yield (depth, path, is_last) tuples for a simple ASCII tree."""
    def walk(dir_path: Path, depth: int):
        if max_depth is not None and depth > max_depth:
            return
        try:
            entries = sorted(
                [p for p in dir_path.iterdir() if not should_skip(p, exclude)],
                key=lambda p: (p.is_file(), p.name.lower())
            )
        except PermissionError:
            return

        count = len(entries)
        for idx, p in enumerate(entries, start=1):
            is_last = idx == count
            yield (depth, p, is_last)
            if p.is_dir():
                yield from walk(p, depth + 1)

    yield (0, root, True)
    yield from walk(root, 1)

def draw_tree(root: Path, exclude: set[str], max_depth: int | None, ascii_only: bool) -> str:
    """Build the tree string with ASCII or simple pseudo-graphics."""
    V, T, L, H, S = ("│", "├", "└", "─", " ") if not ascii_only else ("|", "|", "`", "-", " ")
    lines: list[str] = []
    parents_last: list[bool] = []

    for depth, path, is_last in iter_tree(root, exclude, max_depth):
        if depth == 0:
            lines.append(path.resolve().name)
            continue

        # Build the prefix using info about previous levels' "lastness"
        prefix_chunks = []
        for is_parent_last in parents_last[:depth-1]:
            prefix_chunks.append(S + "   " if is_parent_last else V + "   ")

        branch = L if is_last else T
        prefix = "".join(prefix_chunks) + branch + H * 2 + " "
        name = path.name + ("/" if path.is_dir() else "")
        lines.append(prefix + name)

        # Update parents_last list for current depth
        if len(parents_last) < depth:
            parents_last.append(is_last)
        else:
            parents_last[depth-1] = is_last
            parents_last[depth:] = []

    return "\n".join(lines)

def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print a clean project tree (excludes virtual envs, caches, etc.)"
    )
    parser.add_argument("--root", default=".", help="Root directory (default: current dir).")
    parser.add_argument("--exclude", default=",".join(sorted(DEFAULT_EXCLUDES)),
                        help="Comma-separated names to exclude (directory or file names).")
    parser.add_argument("--max-depth", type=int, default=None,
                        help="Limit recursion depth (1 = only direct children).")
    parser.add_argument("--out", default=None, help="Save output to a file (UTF-8).")
    parser.add_argument("--ascii", action="store_true",
                        help="Force ASCII tree (useful for copy/paste).")
    return parser.parse_args(argv)

def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    root = Path(args.root).resolve()
    if not root.exists():
        print(f"Root not found: {root}", file=sys.stderr)
        return 2

    exclude = {item.strip() for item in args.exclude.split(",") if item.strip()}
    text = draw_tree(root, exclude, args.max_depth, ascii_only=args.ascii)

    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"Wrote tree to {args.out}")
    else:
        # Ensure UTF-8 in Windows terminals that support it
        try:
            sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        except Exception:
            pass
        print(text)

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
