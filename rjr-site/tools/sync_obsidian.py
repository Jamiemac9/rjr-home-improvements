#!/usr/bin/env python3
"""Mirror the RJR handover docs into the Obsidian vault.

    python3 tools/sync_obsidian.py

Writes four notes into ~/Documents/Obsidian Vault/Web Dev Clients/RJR Home Improvements/
(override with OBSIDIAN_VAULT_PATH). Each note links back to the hub note. The project
copies are the master; the vault copies are overwritten. Does not touch the hub note
and does not commit anything: commit the vault yourself (only RJR files).
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VAULT = Path(os.environ.get("OBSIDIAN_VAULT_PATH", Path.home() / "Documents" / "Obsidian Vault"))
DEST = VAULT / "Web Dev Clients" / "RJR Home Improvements"
HUB = "RJR Home Improvements — Website Project"

DOCS = [
    ("handover/3-client-handover.md", "RJR — Client Handover", "What to send the client."),
    ("handover/1-case-study-changes.md", "RJR — Case Study Notes", "Source notes for the APX case study. Feed this to Hermes."),
    ("handover/2-marketing-content.md", "RJR — Marketing Content", "APX promo copy + RJR's ready-to-post content. Facts only; reviews verbatim."),
    ("DEPLOY.md", "RJR — Deploy & Launch Checklist", "Cursor setup, demo deploy, and go-live steps."),
    ("HANDOFF.md", "RJR — Handoff (start here)", "Full state, decisions and open items for picking the project up in a new chat."),
]


def main():
    if not VAULT.exists():
        sys.exit("Vault not found at %s (set OBSIDIAN_VAULT_PATH)" % VAULT)
    force = "--force" in sys.argv
    DEST.mkdir(parents=True, exist_ok=True)
    skipped = 0
    for src, title, purpose in DOCS:
        lines = (ROOT / src).read_text(encoding="utf-8").splitlines()
        if lines and lines[0].startswith("# "):
            lines = lines[1:]
        note = "# %s\n\n%s Hub: [[%s]]. Mirrors `rjr-site/%s` (the project copy is the master).\n\n%s\n" % (
            title, purpose, HUB, src, "\n".join(lines).strip())
        dest = DEST / (title + ".md")
        if (dest.exists() and not force and dest.read_text(encoding="utf-8") != note
                and dest.stat().st_mtime > (ROOT / src).stat().st_mtime):
            print("SKIPPED %s: edited in Obsidian after %s. Merge those edits into the project file, then re-run (or --force)." % (title, src))
            skipped += 1
            continue
        dest.write_text(note, encoding="utf-8")
        print("synced  %s" % title)
    if skipped:
        sys.exit(1)


if __name__ == "__main__":
    main()
