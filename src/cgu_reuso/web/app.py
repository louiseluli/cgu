"""Wage Gap Explorer — Flask dashboard over the invisibility-index outputs.

Pick a município, see its actual gap, how it compares to naive single-axis
addition, and a citable one-paragraph summary. Server-rendered, no JS
dependency, accessible by default (semantic HTML, real <label>s, alt text).
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from flask import Flask, abort, render_template, send_from_directory

from .story import build_story, format_brl

CGU_ROOT = Path(__file__).resolve().parents[3]
TABLES_DIR = CGU_ROOT / "outputs/tables/invisibility_index"
MODEL_DIR = CGU_ROOT / "outputs/tables/wage_model"
MIN_CELL_COUNT = 100

_DOWNLOADABLE = {
    "municipality_invisibility_index.csv": TABLES_DIR,
    "statewide_invisibility_index.csv": TABLES_DIR,
    "shap_feature_importance.csv": MODEL_DIR,
}


def _load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    muni = pd.read_csv(TABLES_DIR / "municipality_invisibility_index.csv")
    state = pd.read_csv(TABLES_DIR / "statewide_invisibility_index.csv")
    return muni, state


def _load_shap() -> tuple[list[dict], dict] | tuple[None, None]:
    importance_path = MODEL_DIR / "shap_feature_importance.csv"
    summary_path = MODEL_DIR / "shap_summary.json"
    if not importance_path.exists() or not summary_path.exists():
        return None, None
    importance = pd.read_csv(importance_path).to_dict(orient="records")
    summary = json.loads(summary_path.read_text())
    return importance, summary


def _trend_path(series: pd.Series, years: pd.Series, width: int = 520, height: int = 120,
                 pad_l: int = 8, pad_r: int = 8, pad_t: int = 10, pad_b: int = 10) -> tuple[str, list[dict]]:
    """Build an SVG path (breaking across missing years) plus point markers."""
    if series.empty:
        return "", []
    vmin, vmax = series.min(), series.max()
    if vmax == vmin:
        vmax = vmin + 1
    yr_min, yr_max = years.min(), years.max()
    yr_span = max(yr_max - yr_min, 1)

    def x(year: int) -> float:
        return pad_l + (year - yr_min) / yr_span * (width - pad_l - pad_r)

    def y(value: float) -> float:
        return pad_t + (vmax - value) / (vmax - vmin) * (height - pad_t - pad_b)

    points = [
        {"year": int(yr), "x": round(x(yr), 1), "y": round(y(v), 1), "v": round(float(v), 1)}
        for yr, v in zip(years, series)
    ]

    segments: list[list[dict]] = []
    for i, pt in enumerate(points):
        if i == 0 or pt["year"] - points[i - 1]["year"] > 1:
            segments.append([pt])
        else:
            segments[-1].append(pt)

    path_parts = []
    for seg in segments:
        if len(seg) < 2:
            continue
        path_parts.append("M" + f"{seg[0]['x']},{seg[0]['y']}" + " " +
                           " ".join(f"L{p['x']},{p['y']}" for p in seg[1:]))
    path_d = " ".join(path_parts)

    return path_d, points


def create_app(base_path: str = "") -> Flask:
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.jinja_env.filters["brl"] = format_brl
    muni_df, state_df = _load_data()
    shap_importance, shap_summary = _load_shap()

    latest_year = int(muni_df["year"].max())
    muni_list = (
        muni_df[muni_df["year"] == latest_year][["municipality_code", "municipality_name"]]
        .sort_values("municipality_name")
        .to_dict(orient="records")
    )

    qualified_latest = muni_df[
        (muni_df["year"] == latest_year)
        & (muni_df["count_male_white"] >= MIN_CELL_COUNT)
        & (muni_df["count_female_black"] >= MIN_CELL_COUNT)
    ].sort_values("invisibility_index", ascending=False).reset_index(drop=True)
    n_qualified = len(qualified_latest)

    def _render(code: int | None):
        selected = None
        story = None
        trend_path = ""
        trend_points: list[dict] = []
        rank = None

        if code is not None:
            rows = muni_df[muni_df["municipality_code"] == code]
            if rows.empty:
                abort(404)
            latest_row = rows[rows["year"] == latest_year]
            if latest_row.empty:
                latest_row = rows[rows["year"] == rows["year"].max()]
            selected = latest_row.iloc[0].to_dict()

            match = qualified_latest.index[
                qualified_latest["municipality_code"] == code
            ]
            rank = int(match[0]) + 1 if len(match) else None

            story = build_story(selected, rank, n_qualified)

            series = rows.sort_values("year")
            trend_path, trend_points = _trend_path(series["actual_gap"], series["year"])

        state_latest = state_df[state_df["year"] == state_df["year"].max()].iloc[0].to_dict()

        return render_template(
            "index.html",
            muni_list=muni_list,
            selected=selected,
            story=story,
            trend_path=trend_path,
            trend_points=trend_points,
            code_param=code,
            latest_year=latest_year,
            n_qualified=n_qualified,
            n_total=len(muni_list),
            min_cell_count=MIN_CELL_COUNT,
            state_latest=state_latest,
            shap_importance=shap_importance,
            shap_summary=shap_summary,
            base_path=base_path,
        )

    @app.route("/")
    def index():
        return _render(None)

    @app.route("/municipio/<int:code>/")
    def municipio(code: int):
        return _render(code)

    @app.route("/download/<path:filename>")
    def download(filename: str):
        directory = _DOWNLOADABLE.get(filename)
        if directory is None:
            abort(404)
        return send_from_directory(directory, filename, as_attachment=True)

    return app


def municipality_codes() -> list[int]:
    """Municipality codes for the latest year — used by freeze.py to enumerate
    every static page to generate."""
    muni, _ = _load_data()
    latest = int(muni["year"].max())
    return sorted(muni[muni["year"] == latest]["municipality_code"].unique().tolist())


if __name__ == "__main__":
    create_app().run(debug=True, port=5050)
