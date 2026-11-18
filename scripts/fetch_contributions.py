#!/usr/bin/env python3
"""Fetch contribution calendar data from the official GitHub GraphQL API.

Never scrapes github.com HTML pages. Writes data/contributions.json.
"""
import datetime
import json
import os
import subprocess
import sys
from collections import defaultdict

import requests

USERNAME = "Mohammed9620"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT_PATH = os.path.join(ROOT, "data", "contributions.json")

GRAPHQL_QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""


def resolve_token() -> str:
    for var in ("GITHUB_TOKEN", "GH_TOKEN"):
        tok = os.environ.get(var, "").strip()
        if tok:
            return tok
    try:
        proc = subprocess.run(
            ["git", "credential", "fill"],
            input="protocol=https\nhost=github.com\n\n",
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        for line in proc.stdout.splitlines():
            if line.startswith("password="):
                tok = line.split("=", 1)[1].strip()
                if tok:
                    return tok
    except OSError:
        pass
    raise RuntimeError(
        "No GitHub token found. Set GITHUB_TOKEN or GH_TOKEN, or configure git credentials."
    )


def fetch_calendar(username: str, token: str) -> dict:
    resp = requests.post(
        "https://api.github.com/graphql",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        },
        json={"query": GRAPHQL_QUERY, "variables": {"login": username}},
        timeout=30,
    )
    resp.raise_for_status()
    payload = resp.json()
    if payload.get("errors"):
        raise RuntimeError(f"GraphQL errors: {payload['errors']}")
    user = (payload.get("data") or {}).get("user")
    if not user:
        raise RuntimeError(f"GitHub user {username!r} not found in GraphQL response.")
    return user["contributionsCollection"]["contributionCalendar"]


def build_summary(username: str, calendar: dict) -> dict:
    days = []
    for week in calendar["weeks"]:
        for day in week["contributionDays"]:
            days.append(
                {
                    "date": day["date"],
                    "count": int(day["contributionCount"]),
                }
            )
    days.sort(key=lambda d: d["date"])

    total = int(calendar["totalContributions"])
    active_days = sum(1 for d in days if d["count"] > 0)
    avg = round(total / max(1, active_days), 1)
    best = max(days, key=lambda d: (d["count"], d["date"])) if days else {"date": "", "count": 0}

    month_totals: dict[str, int] = defaultdict(int)
    for d in days:
        month_totals[d["date"][:7]] += d["count"]
    monthly = [{"month": m, "total": month_totals[m]} for m in sorted(month_totals)[-12:]]

    return {
        "username": username,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "range": {
            "start": days[0]["date"] if days else "",
            "end": days[-1]["date"] if days else "",
        },
        "total_contributions": total,
        "active_days": active_days,
        "avg_per_active_day": avg,
        "best_day": {"date": best["date"], "count": best["count"]},
        "monthly": monthly,
        "days": days,
    }


def main() -> int:
    token = resolve_token()
    calendar = fetch_calendar(USERNAME, token)
    summary = build_summary(USERNAME, calendar)

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
        f.write("\n")

    print(
        f"wrote {os.path.relpath(OUT_PATH, ROOT)}: "
        f"{summary['total_contributions']} contributions, "
        f"{summary['active_days']} active days, "
        f"best {summary['best_day']['count']} on {summary['best_day']['date']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
