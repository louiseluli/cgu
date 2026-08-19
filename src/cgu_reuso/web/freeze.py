"""Render the Wage Gap Explorer to static HTML for GitHub Pages.

The app is GET-only with no session state, so every page it can produce is
just `create_app(base_path=...).test_client().get(url).data` written to disk
— no separate static-site generator needed. `base_path` is baked into every
internal link at render time so the frozen output works at a GitHub Pages
project-site subpath (https://<user>.github.io/<repo>/) instead of root.
"""

import shutil
from pathlib import Path

from .app import _DOWNLOADABLE, create_app, municipality_codes

CGU_ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = CGU_ROOT / "docs"
BASE_PATH = "/cgu"


def write(client, url: str, out_path: Path) -> None:
    resp = client.get(url)
    if resp.status_code != 200:
        raise RuntimeError(f"{url} -> {resp.status_code}")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(resp.data)


def main() -> None:
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)

    app = create_app(base_path=BASE_PATH)
    client = app.test_client()

    write(client, "/", OUT_DIR / "index.html")

    codes = municipality_codes()
    for code in codes:
        write(client, f"/municipio/{code}/", OUT_DIR / "municipio" / str(code) / "index.html")
    print(f"Wrote {len(codes)} município pages + homepage")

    static_src = Path(__file__).resolve().parent / "static"
    shutil.copytree(static_src, OUT_DIR / "static")
    print(f"Copied static assets from {static_src}")

    download_dir = OUT_DIR / "download"
    download_dir.mkdir()
    for filename, source_dir in _DOWNLOADABLE.items():
        shutil.copy(source_dir / filename, download_dir / filename)
    print(f"Copied {len(_DOWNLOADABLE)} downloadable CSVs")

    (OUT_DIR / ".nojekyll").touch()  # GitHub Pages: don't run Jekyll on this

    print(f"\nStatic site ready at {OUT_DIR}")


if __name__ == "__main__":
    main()
