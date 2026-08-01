# Liam: Start Here

This gives your Codex safe, read-only access to The Tips Golf O'Clock data. It can look up reservations and customer records, but it cannot create, change, cancel, or delete anything.

You do not need a GitHub account or technical experience.

## Give this message to Codex

Open Codex on your Mac and paste this entire message:

> Set up the Golf O'Clock integration from https://github.com/apiekar/golf-oclock-codex for me. I am not technical, so download it, install the included Codex skill, and guide me one simple step at a time. Do any safe setup work yourself instead of asking me to run commands. When an API key is needed, use the included macOS Keychain setup. Never ask me to paste the key into Codex chat, GitHub, email, or text. Test only read-only access and tell me clearly when setup is complete.

Codex should download this repository, install the skill, pause while you securely enter your API key, and verify the connection.

## When Codex asks for the API key

An API key is like a password. Do not paste it into Codex chat.

1. Sign into Golf O'Clock using your normal The Tips manager account.
2. Open [Golf O'Clock API Keys](https://thetipsgolf.golfoclock.com/manage/control-panel/integrations?providerId=apikeys).
3. Create a dedicated key named `Liam Codex`, if the page gives you that option.
4. Tell Codex you have the key, without showing it the key.
5. Codex will run the included Keychain setup. Paste the key only into the secure Keychain or Terminal password prompt that appears.

If Golf O'Clock does not let you create a key, stop there and tell Alejandro. Do not use someone else's key.

## After setup

You can ask Codex things like:

- "Use Golf O'Clock to show me today's confirmed reservations."
- "Find this customer in Golf O'Clock by email."
- "Show me this customer's reservation history."
- "Export next week's reservations."

Codex should always use explicit dates, protect customer information, and keep every request read-only.

## Safety

- This public repository contains code and instructions only. It contains no API key or customer data.
- The API key stays in macOS Keychain on Liam's Mac.
- Never paste the API key into Codex chat, GitHub, email, or text.
- Never commit exported customer or reservation data.
- The included CLI blocks routes outside its read-only allowlist. This is a client-side safety measure, not a confirmed Golf O'Clock server-side permission scope.

## Technical reference

Codex can perform these steps itself:

```bash
git clone https://github.com/apiekar/golf-oclock-codex.git
cd golf-oclock-codex
./scripts/install-codex-skill.sh
./scripts/configure-keychain.sh
python3 skills/golf-oclock/scripts/golfoclock.py doctor
```

Run the offline test suite with:

```bash
python3 -m unittest discover -s tests -v
```
