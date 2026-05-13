#!/usr/bin/env python3
"""cforge – tiny command‑line wrapper for ContextForge.

Supported sub‑commands:
  add-fact   KEY VALUE                – store a fact in the journal
  list-facts [KEY]                    – list all facts or those matching KEY
  sync-graphify                        – run the Graphify → ContextForge sync script
  rate-info                            – print the current adaptive rate‑limit delay

All commands operate on the journal located at ``journal/journal.log`` relative
to the repository root.
"""
import argparse
import sys
from pathlib import Path

# Import from the package (the repo root is in sys.path when executed from here)
from ContextForge import Journal, AdaptiveRateLimiter
from scripts.sync_graphify_to_forge import main as sync_main  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
JOURNAL_PATH = REPO_ROOT / "journal" / "journal.log"


def cmd_add_fact(args):
    j = Journal(str(JOURNAL_PATH))
    j.append({"type": "fact", "key": args.key, "value": args.value})
    print(f"Fact added: {args.key} = {args.value}")


def cmd_list_facts(args):
    j = Journal(str(JOURNAL_PATH))
    entries = j._load()
    facts = [e for e in entries if e.get('type') == 'fact']
    if args.key:
        facts = [f for f in facts if f.get('key') == args.key]
    for f in facts:
        print(f"{f.get('key')}: {f.get('value')}")
    if not facts:
        print("No matching facts found.")


def cmd_sync(args):
    # sync_graphify_to_forge.py contains a main() that does the work
    sync_main()


def cmd_rate_info(args):
    limiter = AdaptiveRateLimiter()
    print(f"Current base delay: {limiter.base_delay} ms")
    print(f"Effective delay after last header check: {limiter.current_delay:.3f}s")


def main():
    parser = argparse.ArgumentParser(prog='cforge')
    sub = parser.add_subparsers(dest='command')

    p_add = sub.add_parser('add-fact', help='Add a fact to the journal')
    p_add.add_argument('key')
    p_add.add_argument('value')
    p_add.set_defaults(func=cmd_add_fact)

    p_list = sub.add_parser('list-facts', help='List stored facts')
    p_list.add_argument('key', nargs='?')
    p_list.set_defaults(func=cmd_list_facts)

    p_sync = sub.add_parser('sync-graphify', help='Sync Graphify entries to the journal')
    p_sync.set_defaults(func=cmd_sync)

    p_rate = sub.add_parser('rate-info', help='Show adaptive rate‑limiter status')
    p_rate.set_defaults(func=cmd_rate_info)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    args.func(args)

if __name__ == '__main__':
    main()
