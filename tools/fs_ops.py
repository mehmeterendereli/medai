import hashlib
from pathlib import Path
from typing import Dict, Any, List


def filesystem_search(args: Dict[str, Any]) -> List[str]:
    root = Path(args.get("root", "."))
    pattern = args.get("glob", "**/*")
    contains = args.get("contains")
    limit = int(args.get("limit", 50))
    results: List[str] = []
    for p in root.glob(pattern):
        if p.is_file():
            if contains:
                try:
                    if contains.lower() not in p.read_text(errors="ignore").lower():
                        continue
                except Exception:
                    continue
            results.append(str(p))
            if len(results) >= limit:
                break
    return results


def filesystem_hash(args: Dict[str, Any]) -> str:
    path = Path(args.get("path"))
    algo = args.get("algo", "sha256")
    h = hashlib.new(algo)
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()
