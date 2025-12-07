import subprocess
from typing import List, Optional
from core.storage import Storage
from core.types import SearchResult

class Quicklinks:
    def __init__(self, storage: Optional[Storage] = None):
        self.storage = storage or Storage()

    def search(self, q: str, limit: int = 50) -> List[SearchResult]:
        results = []
        for link in self.storage.list_quicklinks(q=q, limit=limit):
            title = f"{link['name']} [{link['category']}]" if link["category"] else link["name"]
            subtitle = f"{link['target']} {link['args']}".strip()
            results.append(
                SearchResult(
                    title=title,
                    subtitle=subtitle,
                    action=lambda l=link: self.open_link(l),
                    group="quicklink",
                )
            )
        return results

    def open_link(self, link_row):
        kind = link_row["kind"]
        target = link_row["target"]
        args = link_row["args"] or ""
        if kind == "url":
            subprocess.Popen(["start", "", target], shell=True)
        elif kind == "folder":
            subprocess.Popen(["explorer", target])
        else:
            # command
            cmd = f"{target} {args}".strip()
            subprocess.Popen(cmd, shell=True)