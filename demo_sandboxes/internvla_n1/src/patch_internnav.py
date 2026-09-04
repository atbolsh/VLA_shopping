"""InternNav setup.py says python_requires='>=3.8, <=3.12'.

PEP 440 treats <=3.12 as <=3.12.0, so vast.ai 3.12.14 is rejected
even though they list (3, 12) in SUPPORTED_PYTHON_VERSIONS. Patch
the bound and install with --ignore-requires-python.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "vendor" / "InternNav"


def patch_setup_py(setup_py: Path | None = None) -> Path:
    setup_py = setup_py or (VENDOR / "setup.py")
    if not setup_py.exists():
        raise FileNotFoundError(
            f"InternNav not cloned at {setup_py.parent}. Run setup.sh through the clone step."
        )
    text = setup_py.read_text(encoding="utf-8")
    new, n = re.subn(
        r"python_requires\s*=\s*['\"][^'\"]+['\"]",
        "python_requires='>=3.8,<3.13'",
        text,
        count=1,
    )
    if n:
        setup_py.write_text(new, encoding="utf-8")
        print(f"patched {setup_py} python_requires -> >=3.8,<3.13")
    else:
        print(f"{setup_py}: no python_requires line found")
    return setup_py


def internnav_importable() -> bool:
    """Package import only. Do not touch internnav.agent — its __init__
    pulls Habitat CMA/RDP agents that this inference sandbox does not install.
    """
    if str(VENDOR) not in sys.path:
        sys.path.insert(0, str(VENDOR))
    try:
        import internnav  # noqa: F401
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"import internnav failed: {type(exc).__name__} {exc}")
        return False


def ensure_internnav(*, force_pip: bool = False) -> None:
    os.environ["PIP_IGNORE_REQUIRES_PYTHON"] = "1"
    patch_setup_py()
    if not force_pip and internnav_importable():
        print("internnav importable")
        return
    cmd = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--ignore-requires-python",
        "-e",
        str(VENDOR),
    ]
    print("+", " ".join(cmd))
    subprocess.check_call(cmd)
    if not internnav_importable():
        raise RuntimeError("internnav still not importable after pip install")


if __name__ == "__main__":
    ensure_internnav(force_pip=True)
