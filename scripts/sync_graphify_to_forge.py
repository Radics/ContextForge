#!/usr/bin/env python3
"""
Sync selected Graphify entries into ContextForge.

* Reads the Graphify graph JSON (default location: /opt/data/toolbox/graphify-out/graph.json).
* Looks for nodes whose label looks like a *fact* we care about – for now any label containing
  "key", "model", "ssh", or "env" (case‑insensitive).
* Converts those nodes into a ContextForge ``fact`` entry and appends it to ``journal/journal.log``.

The script is idempotent – it will not create duplicate facts for the same label/value pair.
"""
import json, pathlib, re, sys

GRAPHIFY_PATH = pathlib.Path("/opt/data/toolbox/graphify-out/graph.json")
FORGE_JOURNAL = pathlib.Path(__file__).resolve().parents[2] / "journal" / "journal.log"

def load_graph():
    if not GRAPHIFY_PATH.exists():
        print(f"Graphify file not found: {GRAPHIFY_PATH}", file=sys.stderr)
        sys.exit(1)
    with open(GRAPHIFY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def extract_facts(nodes):
    pat = re.compile(r"key|model|ssh|env", re.I)
    facts = []
    for node in nodes:
        label = node.get("label", "")
        if pat.search(label):
            facts.append({"type": "fact", "key": label.lower().replace(" ", "_"), "value": label})
    return facts

def load_existing():
    existing = []
    if FORGE_JOURNAL.exists():
        with open(FORGE_JOURNAL, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    existing.append(json.loads(line))
                except Exception:
                    continue
    return existing

def append_new(facts, existing):
    added = 0
    with open(FORGE_JOURNAL, "a", encoding="utf-8") as f:
        for fact in facts:
            if any(e.get("key") == fact["key"] and e.get("value") == fact["value"] for e in existing):
                continue
            f.write(json.dumps(fact, ensure_ascii=False) + "\n")
            added += 1
    return added

def main():
    data = load_graph()
    nodes = data.get("nodes", [])
    facts = extract_facts(nodes)
    if not facts:
        print("No candidate facts found in Graphify.")
        return
    existing = load_existing()
    added = append_new(facts, existing)
    print(f"Synced {added} new fact(s) from Graphify to ContextForge journal.")

if __name__ == "__main__":
    main()
