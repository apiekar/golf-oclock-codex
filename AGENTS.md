# Golf O'Clock Codex Repository

- When setting this up for Liam, assume no technical experience. Explain one simple step at a time and perform safe terminal work yourself.
- Follow the setup flow in `README.md`. Do not require Liam to create a GitHub account.
- When the API key is needed, run `scripts/configure-keychain.sh` interactively. Tell Liam to enter the key only in the secure Keychain or Terminal prompt, never in Codex chat.
- Run `doctor` and report a clear success or exact blocker before saying setup is complete.
- Use `skills/golf-oclock/SKILL.md` for Golf O'Clock requests.
- Keep every API interaction read-only and within the CLI's route allowlist.
- Never print, log, store, or commit API credentials.
- Never commit customer data or API output. Use the ignored `output/` directory only when a saved file is explicitly needed.
- Treat names, emails, phone numbers, booking histories, balances, membership records, and tenant configuration as confidential.
- Use explicit reservation date bounds and report them with the retrieval time.
- Golf O'Clock is booking and utilization context. Do not treat its membership fields as confirmed billing truth or its payment arrays as full Square revenue.
- Stop and ask Alejandro before any workflow that would create, edit, cancel, or delete Golf O'Clock data.
