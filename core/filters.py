import re
import toml
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class Filters:
    path_globs: List[str]
    extensions: List[str]
    regexes: Dict[str, str]
    store_embeddings_only: bool
    hash_raw_files: bool
    block_on_pii_score: float

    def compile_patterns(self) -> Dict[str, re.Pattern]:
        return {k: re.compile(v, re.I) for k, v in self.regexes.items()}


def load_filters(path: str) -> Filters:
    data = toml.load(path)
    return Filters(
        path_globs=data.get("exclude", {}).get("paths", {}).get("globs", []),
        extensions=data.get("exclude", {}).get("extensions", {}).get("list", []),
        regexes=data.get("exclude", {}).get("regex", {}),
        store_embeddings_only=data.get("policy", {}).get("store_embeddings_only", True),
        hash_raw_files=data.get("policy", {}).get("hash_raw_files", True),
        block_on_pii_score=float(data.get("policy", {}).get("block_on_pii_score", 0.8)),
    )
