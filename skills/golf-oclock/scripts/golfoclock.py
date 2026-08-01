#!/usr/bin/env python3
"""Read-only CLI for The Tips Golf O'Clock API."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


DEFAULT_BASE_URL = "https://thetipsgolf.golfoclock.com"
KEYCHAIN_SERVICE = "the-tips-golf-oclock-api"
KEYCHAIN_ACCOUNT = "codex"
ALLOWED_ROUTES = {
    "CONFIGURATION/get-tenant",
    "RESERVATIONS/search",
    "USERS/search",
    "USERS/get-reservations",
    "USERS/get-account-balance",
}


class GolfOClockError(RuntimeError):
    """Base error for safe, user-facing failures."""


class ConfigurationError(GolfOClockError):
    """Raised when local configuration is missing or invalid."""


class APIError(GolfOClockError):
    """Raised when the remote API request fails."""


def normalize_api_root(base_url: str) -> str:
    value = base_url.strip().rstrip("/")
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ConfigurationError("Golf O'Clock base URL must be an HTTPS origin.")
    allowed_paths = {"", "/", "/api/api-o-clock"}
    if parsed.path not in allowed_paths or parsed.params or parsed.query or parsed.fragment:
        raise ConfigurationError(
            "Golf O'Clock base URL must be a tenant origin or end in /api/api-o-clock."
        )
    if parsed.path == "/api/api-o-clock":
        return value
    return f"{parsed.scheme}://{parsed.netloc}/api/api-o-clock"


def load_api_key() -> str:
    env_key = os.environ.get("GOLFOCLOCK_API_KEY", "").strip()
    if env_key:
        return env_key

    if sys.platform == "darwin" and Path("/usr/bin/security").exists():
        result = subprocess.run(
            [
                "/usr/bin/security",
                "find-generic-password",
                "-a",
                KEYCHAIN_ACCOUNT,
                "-s",
                KEYCHAIN_SERVICE,
                "-w",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        key = result.stdout.strip()
        if result.returncode == 0 and key:
            return key

    raise ConfigurationError(
        "No API key found. Run scripts/configure-keychain.sh from the repository "
        "or set GOLFOCLOCK_API_KEY for this process only."
    )


class Client:
    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = 60,
        opener: Callable[..., Any] = urlopen,
    ) -> None:
        self.api_key = api_key
        self.api_root = normalize_api_root(base_url)
        self.timeout = timeout
        self.opener = opener

    def post(self, route: str, body: dict[str, Any]) -> Any:
        if route not in ALLOWED_ROUTES:
            raise ConfigurationError(f"Route is not allowlisted for read-only access: {route}")

        request = Request(
            f"{self.api_root}/{route}",
            data=json.dumps(body).encode("utf-8"),
            method="POST",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "the-tips-golf-oclock-codex/1.0",
            },
        )
        try:
            with self.opener(request, timeout=self.timeout) as response:
                return json.load(response)
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:500].strip()
            suffix = f" Response: {detail}" if detail else ""
            raise APIError(f"Golf O'Clock returned HTTP {exc.code}.{suffix}") from exc
        except URLError as exc:
            raise APIError(f"Could not reach Golf O'Clock: {exc.reason}") from exc
        except json.JSONDecodeError as exc:
            raise APIError("Golf O'Clock returned an invalid JSON response.") from exc


def parse_iso_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Expected a real date in YYYY-MM-DD format.") from exc


def validate_date_range(start: date, end: date) -> None:
    if start > end:
        raise ConfigurationError("Reservation start date must be on or before the end date.")


def fetch_reservations(
    client: Client,
    start: date,
    end: date,
    status: str | None,
    max_results: int,
) -> dict[str, Any]:
    validate_date_range(start, end)
    if not 1 <= max_results <= 10000:
        raise ConfigurationError("--max-results must be between 1 and 10000.")

    filters: list[list[Any]] = [
        ["availability.date", ">=", start.isoformat()],
        ["availability.date", "<=", end.isoformat()],
    ]
    if status:
        filters.append(["status", "==", status])

    reservations: list[Any] = []
    cursor: str | None = None
    seen_cursors: set[str] = set()
    remote_has_more = False

    while len(reservations) < max_results:
        body: dict[str, Any] = {
            "filters": filters,
            "orderBy": "availability.date",
            "orderDirection": "asc",
            "limit": min(100, max_results - len(reservations)),
        }
        if cursor:
            body["startAfter"] = cursor

        response = client.post("RESERVATIONS/search", body)
        if not isinstance(response, dict):
            raise APIError("Reservation search returned an unexpected response shape.")
        batch = response.get("reservations", [])
        if not isinstance(batch, list):
            raise APIError("Reservation search did not return a reservations list.")

        reservations.extend(batch)
        next_cursor = response.get("nextCursor")
        remote_has_more = bool(next_cursor)
        if not batch or not next_cursor:
            break
        if not isinstance(next_cursor, str) or next_cursor in seen_cursors:
            raise APIError("Reservation pagination returned an invalid or repeated cursor.")
        seen_cursors.add(next_cursor)
        cursor = next_cursor

    return {
        "query": {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "status": status,
            "max_results": max_results,
        },
        "count": len(reservations),
        "truncated": len(reservations) >= max_results and remote_has_more,
        "reservations": reservations,
    }


def doctor_summary(client: Client) -> dict[str, Any]:
    response = client.post("CONFIGURATION/get-tenant", {})
    summary: dict[str, Any] = {
        "ok": True,
        "api_root": client.api_root,
        "response_type": type(response).__name__,
    }
    if isinstance(response, dict):
        summary["top_level_keys"] = sorted(response.keys())
        safe_identity = {}
        for field in ("id", "name", "displayName", "slug", "domain"):
            value = response.get(field)
            if isinstance(value, (str, int, float, bool)) or value is None:
                safe_identity[field] = value
        if safe_identity:
            summary["tenant"] = safe_identity
    return summary


def write_result(result: Any, output: Path | None, compact: bool) -> None:
    indent = None if compact else 2
    rendered = json.dumps(result, indent=indent, ensure_ascii=False, sort_keys=False) + "\n"
    if output is None:
        sys.stdout.write(rendered)
        return

    output = output.expanduser()
    output.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(rendered)
    finally:
        os.chmod(output, 0o600)
    print(f"Wrote {output} with owner-only permissions.", file=sys.stderr)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base-url",
        default=os.environ.get("GOLFOCLOCK_BASE_URL", DEFAULT_BASE_URL),
        help="Tenant HTTPS origin. Defaults to The Tips Golf O'Clock tenant.",
    )
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--output", type=Path, help="Write JSON to this local file.")
    parser.add_argument("--compact", action="store_true", help="Emit compact JSON.")

    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("doctor", help="Verify credentials without returning customer data.")
    commands.add_parser("tenant", help="Return export-safe tenant configuration.")

    reservations = commands.add_parser("reservations", help="Search reservations by date.")
    reservations.add_argument("--start", type=parse_iso_date, required=True)
    reservations.add_argument("--end", type=parse_iso_date, required=True)
    reservations.add_argument("--status")
    reservations.add_argument("--max-results", type=int, default=500)

    user = commands.add_parser("user", help="Find a user by one exact identifier.")
    user_identifier = user.add_mutually_exclusive_group(required=True)
    user_identifier.add_argument("--email")
    user_identifier.add_argument("--phone")
    user_identifier.add_argument("--id")

    user_reservations = commands.add_parser(
        "user-reservations", help="Return one user's reservations."
    )
    user_reservations.add_argument("--user-id", required=True)
    user_reservations.add_argument("--include-past", action="store_true")
    user_reservations.add_argument("--include-canceled", action="store_true")

    balance = commands.add_parser("balance", help="Return one user's account balance.")
    balance.add_argument("--user-id", required=True)
    balance.add_argument("--account-id", default="default")
    balance.add_argument("--include-updates", action="store_true")
    return parser


def execute(args: argparse.Namespace, client: Client) -> Any:
    if args.command == "doctor":
        return doctor_summary(client)
    if args.command == "tenant":
        return client.post("CONFIGURATION/get-tenant", {})
    if args.command == "reservations":
        return fetch_reservations(
            client, args.start, args.end, args.status, args.max_results
        )
    if args.command == "user":
        body = {
            key: value
            for key, value in (("email", args.email), ("phone", args.phone), ("id", args.id))
            if value is not None
        }
        return client.post("USERS/search", body)
    if args.command == "user-reservations":
        return client.post(
            "USERS/get-reservations",
            {
                "userId": args.user_id,
                "includePast": args.include_past,
                "includeCanceled": args.include_canceled,
            },
        )
    if args.command == "balance":
        return client.post(
            "USERS/get-account-balance",
            {
                "userId": args.user_id,
                "accountId": args.account_id,
                "returnUpdates": args.include_updates,
            },
        )
    raise ConfigurationError(f"Unsupported command: {args.command}")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.timeout < 1 or args.timeout > 300:
        parser.error("--timeout must be between 1 and 300 seconds.")

    try:
        client = Client(load_api_key(), args.base_url, args.timeout)
        result = execute(args, client)
        write_result(result, args.output, args.compact)
        return 0
    except GolfOClockError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
