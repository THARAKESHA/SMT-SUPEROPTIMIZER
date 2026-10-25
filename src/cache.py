"""
cache.py -- Persistent Optimization Cache (Memoization).

Owner: Member 1 (Lead / Architecture)

Mimics production SMT superoptimizers (e.g. Souper's Redis cache)
by persisting formally proven optimizations across runs.
If a basic block has been optimized before, its proven-optimal replacement
is returned instantly (0.000s) without repeating candidate generation or Z3 queries.
"""

import json
import os
from typing import Optional, Dict
from .ir import BasicBlock
from .parser import parse_block

DEFAULT_CACHE_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "superoptimizer_cache.json"
)


class OptimizationCache:
    def __init__(self, cache_file: str = DEFAULT_CACHE_FILE, enabled: bool = True):
        self.cache_file = cache_file
        self.enabled = enabled
        self._entries: Dict[str, dict] = {}
        self.hits = 0
        self.misses = 0
        if self.enabled:
            self.load()

    def _block_key(self, block: BasicBlock) -> str:
        """Canonical key representing the block structure and free inputs."""
        inputs_str = ",".join(sorted(block.inputs))
        instrs_str = "; ".join(str(ins) for ins in block.instructions)
        return f"inputs:[{inputs_str}] | code:[{instrs_str}]"

    def get(self, block: BasicBlock) -> Optional[BasicBlock]:
        """Look up a block in the cache. Returns proven replacement BasicBlock or None."""
        if not self.enabled:
            return None
        key = self._block_key(block)
        if key in self._entries:
            self.hits += 1
            entry = self._entries[key]
            code = entry.get("best_code", "")
            return parse_block(code) if code else None
        self.misses += 1
        return None

    def put(self, block: BasicBlock, best: BasicBlock, orig_cost: int, best_cost: int, time_taken: float):
        """Save a newly proven optimization result into cache."""
        if not self.enabled:
            return
        key = self._block_key(block)
        self._entries[key] = {
            "original_code": str(block),
            "best_code": str(best),
            "original_cost": orig_cost,
            "best_cost": best_cost,
            "improved": (str(best) != str(block)),
            "synthesis_time": time_taken,
        }
        self.save()

    def load(self):
        """Load cache entries from JSON file."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    self._entries = json.load(f)
            except Exception:
                self._entries = {}

    def save(self):
        """Persist cache entries to JSON file."""
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self._entries, f, indent=2)
        except Exception:
            pass

    def clear(self):
        """Clear cache entries and remove cache file."""
        self._entries.clear()
        self.hits = 0
        self.misses = 0
        if os.path.exists(self.cache_file):
            try:
                os.remove(self.cache_file)
            except Exception:
                pass

    def size(self) -> int:
        return len(self._entries)
