# ContextForge

A lightweight framework for **persistent memory across LLM agent sessions**. It stores a journal of agent actions, facts, and tool outputs on disk so that subsequent interactions can retrieve and reuse that information without re‑prompting.

## Features
- **File‑based journal** (`journal/`) that is appended to after each agent step.
- **Session‑hand‑off** skill (`hermes‑hostinger‑deploy` style) that can replay the journal on a fresh container.
- **Git‑tracked** so the memory state lives in version control and can be shared.
- Simple Python helper (`context_forge.py`) to read, query, and append entries.

## Quick start
```bash
# clone (already done)
cd ContextForge
# install dependencies (none required for the core lib)
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt  # optional if you add extras

# initialize journal
touch journal/journal.log
```

## Usage (Python)
```python
from context_forge import Journal

j = Journal('journal/journal.log')
# Append a fact
j.append({'type':'fact','key':'ssh_key','value':'/opt/data/home/.ssh/id_ed25519'})
# Query latest fact
print(j.latest('ssh_key'))
```

See `context_forge.py` for the full API.
