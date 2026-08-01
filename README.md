# Golf O'Clock for Codex

Private, read-only access to The Tips Golf O'Clock API for Liam's Codex. It includes a small Python CLI and an installable Codex skill. No credentials or customer records belong in this repository.

## What it can do

- Search reservations in an explicit date range
- Look up a customer by exact email, phone, or Golf O'Clock ID
- Read one customer's reservation history
- Read one customer's account balance
- Read export-safe tenant configuration

It cannot create, change, cancel, or delete anything in Golf O'Clock.

## Install on Liam's Mac

Requirements: macOS, Git, Python 3, Codex, and a Golf O'Clock API key issued for Liam.

```bash
git clone https://github.com/apiekar/golf-oclock-codex.git
cd golf-oclock-codex
./scripts/install-codex-skill.sh
./scripts/configure-keychain.sh
```

The Keychain command prompts for the API key without putting it in shell history. Start a fresh Codex session after installing the skill.

Verify the connection:

```bash
python3 skills/golf-oclock/scripts/golfoclock.py doctor
```

Then ask Codex, for example:

```text
Use $golf-oclock to show me confirmed reservations for August 1, 2026.
```

## Direct CLI examples

```bash
python3 skills/golf-oclock/scripts/golfoclock.py reservations \
  --start 2026-08-01 --end 2026-08-01 --status confirmed

python3 skills/golf-oclock/scripts/golfoclock.py user \
  --email person@example.com
```

Use `--output output/descriptive-name.json` when a file is needed. The repository ignores `output/`, and the CLI writes files with owner-only permissions.

## Credentials

The CLI checks, in order:

1. `GOLFOCLOCK_API_KEY` in the current process
2. macOS Keychain service `the-tips-golf-oclock-api`, account `codex`

Use the Keychain setup script for normal operation. Do not create a `.env` file, paste the key into Codex chat, or commit API output.

## Test

```bash
python3 -m unittest discover -s tests -v
python3 /Users/layla/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/golf-oclock
```

The second command is optional on Liam's Mac because its path is Alejandro's local Codex validator.
