import json
import os
import urllib.request
from datetime import date, timedelta
from html import escape
from pathlib import Path

TOKEN = os.environ["GITHUB_TOKEN"]
USERNAME = os.environ.get("GITHUB_USERNAME", "HidayahMF")
ENDPOINT = "https://api.github.com/graphql"

QUERY = r"""
query($login: String!) {
  user(login: $login) {
    followers { totalCount }
    repositories(first: 100, ownerAffiliations: [OWNER], privacy: PUBLIC, isFork: false) {
      totalCount
      nodes {
        stargazerCount
        forkCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays { date contributionCount }
        }
      }
    }
  }
}
"""


def graphql(query, variables):
    body = json.dumps({"query": query, "variables": variables}).encode("utf-8")
    req = urllib.request.Request(
        ENDPOINT,
        data=body,
        headers={
            "Authorization": f"bearer {TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "HidayahMF-profile-analytics",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        payload = json.load(response)
    if payload.get("errors"):
        raise RuntimeError(json.dumps(payload["errors"], indent=2))
    return payload["data"]


def calculate_streaks(days):
    values = {date.fromisoformat(d["date"]): d["contributionCount"] for d in days}
    if not values:
        return 0, 0

    ordered = sorted(values)
    longest = 0
    running = 0
    for d in ordered:
        if values[d] > 0:
            running += 1
            longest = max(longest, running)
        else:
            running = 0

    last = max(ordered)
    cursor = last
    if values.get(cursor, 0) == 0:
        cursor -= timedelta(days=1)

    current = 0
    while values.get(cursor, 0) > 0:
        current += 1
        cursor -= timedelta(days=1)

    return current, longest


def svg_shell(width, height, body, title):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <title>{escape(title)}</title>
  <style>
    .bg {{ fill: #0d1117; stroke: #30363d; stroke-width: 1; }}
    .title {{ fill: #58a6ff; font: 600 18px -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif; }}
    .label {{ fill: #8b949e; font: 500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif; }}
    .value {{ fill: #f0f6fc; font: 700 20px -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif; }}
    .small {{ fill: #c9d1d9; font: 500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif; }}
  </style>
  <rect class="bg" x="0.5" y="0.5" width="{width-1}" height="{height-1}" rx="10"/>
  {body}
</svg>'''


def make_stats(user):
    repos = user["repositories"]
    nodes = repos["nodes"]
    stars = sum(repo["stargazerCount"] for repo in nodes)
    forks = sum(repo["forkCount"] for repo in nodes)
    followers = user["followers"]["totalCount"]
    calendar = user["contributionsCollection"]["contributionCalendar"]
    contributions = calendar["totalContributions"]
    days = [d for w in calendar["weeks"] for d in w["contributionDays"]]
    current, longest = calculate_streaks(days)

    metrics = [
        ("Contributions", contributions),
        ("Public Repositories", repos["totalCount"]),
        ("Total Stars", stars),
        ("Followers", followers),
        ("Current Streak", f"{current} days"),
        ("Longest Streak", f"{longest} days"),
    ]

    body = '<text class="title" x="24" y="34">GitHub Analytics</text>'
    positions = [(24, 78), (166, 78), (308, 78), (24, 150), (166, 150), (308, 150)]
    for (label, value), (x, y) in zip(metrics, positions):
        body += f'<text class="value" x="{x}" y="{y}">{escape(str(value))}</text>'
        body += f'<text class="label" x="{x}" y="{y+22}">{escape(label)}</text>'

    body += '<text class="small" x="24" y="202">Generated daily from GitHub data</text>'
    return svg_shell(440, 220, body, f"{USERNAME} GitHub analytics")


def make_languages(user):
    totals = {}
    colors = {}
    for repo in user["repositories"]["nodes"]:
        for edge in repo["languages"]["edges"]:
            name = edge["node"]["name"]
            totals[name] = totals.get(name, 0) + edge["size"]
            colors[name] = edge["node"].get("color") or "#58a6ff"

    top = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)[:6]
    grand = sum(v for _, v in top) or 1

    body = '<text class="title" x="24" y="34">Most Used Languages</text>'
    y = 68
    for name, size in top:
        pct = size / grand * 100
        bar_w = max(4, 300 * pct / 100)
        color = colors.get(name, "#58a6ff")
        body += f'<circle cx="28" cy="{y-4}" r="5" fill="{escape(color)}"/>'
        body += f'<text class="small" x="42" y="{y}">{escape(name)}</text>'
        body += f'<text class="label" x="396" y="{y}" text-anchor="end">{pct:.1f}%</text>'
        body += f'<rect x="42" y="{y+8}" width="300" height="6" rx="3" fill="#21262d"/>'
        body += f'<rect x="42" y="{y+8}" width="{bar_w:.1f}" height="6" rx="3" fill="{escape(color)}"/>'
        y += 27

    if not top:
        body += '<text class="small" x="24" y="80">No public language data available.</text>'

    return svg_shell(440, 240, body, f"{USERNAME} most used languages")


def main():
    data = graphql(QUERY, {"login": USERNAME})
    user = data["user"]
    if not user:
        raise RuntimeError(f"GitHub user not found: {USERNAME}")

    out = Path("generated")
    out.mkdir(exist_ok=True)
    (out / "github-stats.svg").write_text(make_stats(user), encoding="utf-8")
    (out / "top-languages.svg").write_text(make_languages(user), encoding="utf-8")


if __name__ == "__main__":
    main()
