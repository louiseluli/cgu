"""Compute the invisibility index: how much of the white-men-vs-Black-women wage
gap is missed by adding a sex-only gap to a race-only gap.

Source: wage_gap's municipality_sex_race_summary.csv (RAIS, RJ, 2010-2024), which
carries mean_wage and worker_count per (year, municipality, sex, race) cell. Sex-only
and race-only gaps are derived here as worker-count-weighted averages that collapse
the other dimension, so all three gaps (sex-only, race-only, intersectional) come
from the same source table and are directly comparable.

invisibility_index = actual intersectional gap - (sex-only gap + race-only gap)
invisibility_pct   = invisibility_index / actual intersectional gap * 100
"""

import json
from pathlib import Path

import pandas as pd

WAGE_GAP_ROOT = Path("/Users/louisesfer/Documents/Portfolios/wage_gap")
SOURCE_CSV = (
    WAGE_GAP_ROOT / "outputs/analysis/intersectional/municipality_sex_race_summary.csv"
)

CGU_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = CGU_ROOT / "outputs/tables/invisibility_index"

GEO_COLS = [
    "municipality_name",
    "uf_sigla",
    "uf_name",
    "mesoregion_name",
    "microregion_name",
    "immediate_region_name",
    "intermediate_region_name",
]


def weighted_mean_by(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    """Worker-count-weighted mean_wage, collapsing every column not in group_cols
    (other than worker_count/mean_wage)."""
    weighted = df.assign(_wsum=df["worker_count"] * df["mean_wage"])
    agg = weighted.groupby(group_cols, as_index=False).agg(
        _wsum=("_wsum", "sum"), worker_count=("worker_count", "sum")
    )
    agg["mean_wage"] = agg["_wsum"] / agg["worker_count"]
    return agg.drop(columns="_wsum")


def build_municipality_table(df: pd.DataFrame) -> pd.DataFrame:
    geo = df.drop_duplicates(["year", "municipality_code"])[
        ["year", "municipality_code", *GEO_COLS]
    ]

    intersectional = df[
        ((df["sex_label"] == "male") & (df["race_label"] == "white"))
        | ((df["sex_label"] == "female") & (df["race_label"] == "black"))
    ]
    inter_wide = intersectional.pivot_table(
        index=["year", "municipality_code"],
        columns=["sex_label", "race_label"],
        values="mean_wage",
    )
    inter_wide.columns = ["_".join(c) for c in inter_wide.columns]
    inter_wide = inter_wide.reset_index()

    inter_counts = intersectional.pivot_table(
        index=["year", "municipality_code"],
        columns=["sex_label", "race_label"],
        values="worker_count",
    )
    inter_counts.columns = [f"count_{'_'.join(c)}" for c in inter_counts.columns]
    inter_counts = inter_counts.reset_index()

    sex_only = weighted_mean_by(df, ["year", "municipality_code", "sex_label"])
    sex_wide = sex_only.pivot_table(
        index=["year", "municipality_code"], columns="sex_label", values="mean_wage"
    )
    sex_wide.columns = [f"sex_only_{c}" for c in sex_wide.columns]
    sex_wide = sex_wide.reset_index()

    race_only = weighted_mean_by(
        df[df["race_label"].isin(["black", "white"])],
        ["year", "municipality_code", "race_label"],
    )
    race_wide = race_only.pivot_table(
        index=["year", "municipality_code"], columns="race_label", values="mean_wage"
    )
    race_wide.columns = [f"race_only_{c}" for c in race_wide.columns]
    race_wide = race_wide.reset_index()

    out = (
        geo.merge(inter_wide, on=["year", "municipality_code"], how="inner")
        .merge(inter_counts, on=["year", "municipality_code"], how="inner")
        .merge(sex_wide, on=["year", "municipality_code"], how="inner")
        .merge(race_wide, on=["year", "municipality_code"], how="inner")
    )

    out = out.dropna(
        subset=["male_white", "female_black", "sex_only_male", "sex_only_female",
                 "race_only_white", "race_only_black"]
    )

    out["actual_gap"] = out["male_white"] - out["female_black"]
    out["sex_only_gap"] = out["sex_only_male"] - out["sex_only_female"]
    out["race_only_gap"] = out["race_only_white"] - out["race_only_black"]
    out["naive_additive_gap"] = out["sex_only_gap"] + out["race_only_gap"]
    out["invisibility_index"] = out["actual_gap"] - out["naive_additive_gap"]
    out["invisibility_pct"] = (
        out["invisibility_index"] / out["actual_gap"] * 100
    )

    cols = [
        "year",
        "municipality_code",
        *GEO_COLS,
        "count_male_white",
        "count_female_black",
        "actual_gap",
        "sex_only_gap",
        "race_only_gap",
        "naive_additive_gap",
        "invisibility_index",
        "invisibility_pct",
    ]
    return out[cols].sort_values(["year", "municipality_code"]).reset_index(drop=True)


def build_statewide_table(df: pd.DataFrame) -> pd.DataFrame:
    intersectional = df[
        ((df["sex_label"] == "male") & (df["race_label"] == "white"))
        | ((df["sex_label"] == "female") & (df["race_label"] == "black"))
    ]
    inter_state = weighted_mean_by(intersectional, ["year", "sex_label", "race_label"])
    inter_wide = inter_state.pivot_table(
        index="year", columns=["sex_label", "race_label"], values="mean_wage"
    )
    inter_wide.columns = ["_".join(c) for c in inter_wide.columns]
    inter_wide = inter_wide.reset_index()

    sex_state = weighted_mean_by(df, ["year", "sex_label"])
    sex_wide = sex_state.pivot_table(index="year", columns="sex_label", values="mean_wage")
    sex_wide.columns = [f"sex_only_{c}" for c in sex_wide.columns]
    sex_wide = sex_wide.reset_index()

    race_state = weighted_mean_by(
        df[df["race_label"].isin(["black", "white"])], ["year", "race_label"]
    )
    race_wide = race_state.pivot_table(index="year", columns="race_label", values="mean_wage")
    race_wide.columns = [f"race_only_{c}" for c in race_wide.columns]
    race_wide = race_wide.reset_index()

    out = inter_wide.merge(sex_wide, on="year").merge(race_wide, on="year")

    out["actual_gap"] = out["male_white"] - out["female_black"]
    out["sex_only_gap"] = out["sex_only_male"] - out["sex_only_female"]
    out["race_only_gap"] = out["race_only_white"] - out["race_only_black"]
    out["naive_additive_gap"] = out["sex_only_gap"] + out["race_only_gap"]
    out["invisibility_index"] = out["actual_gap"] - out["naive_additive_gap"]
    out["invisibility_pct"] = out["invisibility_index"] / out["actual_gap"] * 100

    cols = [
        "year",
        "actual_gap",
        "sex_only_gap",
        "race_only_gap",
        "naive_additive_gap",
        "invisibility_index",
        "invisibility_pct",
    ]
    return out[cols].sort_values("year").reset_index(drop=True)


MIN_CELL_COUNT = 100  # minimum workers required in both the white-men and
# black-women cells for a municipality to be ranked; below this, invisibility_pct
# is dominated by sampling noise rather than a real local effect (verified: the
# unfiltered top-of-ranking was dominated by municipalities with 50-170 black-women
# workers, e.g. Cardoso Moreira N=58, São José de Ubá N=52).


def build_summary(municipality_table: pd.DataFrame, statewide_table: pd.DataFrame) -> dict:
    latest_year = int(statewide_table["year"].max())
    first_year = int(statewide_table["year"].min())
    latest_state = statewide_table[statewide_table["year"] == latest_year].iloc[0]
    first_state = statewide_table[statewide_table["year"] == first_year].iloc[0]

    latest_muni = municipality_table[municipality_table["year"] == latest_year]
    qualified = latest_muni[
        (latest_muni["count_male_white"] >= MIN_CELL_COUNT)
        & (latest_muni["count_female_black"] >= MIN_CELL_COUNT)
    ]

    # invisibility_pct divides by actual_gap, so a municipality with a large,
    # well-sampled actual gap that happens to sit near zero (e.g. Maricá 2024:
    # N=2004 black women, actual_gap=R$29) still produces an extreme pct even
    # after the N-filter. p5/p95 is the robust headline stat; raw min/max is kept
    # for transparency but should not be quoted without that caveat. Rankings use
    # invisibility_index (R$) rather than pct for exactly this reason.
    heterogeneity = {
        "n_municipalities_qualified": int(len(qualified)),
        "min_cell_count_threshold": MIN_CELL_COUNT,
        "invisibility_pct_std": round(float(qualified["invisibility_pct"].std()), 1),
        "invisibility_pct_p5": round(float(qualified["invisibility_pct"].quantile(0.05)), 1),
        "invisibility_pct_p95": round(float(qualified["invisibility_pct"].quantile(0.95)), 1),
        "invisibility_pct_min_raw": round(float(qualified["invisibility_pct"].min()), 1),
        "invisibility_pct_max_raw": round(float(qualified["invisibility_pct"].max()), 1),
        "invisibility_pct_min_max_caveat": (
            "min/max can be driven by a near-zero actual_gap denominator rather "
            "than a large real effect, even at N>=100 (see EDA section 3.1); "
            "prefer p5/p95 or the R$ invisibility_index rankings below."
        ),
    }

    top_super_additive = (
        qualified.sort_values("invisibility_index", ascending=False)
        .head(10)[
            ["municipality_name", "count_male_white", "count_female_black",
             "actual_gap", "invisibility_index", "invisibility_pct"]
        ]
        .to_dict(orient="records")
    )
    top_sub_additive = (
        qualified.sort_values("invisibility_index", ascending=True)
        .head(10)[
            ["municipality_name", "count_male_white", "count_female_black",
             "actual_gap", "invisibility_index", "invisibility_pct"]
        ]
        .to_dict(orient="records")
    )

    return {
        "first_year": first_year,
        "latest_year": latest_year,
        "statewide_latest": {
            "actual_gap": round(float(latest_state["actual_gap"]), 2),
            "naive_additive_gap": round(float(latest_state["naive_additive_gap"]), 2),
            "invisibility_index": round(float(latest_state["invisibility_index"]), 2),
            "invisibility_pct": round(float(latest_state["invisibility_pct"]), 1),
        },
        "statewide_first_year": {
            "actual_gap": round(float(first_state["actual_gap"]), 2),
            "naive_additive_gap": round(float(first_state["naive_additive_gap"]), 2),
            "invisibility_index": round(float(first_state["invisibility_index"]), 2),
            "invisibility_pct": round(float(first_state["invisibility_pct"]), 1),
        },
        "municipality_heterogeneity_latest_year": heterogeneity,
        "top_10_super_additive_municipalities_latest_year": top_super_additive,
        "top_10_sub_additive_municipalities_latest_year": top_sub_additive,
    }


def main() -> None:
    df = pd.read_csv(SOURCE_CSV)

    municipality_table = build_municipality_table(df)
    statewide_table = build_statewide_table(df)
    summary = build_summary(municipality_table, statewide_table)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    municipality_table.to_csv(OUT_DIR / "municipality_invisibility_index.csv", index=False)
    statewide_table.to_csv(OUT_DIR / "statewide_invisibility_index.csv", index=False)
    (OUT_DIR / "invisibility_index_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False)
    )

    print(f"Wrote {len(municipality_table)} municipality-year rows and "
          f"{len(statewide_table)} statewide-year rows to {OUT_DIR}")
    print(json.dumps(summary["statewide_latest"], indent=2))


if __name__ == "__main__":
    main()
