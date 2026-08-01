# Read-only API reference

All requests are JSON POSTs to:

```text
https://thetipsgolf.golfoclock.com/api/api-o-clock/<route>
```

Authentication uses `Authorization: Bearer <key>`. The CLI obtains the key from `GOLFOCLOCK_API_KEY` or the macOS Keychain item with service `the-tips-golf-oclock-api` and account `codex`.

Supported routes:

| CLI command | Route | Purpose |
|---|---|---|
| `doctor`, `tenant` | `CONFIGURATION/get-tenant` | Verify access or return export-safe tenant configuration |
| `reservations` | `RESERVATIONS/search` | Search and paginate reservations by date and optional status |
| `user` | `USERS/search` | Find users by exact email, phone, or ID |
| `user-reservations` | `USERS/get-reservations` | Return one user's reservations |
| `balance` | `USERS/get-account-balance` | Return one user's account balance and optional updates |

Reservation filters use tuples such as:

```json
[
  ["availability.date", ">=", "2026-08-01"],
  ["availability.date", "<=", "2026-08-07"],
  ["status", "==", "confirmed"]
]
```

`RESERVATIONS/search` returns up to 100 rows per page and a `nextCursor`. The CLI follows cursors until it reaches the requested `--max-results` cap or the API returns no next cursor.
