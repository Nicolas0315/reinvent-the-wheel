"""Reinvent the wheel, literally.

Builds rewheel-0.1.0-py3-none-any.whl by hand per PEP 427 —
no setuptools, no pip, no build. Just zipfile, hashlib, base64.
"""

import base64
import hashlib
import zipfile
from pathlib import Path

NAME = "rewheel"
VERSION = "0.1.0"
TAG = "py3-none-any"
DIST_INFO = f"{NAME}-{VERSION}.dist-info"
WHEEL_FILE = f"{NAME}-{VERSION}-{TAG}.whl"

METADATA = f"""\
Metadata-Version: 2.1
Name: {NAME}
Version: {VERSION}
Summary: The wheel, reinvented (Myers diff packaged in a hand-rolled wheel)
Requires-Python: >=3.8
"""

WHEEL_META = f"""\
Wheel-Version: 1.0
Generator: bare-hands (0.0.0)
Root-Is-Purelib: true
Tag: {TAG}
"""


def record_hash(data: bytes) -> str:
    digest = hashlib.sha256(data).digest()
    return "sha256=" + base64.urlsafe_b64encode(digest).rstrip(b"=").decode()


def main():
    root = Path(__file__).parent
    entries = []  # (archive_name, bytes)
    for src in sorted((root / NAME).rglob("*.py")):
        entries.append((f"{NAME}/{src.relative_to(root / NAME)}", src.read_bytes()))
    entries.append((f"{DIST_INFO}/METADATA", METADATA.encode()))
    entries.append((f"{DIST_INFO}/WHEEL", WHEEL_META.encode()))

    record_lines = [f"{name},{record_hash(data)},{len(data)}" for name, data in entries]
    record_lines.append(f"{DIST_INFO}/RECORD,,")
    entries.append((f"{DIST_INFO}/RECORD", ("\n".join(record_lines) + "\n").encode()))

    out = root / WHEEL_FILE
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, data in entries:
            # fixed timestamp: reproducible builds, and no Date.now in sight
            zf.writestr(zipfile.ZipInfo(name, (2026, 7, 5, 0, 0, 0)), data)
    print(f"built {out.name} ({out.stat().st_size} bytes)")
    for name, _ in entries:
        print(f"  {name}")


if __name__ == "__main__":
    main()
