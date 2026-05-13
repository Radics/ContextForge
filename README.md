# ContextForge

**ContextForge** is a lightweight framework that gives Large Language Model (LLM) agents **persistent memory** across sessions. It records every tool call, observation, and fact in a simple line‑based JSON journal so that a fresh agent can replay the history and continue where the last one left off.

---

## Why persistent memory?

LLM agents are stateless by design – each request starts with a fresh prompt. In production workflows this means you often have to repeat the same context (API keys, SSH fingerprints, model selections, etc.) or re‑run expensive steps. ContextForge solves that by:

* **Storing facts** (e.g., "SSH key is at /opt/data/home/.ssh/id_ed25519")
* **Logging tool output** so it can be examined later
* **Re‑playing the journal** on a brand‑new container, reproducing the exact state without manual re‑prompting
* **Version‑controlling the journal** – because it lives in a Git repository, the whole memory history can be diffed, branched, and shared.

---

## Core concepts

| Concept | Description |
|---------|-------------|
| **Journal** | A plain‑text file (`journal/journal.log`) where each line is a JSON object representing a single entry. |
| **Entry types** | `fact` (key/value pair), `observation` (raw tool output), `tool_output` (structured result), `note` (free‑form comment). |
| **Replay** | On start‑up a helper script reads the journal and reconstructs the in‑memory state for the new agent. |
| **Model agility** | Because the journal only stores data, you can switch LLM providers or model versions between runs without losing any remembered facts. |

---

## Quick start

```bash
# Clone the repo (already done in the session, but for new users)
git clone https://github.com/Radics/ContextForge.git
cd ContextForge

# Set up a virtual environment (optional but recommended)
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt   # currently empty – add deps as needed

# Initialise the journal file
mkdir -p journal && touch journal/journal.log
```

### Using the Python helper

```python
from context_forge import Journal

# Create / load the journal
j = Journal('journal/journal.log')

# Append a fact – for example, the path to your SSH key
j.append({
    'type': 'fact',
    'key': 'ssh_key',
    'value': '/opt/data/home/.ssh/id_ed25519'
})

# Later you can retrieve the latest value
print('SSH key location:', j.latest('ssh_key'))

# Store a tool output (e.g., result of `git status`)
import subprocess, json
out = subprocess.check_output(['git', 'status', '--porcelain']).decode()
j.append({
    'type': 'tool_output',
    'tool': 'git_status',
    'value': out.strip()
})
```

### Re‑playing on a fresh container

When a new Hermes / Claude / OpenAI agent boots, just run:

```python
from context_forge import Journal
j = Journal('journal/journal.log')
# Re‑hydrate any needed facts
ssh_key = j.latest('ssh_key')
print('Recovered SSH key path:', ssh_key)
```

All previously recorded facts, tool outputs and notes become instantly available.

---

## Model‑on‑the‑fly support

Because the journal never stores *model* objects—only raw data—it is **agnostic to the LLM backend**. You can:

1. Run a session with `gpt‑4‑turbo` and store the observations.
2. Shut down the container.
3. Start a new session with `claude‑sonnet‑3.5` (or any future model) and replay the same journal.
4. The new model sees the exact same context, eliminating the “I forgot my API key” problem.

---

## Testing & future work

* **Automated tests** – a CI pipeline should verify that a journal created by one run can be replayed without errors by a different model version.
* **Schema validation** – enforce a JSON schema for entries to catch malformed logs early.
* **CLI wrapper** – a tiny command‑line tool (`cforge`) to add facts, list entries, and clear the journal.
* **Integration with Hermes** – hook into the `session‑handoff` skill so that every Hermes run automatically writes to the journal.

Feel free to open issues or PRs to add the above features.

---

## License

MIT – see `LICENSE` (add your own license file if you wish).

---

### Acknowledgements

* The idea stems from the **persistent‑memory** experiments you performed earlier in this session (`ContextForge` vs. the earlier `ContextForge` attempt).
* Inspired by LangChain’s memory abstractions, AutoGPT’s scratchpad, and the OpenAI Assistants API.
* Built on top of the Hermes agent’s own journaling capabilities (`hermes‑hostinger‑deploy`, `session‑handoff`).
