---
name: golf-oclock
description: Read-only access to The Tips Golf O'Clock API for reservation searches, customer lookup, customer reservation history, account balances, and tenant configuration. Use when Codex is asked to inspect, export, summarize, or analyze The Tips Golf O'Clock booking data.
---

# Golf O'Clock

Use the bundled CLI for every API call. Keep all activity read-only.

## Workflow

1. Translate the request into one of the supported commands below. Do not call undocumented routes or invent endpoints.
2. Run `doctor` first if credentials have not been verified in the current session.
3. Make reservation date bounds explicit. The CLI requires both a start and end date.
4. Request only the records and fields needed for the task. Treat names, emails, phone numbers, bookings, and balances as confidential.
5. Report the source window and distinguish live API results from saved exports or assumptions.
6. Save output only when requested. Files containing customer data must stay in an ignored local output directory or another user-approved secure location.

Resolve the CLI path relative to this file:

```bash
python3 scripts/golfoclock.py doctor
```

## Commands

```bash
# Reservations in a bounded date range
python3 scripts/golfoclock.py reservations \
  --start 2026-08-01 --end 2026-08-07

# Exact customer lookup, using one identifier
python3 scripts/golfoclock.py user --email person@example.com
python3 scripts/golfoclock.py user --phone +13055550123
python3 scripts/golfoclock.py user --id user_abc123

# One customer's booking history
python3 scripts/golfoclock.py user-reservations \
  --user-id user_abc123 --include-past --include-canceled

# One account balance
python3 scripts/golfoclock.py balance \
  --user-id user_abc123 --account-id default --include-updates

# Tenant configuration
python3 scripts/golfoclock.py tenant
```

Use `--output output/descriptive-name.json` to write JSON with owner-only permissions. Prefer stdout for small, one-off queries.

## Guardrails

- Use only the five allowlisted POST routes implemented by the CLI. They are documented in [references/api.md](references/api.md).
- Do not create, edit, cancel, or reschedule reservations.
- Do not add or remove credits, memberships, users, or configuration.
- Never print, log, commit, or ask the user to paste an API key into chat.
- Never commit API results or customer data.
- Do not equate Golf O'Clock membership fields with confirmed billing status. Read [references/data-boundaries.md](references/data-boundaries.md) before answering membership, revenue, or payment questions.
- If a task requires a write operation, stop and ask for an approved operational workflow outside this skill.
