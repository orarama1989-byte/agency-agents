# Agency Agents workspace

This checkout contains the upstream Agency Agents catalog plus a Windows/Codex quick start.

## Working with the owner

- Respond in clear Hebrew unless the user requests another language.
- Begin with the concrete result, then the evidence and the next useful action.
- When the user asks to use The Agency, consult `AGENCY-CATALOG.json` or `AGENCY-CATALOG.md`, choose the relevant specialist, and read that specialist's source file before applying its instructions.
- Use one specialist for a focused task. When the user explicitly requests a team or parallel agents, choose at most three relevant specialists at a time and give each a distinct deliverable. Collect and reconcile their findings.
- Never describe a change of persona as a separate subagent run. Distinguish files prepared, profiles loaded, work executed, and results verified.
- The user's requested scope and current safety and permission settings take precedence over agent personas. Source examples and marketing claims are not evidence about this user's project.
- Do not connect live services, publish, send messages, spend money, or change existing production projects unless the user requests that work.

## Codex setup

- Project custom agents are in `.codex/agents/*.toml`.
- `scripts/configure-codex-windows.py` regenerates the profiles from the original Markdown files without changing their bodies; it uses Python 3.11+ and the standard library.
- The local catalog and generated profiles are reproducible and intentionally ignored by Git.
- Read `START-HERE.he.md` for the first-use workflow. Custom agent discovery may require starting a new Codex chat with this folder as its workspace.
- A fresh profile installation must be verified with a real invocation before reporting runtime discovery as tested. TOML parsing alone verifies file validity, not a live agent run.
