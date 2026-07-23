#!/usr/bin/env python3
"""iTunes Lookup APIから公開中アプリを取得し、READMEのマーカー間を書き換える。

新しいアプリがApp Storeに公開されると、次回のワークフロー実行で自動的に表へ追加される。
"""
import json
import re
import sys
import urllib.request
from pathlib import Path

ARTIST_ID = 883528248  # Takeshita Kyohei
LOOKUP_URL = (
    f"https://itunes.apple.com/lookup?id={ARTIST_ID}&country=jp&entity=software&limit=200"
)
README = Path(__file__).resolve().parent.parent / "README.md"
BEGIN = "<!-- APPS:BEGIN -->"
END = "<!-- APPS:END -->"


def fetch_apps():
    req = urllib.request.Request(LOOKUP_URL, headers={"User-Agent": "profile-readme-bot"})
    with urllib.request.urlopen(req, timeout=30) as res:
        data = json.load(res)
    apps = [r for r in data["results"] if r.get("wrapperType") == "software"]
    apps.sort(key=lambda a: a.get("releaseDate", ""), reverse=True)
    return apps


def build_table(apps):
    lines = [
        "| | App | ジャンル | Store |",
        "|---|---|---|---|",
    ]
    for a in apps:
        icon = a.get("artworkUrl100", "")
        name = a["trackName"].split(" - ")[0].split("｜")[0].strip()
        genre = a.get("primaryGenreName", "-")
        url = a["trackViewUrl"].split("?")[0]
        lines.append(
            f'| <img src="{icon}" width="48" alt=""> | **{name}** | {genre} | [App Store]({url}) |'
        )
    return "\n".join(lines)


def main():
    apps = fetch_apps()
    if not apps:
        print("No apps returned; keeping README unchanged", file=sys.stderr)
        return 1
    content = README.read_text(encoding="utf-8")
    block = f"{BEGIN}\n{build_table(apps)}\n{END}"
    new_content = re.sub(
        re.escape(BEGIN) + r".*?" + re.escape(END), block, content, flags=re.DOTALL
    )
    if new_content == content:
        print("README is up to date")
        return 0
    README.write_text(new_content, encoding="utf-8")
    print(f"README updated with {len(apps)} apps")
    return 0


if __name__ == "__main__":
    sys.exit(main())
