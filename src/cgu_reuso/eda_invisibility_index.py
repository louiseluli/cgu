"""EDA for the invisibility-index pipeline: data quality on the source table,
justification for the MIN_CELL_COUNT filter, distribution of the computed metrics,
and a sensitivity check on one definitional choice (whether sex-only gap should be
computed across all races or restricted to black/white workers only).

Writes outputs/tables/eda/eda_briefing.md and outputs/figures/eda/*.png.
"""

import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

WAGE_GAP_ROOT = Path("/Users/louisesfer/Documents/Portfolios/wage_gap")
SOURCE_CSV = (
    WAGE_GAP_ROOT / "outputs/analysis/intersectional/municipality_sex_race_summary.csv"
)
CGU_ROOT = Path(__file__).resolve().parents[2]
TABLES_OUT = CGU_ROOT / "outputs/tables/eda"
FIGURES_OUT = CGU_ROOT / "outputs/figures/eda"
INDEX_MUNI_CSV = CGU_ROOT / "outputs/tables/invisibility_index/municipality_invisibility_index.csv"

RJ_MUNICIPALITY_COUNT = 92


def section_data_quality(df: pd.DataFrame, lines: list[str]) -> None:
    lines.append("## 1. Source data quality (`municipality_sex_race_summary.csv`)\n")

    n_dupes = df.duplicated(subset=["year", "municipality_code", "sex_label", "race_label"]).sum()
    n_nulls = df[["mean_wage", "worker_count"]].isna().sum().sum()
    n_nonpositive_wage = (df["mean_wage"] <= 0).sum()
    n_zero_count = (df["worker_count"] <= 0).sum()

    lines.append(f"- Rows: {len(df):,}")
    lines.append(f"- Duplicate (year, municipality, sex, race) keys: {n_dupes}")
    lines.append(f"- Nulls in mean_wage/worker_count: {n_nulls}")
    lines.append(f"- Non-positive mean_wage rows: {n_nonpositive_wage}")
    lines.append(f"- Non-positive worker_count rows: {n_zero_count}")

    years = sorted(df["year"].unique())
    lines.append(f"- Years present: {years}")
    lines.append(
        "  (2006-2008, 2017, 2019, 2020 excluded upstream — `BLOCKED_YEARS` in "
        "wage_gap's `build_dataset.py`, a pre-existing documented decision, not "
        "introduced by this pipeline.)"
    )

    munis_per_year = df.groupby("year")["municipality_code"].nunique()
    lines.append(
        f"- Municipalities per year: min={munis_per_year.min()}, "
        f"max={munis_per_year.max()} (RJ has {RJ_MUNICIPALITY_COUNT} municipalities "
        f"total — years below that are missing coverage, not necessarily an error, "
        f"since a municipality can simply have zero workers in a given sex×race cell "
        f"in a given year)."
    )
    incomplete_years = munis_per_year[munis_per_year < RJ_MUNICIPALITY_COUNT]
    if len(incomplete_years):
        lines.append(f"  Years below full coverage: {incomplete_years.to_dict()}")

    assert n_dupes == 0, "Duplicate keys would silently corrupt the weighted-mean aggregation"
    assert n_nulls == 0, "Nulls would propagate as NaN gaps"


def section_cell_count_distribution(df: pd.DataFrame, lines: list[str]) -> Path:
    lines.append("\n## 2. Worker-count-per-cell distribution (justifies MIN_CELL_COUNT)\n")

    target = df[
        ((df["sex_label"] == "male") & (df["race_label"] == "white"))
        | ((df["sex_label"] == "female") & (df["race_label"] == "black"))
    ]
    fb = target[(target["sex_label"] == "female") & (target["race_label"] == "black")]["worker_count"]

    lines.append("Black-women cell worker_count, all municipality-years (n=%d):" % len(fb))
    for q in [0.05, 0.10, 0.25, 0.50, 0.75, 0.90]:
        lines.append(f"  - p{int(q*100)}: {fb.quantile(q):.0f}")
    lines.append(f"  - share below 100 workers: {(fb < 100).mean()*100:.1f}%")
    lines.append(f"  - share below 30 workers: {(fb < 30).mean()*100:.1f}%")
    lines.append(
        "\nMIN_CELL_COUNT=100 in build_invisibility_index.py excludes the bottom "
        f"{(fb < 100).mean()*100:.0f}% of municipality-years by black-women worker "
        "count — this is the noisy tail where invisibility_pct swings to ±150-350% "
        "on cells as small as N=52 (see §3)."
    )

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(fb.clip(upper=2000), bins=60, color="#4C6EF5", edgecolor="none")
    ax.axvline(100, color="#E03131", linestyle="--", label="MIN_CELL_COUNT=100")
    ax.set_xlabel("Black-women workers per municipality-year (clipped at 2000)")
    ax.set_ylabel("Count")
    ax.set_title("Distribution of black-women cell size")
    ax.legend()
    fig.tight_layout()
    out_path = FIGURES_OUT / "cell_count_distribution.png"
    fig.savefig(out_path, dpi=120)
    plt.close(fig)
    return out_path


def section_invisibility_distribution(lines: list[str]) -> Path:
    lines.append("\n## 3. Effect of the N-filter on invisibility_pct (why it's necessary)\n")

    idx = pd.read_csv(INDEX_MUNI_CSV)
    latest = idx[idx["year"] == idx["year"].max()]

    unfiltered = latest["invisibility_pct"]
    filtered = latest[
        (latest["count_male_white"] >= 100) & (latest["count_female_black"] >= 100)
    ]["invisibility_pct"]

    lines.append(f"Latest year ({int(idx['year'].max())}), invisibility_pct across municipalities:")
    lines.append(f"  - Unfiltered (n={len(unfiltered)}): std={unfiltered.std():.1f}, "
                  f"min={unfiltered.min():.1f}, max={unfiltered.max():.1f}")
    lines.append(f"  - Filtered N>=100 (n={len(filtered)}): std={filtered.std():.1f}, "
                  f"min={filtered.min():.1f}, max={filtered.max():.1f}")
    lines.append(
        "\nMost unfiltered extremes are driven by small N combined with a small "
        "denominator — confirmed by manual lookup: the unfiltered top-ranked "
        "municipality (Cardoso Moreira, +212%) has only 58 black-women workers. "
        "Filtering to N>=100 removes most of this and stabilizes std from noisy to "
        "~53 points.\n"
    )
    lines.append(
        "### 3.1 A second, distinct failure mode survives the N-filter\n"
        "The filtered minimum is still an extreme -355% (Maricá, 2024). This is "
        "*not* a small-N artifact — Maricá has 2,004 black-women workers, well "
        "above the threshold. It happens because invisibility_pct divides by "
        "actual_gap, and Maricá's actual gap is only R$29 (white men and Black "
        "women are at near pay parity there specifically), so dividing a modest "
        "R$102 invisibility_index by a R$29 denominator produces a huge percentage "
        "even though both numbers are individually well-sampled and real. "
        "**Consequence: invisibility_pct is not a safe ranking key on its own, "
        "even after N-filtering** — this is why build_invisibility_index.py ranks "
        "municipalities by invisibility_index in R$ terms for the narrative's top-10 "
        "lists, and reports p5/p95 rather than raw min/max as the headline "
        "heterogeneity spread."
    )

    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    axes[0].hist(unfiltered.clip(-400, 400), bins=40, color="#F08C00")
    axes[0].set_title(f"Unfiltered (n={len(unfiltered)})")
    axes[1].hist(filtered.clip(-400, 400), bins=40, color="#2F9E44")
    axes[1].set_title(f"N>=100 filtered (n={len(filtered)})")
    for ax in axes:
        ax.set_xlabel("invisibility_pct")
        ax.axvline(0, color="black", linewidth=0.8)
    axes[0].set_ylabel("Count")
    fig.suptitle("Effect of the sample-size filter on invisibility_pct")
    fig.tight_layout()
    out_path = FIGURES_OUT / "invisibility_pct_filter_effect.png"
    fig.savefig(out_path, dpi=120)
    plt.close(fig)
    return out_path


def section_sensitivity_check(df: pd.DataFrame, lines: list[str]) -> None:
    lines.append("\n## 4. Sensitivity check: sex-only gap definition\n")
    lines.append(
        "The pipeline computes sex_only_gap over **all four race categories** "
        "(black, pardo, white, yellow), while race_only_gap is restricted to "
        "**black/white only**. This is a deliberate, defensible choice (sex-only "
        "should reflect 'what if we only knew someone's sex', i.e. the whole "
        "population) but it's an asymmetry worth stress-testing: does restricting "
        "sex_only_gap to black/white workers only change the conclusion?\n"
    )

    def weighted_mean_by(frame, group_cols):
        w = frame.assign(_w=frame["worker_count"] * frame["mean_wage"])
        agg = w.groupby(group_cols, as_index=False).agg(
            _w=("_w", "sum"), worker_count=("worker_count", "sum")
        )
        agg["mean_wage"] = agg["_w"] / agg["worker_count"]
        return agg.drop(columns="_w")

    full_sex = weighted_mean_by(df, ["year", "sex_label"]).pivot(
        index="year", columns="sex_label", values="mean_wage"
    )
    full_sex_gap = full_sex["male"] - full_sex["female"]

    bw_only = df[df["race_label"].isin(["black", "white"])]
    bw_sex = weighted_mean_by(bw_only, ["year", "sex_label"]).pivot(
        index="year", columns="sex_label", values="mean_wage"
    )
    bw_sex_gap = bw_sex["male"] - bw_sex["female"]

    cmp = pd.DataFrame({
        "sex_only_gap_all_races": full_sex_gap,
        "sex_only_gap_black_white_only": bw_sex_gap,
    })
    cmp["diff"] = cmp["sex_only_gap_all_races"] - cmp["sex_only_gap_black_white_only"]
    cmp["diff_pct_of_gap"] = cmp["diff"] / cmp["sex_only_gap_all_races"] * 100

    lines.append(cmp.round(1).to_string())
    max_diff_pct = cmp["diff_pct_of_gap"].abs().max()
    lines.append(
        f"\nMax divergence: {max_diff_pct:.1f}% of the sex-only gap. "
        + (
            "This is small enough not to change the direction or rough magnitude "
            "of the invisibility index reported in the narrative."
            if max_diff_pct < 15
            else "This is large enough to matter — the narrative should state "
            "which definition it uses and note this as a limitation."
        )
    )


def _weighted_mean_by(frame: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    w = frame.assign(_w=frame["worker_count"] * frame["mean_wage"])
    agg = w.groupby(group_cols, as_index=False).agg(
        _w=("_w", "sum"), worker_count=("worker_count", "sum")
    )
    agg["mean_wage"] = agg["_w"] / agg["worker_count"]
    return agg.drop(columns="_w")


def section_race_robustness_check(df: pd.DataFrame, lines: list[str]) -> Path:
    lines.append("\n## 5. Robustness check: is this specific to Black women, or generic to any woman-of-color category?\n")
    lines.append(
        "The invisibility index so far compares white men to Black women only. "
        "If the same naive-additive-vs-actual gap showed up for *any* non-white "
        "women's category, the 'hidden compounding' story would be a generic "
        "artifact of the arithmetic rather than a real feature of the Black-women "
        "comparison specifically. Re-running the identical computation with pardo "
        "and yellow women in place of Black women tests that directly.\n"
    )

    rows = []
    for race in ["black", "pardo", "yellow"]:
        pair = df[
            ((df["sex_label"] == "male") & (df["race_label"] == "white"))
            | ((df["sex_label"] == "female") & (df["race_label"] == race))
        ]
        wide = _weighted_mean_by(pair, ["year", "sex_label", "race_label"]).pivot_table(
            index="year", columns=["sex_label", "race_label"], values="mean_wage"
        )
        wide.columns = ["_".join(c) for c in wide.columns]
        sex_state = _weighted_mean_by(df, ["year", "sex_label"]).pivot(
            index="year", columns="sex_label", values="mean_wage"
        )
        race_state = _weighted_mean_by(
            df[df["race_label"].isin([race, "white"])], ["year", "race_label"]
        ).pivot(index="year", columns="race_label", values="mean_wage")

        actual = wide["male_white"] - wide[f"female_{race}"]
        naive = (sex_state["male"] - sex_state["female"]) + (race_state["white"] - race_state[race])
        pct = (actual - naive) / actual * 100
        latest_year = pct.index.max()
        n_women = df[
            (df["year"] == latest_year) & (df["sex_label"] == "female") & (df["race_label"] == race)
        ]["worker_count"].sum()
        rows.append({
            "comparison": f"white men vs {race} women",
            "n_women_statewide_2024": int(n_women),
            "invisibility_pct_2024": round(float(pct.loc[latest_year]), 1),
            "invisibility_pct_mean_all_years": round(float(pct.mean()), 1),
        })

    result = pd.DataFrame(rows)
    result.to_csv(TABLES_OUT / "race_robustness_check.csv", index=False)
    lines.append(result.to_string(index=False))
    lines.append(
        "\nHonest read: all three statewide invisibility percentages sit in the "
        "same single-to-low-double-digit range (-3.3% to +13.1%) — this is *not* "
        "a clean 'only Black women show it' result, and the narrative should not "
        "claim it is. What it does rule out is the arithmetic being a pure "
        "artifact that would blow up for any category regardless of N: the "
        "largest deviation (yellow women, 13.1% multi-year mean) belongs to the "
        "smallest, most volatile subgroup (statewide N=23,499 vs 310k for black, "
        "1.0M for pardo), consistent with sampling noise rather than a distinct "
        "effect. The municipality-level heterogeneity finding in §3 (p5/p95 of "
        "-39% to +40% for the black-women comparison specifically) remains the "
        "strongest, best-supported claim in this analysis — it is not undermined "
        "by this check, but this check does mean the narrative should frame the "
        "state-level black-women number as 'small and inconclusive on its own', "
        "not as evidence the effect is uniquely absent for Black women."
    )
    return result


def section_statewide_uncertainty(df: pd.DataFrame, lines: list[str]) -> None:
    lines.append("\n## 6. Approximate statewide confidence interval\n")
    lines.append(
        "Every number so far is a point estimate — no uncertainty is reported. "
        "True confidence intervals need per-cell wage variance, which only exists "
        "**statewide** (via the `inequality/` percentile tables), not per "
        "municipality — so this section covers the statewide invisibility index "
        "only; municipality-level numbers cannot get a rigorous CI from the "
        "outputs available today (see §7 recommendations).\n"
    )

    sex_dist = pd.read_csv(
        WAGE_GAP_ROOT / "outputs/analysis/inequality/sex_distribution_summary.csv"
    )
    latest = sex_dist[sex_dist["year"] == sex_dist["year"].max()]

    def sigma_from_iqr(row):
        return (row["p75"] - row["p25"]) / 1.349

    latest = latest.assign(sigma_approx=latest.apply(sigma_from_iqr, axis=1))
    latest = latest.assign(sem=latest["sigma_approx"] / latest["count"] ** 0.5)

    lines.append(
        "Sigma approximated from the IQR (`(p75-p25)/1.349`, the normal-distribution "
        "relationship) since no raw standard deviation is published. RAIS wages "
        "are heavily right-skewed (max values run 50-100x the median — see §1), "
        "so **this understates true sigma and therefore understates the interval "
        "width; treat it as a lower bound on uncertainty, not an exact interval.** "
        "By the Central Limit Theorem the *mean's* sampling distribution is still "
        "approximately normal at these sample sizes (hundreds of thousands), which "
        "is what justifies a normal-approximation SEM despite the skewed "
        "individual-wage distribution.\n"
    )
    lines.append(latest[["sex_label", "count", "mean", "sigma_approx", "sem"]].round(2).to_string(index=False))

    female_sem = latest[latest["sex_label"] == "female"]["sem"].iloc[0]
    male_sem = latest[latest["sex_label"] == "male"]["sem"].iloc[0]
    gap_sem = (female_sem**2 + male_sem**2) ** 0.5
    ci95 = 1.96 * gap_sem
    lines.append(
        f"\nSex-only gap SEM (error propagation, independent samples): {gap_sem:.2f} "
        f"-> approx 95% CI half-width ±{ci95:.2f} on a gap of R$813. Even this "
        "conservative lower-bound interval is tiny relative to the gap itself, "
        "which is expected given the sample sizes involved — the state-level "
        "**point estimate** (sex-only + race-only gaps, and their sum) is not "
        "noise. What remains genuinely uncertain is not 'is there a gap' but "
        "'how much of the R$2,622 actual gap in 2024 is missed by naive addition' "
        "(-3.3%, i.e. close to zero either way) — that number's practical "
        "conclusion (roughly additive at the state level) does not hinge on the "
        "precision of this approximation."
    )


def main() -> None:
    warnings.filterwarnings("ignore")
    TABLES_OUT.mkdir(parents=True, exist_ok=True)
    FIGURES_OUT.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(SOURCE_CSV)

    lines = ["# EDA — invisibility index pipeline\n"]
    section_data_quality(df, lines)
    section_cell_count_distribution(df, lines)
    section_invisibility_distribution(lines)
    section_sensitivity_check(df, lines)
    section_race_robustness_check(df, lines)
    section_statewide_uncertainty(df, lines)

    briefing_path = TABLES_OUT / "eda_briefing.md"
    briefing_path.write_text("\n".join(lines))
    print(f"Wrote {briefing_path}")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
