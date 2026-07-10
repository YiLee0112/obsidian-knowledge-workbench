#!/usr/bin/env python3
"""Install enabled Obsidian community plugins for this vault.

The script reads .obsidian/community-plugins.json, resolves plugin GitHub
repositories from Obsidian's official community plugin index, then downloads the
release assets Obsidian needs: manifest.json, main.js, and optional styles.css.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


COMMUNITY_INDEX_URL = (
    "https://raw.githubusercontent.com/obsidianmd/obsidian-releases/"
    "master/community-plugins.json"
)
ASSETS = ("manifest.json", "main.js", "styles.css")


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"Missing file: {path}") from None
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}") from None


def fetch_bytes(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "obsidian-vault-plugin-installer"})
    with urlopen(request, timeout=60) as response:
        return response.read()


def fetch_json(url: str):
    try:
        return json.loads(fetch_bytes(url).decode("utf-8"))
    except (HTTPError, URLError) as exc:
        raise SystemExit(f"Could not fetch community plugin index: {exc}") from None
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Community plugin index is not valid JSON: {exc}") from None


def load_enabled_plugins(vault: Path) -> list[str]:
    plugins = read_json(vault / ".obsidian" / "community-plugins.json")
    if not isinstance(plugins, list) or not all(isinstance(item, str) for item in plugins):
        raise SystemExit(".obsidian/community-plugins.json must be a JSON array of plugin IDs")
    return plugins


def load_manual_sources(vault: Path) -> dict[str, dict[str, str]]:
    path = vault / ".obsidian" / "plugin-sources.json"
    if not path.exists():
        return {}

    data = read_json(path)
    if not isinstance(data, dict):
        raise SystemExit(".obsidian/plugin-sources.json must be a JSON object")

    sources: dict[str, dict[str, str]] = {}
    for plugin_id, source in data.items():
        if isinstance(source, str):
            sources[plugin_id] = {"id": plugin_id, "repo": source}
        elif isinstance(source, dict):
            sources[plugin_id] = {"id": plugin_id, **source}
        else:
            raise SystemExit(f"Invalid source for {plugin_id} in .obsidian/plugin-sources.json")
    return sources


def current_version(plugin_dir: Path) -> str | None:
    manifest = plugin_dir / "manifest.json"
    if not manifest.exists():
        return None
    data = read_json(manifest)
    version = data.get("version")
    return version if isinstance(version, str) and version else None


def release_urls(repo: str, asset: str, version: str | None, latest: bool) -> list[str]:
    tags: list[str] = []
    if version and not latest:
        tags.append(version)
        if not version.startswith("v"):
            tags.append(f"v{version}")

    urls = [f"https://github.com/{repo}/releases/download/{tag}/{asset}" for tag in tags]
    urls.append(f"https://github.com/{repo}/releases/latest/download/{asset}")
    return urls


def download_asset(repo: str, asset: str, target: Path, version: str | None, latest: bool) -> bool:
    errors: list[str] = []
    for url in release_urls(repo, asset, version, latest):
        try:
            target.write_bytes(fetch_bytes(url))
            return True
        except HTTPError as exc:
            errors.append(f"{exc.code} {url}")
            if asset == "styles.css" and exc.code == 404:
                return False
        except URLError as exc:
            errors.append(f"{exc.reason} {url}")

    if asset == "styles.css":
        return False
    raise RuntimeError(f"failed to download {asset} from {repo}: {'; '.join(errors)}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Install enabled Obsidian community plugins.")
    parser.add_argument("--vault", default=".", help="Vault path, defaults to current directory")
    parser.add_argument(
        "--latest",
        action="store_true",
        help="Always install latest releases instead of trying current local manifest versions first",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print what would be installed")
    args = parser.parse_args()

    vault = Path(args.vault).expanduser().resolve()
    enabled_plugins = load_enabled_plugins(vault)
    community_index = fetch_json(COMMUNITY_INDEX_URL)
    plugin_by_id = {plugin["id"]: plugin for plugin in community_index if "id" in plugin}
    plugin_by_id.update(load_manual_sources(vault))

    missing = [plugin_id for plugin_id in enabled_plugins if plugin_id not in plugin_by_id]
    if missing:
        print("Not found in the official community plugin index:", file=sys.stderr)
        for plugin_id in missing:
            print(f"  - {plugin_id}", file=sys.stderr)
        print("Install those manually or remove them from community-plugins.json.", file=sys.stderr)

    installed = 0
    for plugin_id in enabled_plugins:
        plugin = plugin_by_id.get(plugin_id)
        if not plugin:
            continue

        repo = plugin.get("repo")
        if not isinstance(repo, str) or "/" not in repo:
            print(f"Skipping {plugin_id}: missing GitHub repo in community index", file=sys.stderr)
            continue

        plugin_dir = vault / ".obsidian" / "plugins" / plugin_id
        version = current_version(plugin_dir)

        if args.dry_run:
            source = "latest" if args.latest or not version else version
            print(f"{plugin_id}: {repo} ({source})")
            continue

        plugin_dir.mkdir(parents=True, exist_ok=True)
        downloaded = []
        for asset in ASSETS:
            target = plugin_dir / asset
            if download_asset(repo, asset, target, version, args.latest):
                downloaded.append(asset)

        installed += 1
        print(f"Installed {plugin_id}: {', '.join(downloaded)}")

    if args.dry_run:
        print(f"Checked {len(enabled_plugins)} enabled plugins.")
    else:
        print(f"Installed {installed} plugins.")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())

