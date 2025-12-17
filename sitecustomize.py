"""
Lightweight runtime helpers to make the project work in headless CI environments.

- Ensures the bundled config.default.json is also available one level above the
  package directory, matching build/test expectations.
"""
from pathlib import Path


def _ensure_top_level_config():
    repo_root = Path(__file__).parent
    source = repo_root / "config.default.json"
    target = repo_root.parent / "config.default.json"
    if source.exists() and not target.exists():
        try:
            target.write_bytes(source.read_bytes())
        except Exception:
            pass


_ensure_top_level_config()

