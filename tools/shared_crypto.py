"""Verify or update pinned Web sources used by the Android crypto bridge."""
import argparse
from pathlib import Path
import re
import subprocess
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
FILES = ("cloud/crypto/engine.ts", "cloud/crypto/content.ts", "cloud/crypto/canonical.ts",
         "cloud/crypto/envelope.ts", "cloud/types.ts", "chat/types.ts", "chat/drafts.ts",
         "chat/images.ts", "chat/files.ts")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--update", metavar="COMMIT", help="replace sources and pin after downloading all files")
    parser.add_argument("--source", metavar="GIT_REPO", help="read pinned objects from an existing checkout")
    args = parser.parse_args()
    pin = ROOT / "crypto/shared-revision.txt"
    revision = args.update or pin.read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"[a-f0-9]{40}", revision):
        parser.error("use a full Git commit ID")
    fetched = {}
    for relative in FILES:
        path = "web/src/" + relative
        if args.source:
            data = subprocess.check_output(["git", "-C", args.source, "show", revision + ":" + path])
        else:
            url = f"https://raw.githubusercontent.com/NingCold/llm-nest/{revision}/{path}"
            with urlopen(url, timeout=30) as response:
                data = response.read()
        fetched[ROOT / "crypto/shared" / relative] = data
    for target, data in fetched.items():
        if args.update:
            target.write_bytes(data)
        elif target.read_bytes() != data:
            raise SystemExit(f"{target.relative_to(ROOT)} differs from {revision}")
    if args.update:
        pin.write_text(revision + "\n", encoding="utf-8", newline="\n")
    print(f"Verified {len(FILES)} shared source files at {revision}")

if __name__ == "__main__":
    main()
