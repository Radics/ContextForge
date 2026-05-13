# context_forge.py
"""
Simple persistent journal for LLM agents.
Each line in the log file is a JSON object.
Supported entry types: fact, observation, tool_output, note
"""
import json
import os
from typing import Any, Dict, List, Optional

class Journal:
    def __init__(self, path: str):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        # ensure file exists
        open(self.path, 'a').close()

    def _load(self) -> List[Dict[str, Any]]:
        entries = []
        with open(self.path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    # ignore malformed lines
                    continue
        return entries

    def append(self, entry: Dict[str, Any]):
        """Append a JSON entry to the journal."""
        with open(self.path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def query(self, key: str, latest: bool = True) -> Optional[Any]:
        """Return the value(s) for a given entry key.
        If latest=True returns the most recent value, otherwise a list of all.
        """
        entries = self._load()
        matches = [e['value'] for e in entries if e.get('key') == key]
        if not matches:
            return None
        return matches[-1] if latest else matches

    def latest(self, key: str) -> Optional[Any]:
        return self.query(key, latest=True)

    def all(self, key: str) -> List[Any]:
        return self.query(key, latest=False) or []

# Convenience function for scripts
def add_fact(journal_path: str, key: str, value: Any):
    j = Journal(journal_path)
    j.append({'type': 'fact', 'key': key, 'value': value})

if __name__ == '__main__':
    # tiny demo when run directly
    import sys
    if len(sys.argv) != 4:
        print('Usage: python context_forge.py <journal_path> <key> <value>')
        sys.exit(1)
    _, p, k, v = sys.argv
    add_fact(p, k, v)
    print('Added fact', k, '=', v)
"""