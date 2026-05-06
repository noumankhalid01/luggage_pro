from __future__ import annotations

import sys
from pathlib import Path


def _add_venv_site_packages() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    site_packages = repo_root / ".venv" / "lib" / "python3.12" / "site-packages"
    if site_packages.is_dir():
        path = str(site_packages)
        if path not in sys.path:
            sys.path.append(path)


_add_venv_site_packages()
