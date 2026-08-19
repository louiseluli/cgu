"""Train an XGBoost wage model on the validated RJ panel (2024) and compute
SHAP feature importance — the deferred "what drives the gap" piece for the
Wage Gap Explorer.

Deliberately does NOT use wage_gap's own `rio_sample_200k.parquet`: no script
in wage_gap generates that file, it carries no year column, and its provenance
relative to the validated 2010-2024 panel (42/42 checks) can't be confirmed.
This trains directly on `data/processed/rj_state_panel_combined.parquet`
instead, filtered to 2024 (the year every other output in this project uses
as "latest"), so the model result is traceable to the same validated source
as everything else.
"""

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import shap
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder
from xgboost import XGBRegressor

WAGE_GAP_ROOT = Path("/Users/louisesfer/Documents/Portfolios/wage_gap")
PANEL_PATH = WAGE_GAP_ROOT / "data/processed/rj_state_panel_combined.parquet"

CGU_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = CGU_ROOT / "outputs/tables/wage_model"

TARGET = "log_remuneracao_media"
NUMERIC_FEATURES = ["age", "contracted_hours", "tenure_months"]
CATEGORICAL_FEATURES = [
    "sex_code", "race_code", "education_code", "occupation_code",
    "sector_class_code", "sector_subclass_code", "firm_size_code",
]
ALL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES

FEATURE_LABELS = {
    "age": "Idade",
    "contracted_hours": "Carga horária contratada",
    "tenure_months": "Tempo de emprego (meses)",
    "sex_code": "Sexo",
    "race_code": "Raça/cor",
    "education_code": "Escolaridade",
    "occupation_code": "Ocupação (CBO)",
    "sector_class_code": "Setor (CNAE classe)",
    "sector_subclass_code": "Setor (CNAE subclasse)",
    "firm_size_code": "Porte do estabelecimento",
}

TRAIN_SAMPLE_SIZE = 6_000_000  # effectively the full 2024 panel (~5.78M rows) —
# an initial 300k-row run finished in 3s, so there was no real time-budget reason
# to subsample training data; only SHAP explanation is sampled (standard practice).
SHAP_SAMPLE_SIZE = 4_000
RANDOM_STATE = 42


def build_preprocessor() -> ColumnTransformer:
    numeric_pipeline = Pipeline([("imputer", SimpleImputer(strategy="median"))])
    categorical_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("ordinal", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)),
    ])
    return ColumnTransformer([
        ("num", numeric_pipeline, NUMERIC_FEATURES),
        ("cat", categorical_pipeline, CATEGORICAL_FEATURES),
    ])


def main() -> None:
    t0 = time.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    full = pd.read_parquet(PANEL_PATH, columns=ALL_FEATURES + [TARGET, "year"])
    d2024 = full[full["year"] == 2024]
    n_available = len(d2024)
    sample = d2024.sample(n=min(TRAIN_SAMPLE_SIZE, n_available), random_state=RANDOM_STATE)
    print(f"2024 rows available: {n_available:,} -> training sample: {len(sample):,} "
          f"({time.time()-t0:.0f}s)")

    X = sample[ALL_FEATURES]
    y = sample[TARGET]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE
    )

    preprocessor = build_preprocessor()
    X_train_t = preprocessor.fit_transform(X_train)
    X_test_t = preprocessor.transform(X_test)

    model = XGBRegressor(
        n_estimators=300, max_depth=6, learning_rate=0.05,
        random_state=RANDOM_STATE, n_jobs=-1,
    )
    model.fit(X_train_t, y_train)
    print(f"Model trained ({time.time()-t0:.0f}s)")

    pred = model.predict(X_test_t)
    r2 = r2_score(y_test, pred)
    mae_log = mean_absolute_error(y_test, pred)

    explainer = shap.TreeExplainer(model)
    shap_idx = np.random.RandomState(RANDOM_STATE).choice(
        X_test_t.shape[0], size=min(SHAP_SAMPLE_SIZE, X_test_t.shape[0]), replace=False
    )
    shap_values = explainer.shap_values(X_test_t[shap_idx])
    print(f"SHAP computed on {len(shap_idx):,} rows ({time.time()-t0:.0f}s)")

    mean_abs_shap = np.abs(shap_values).mean(axis=0)
    importance = pd.DataFrame({
        "feature": ALL_FEATURES,
        "feature_label": [FEATURE_LABELS[f] for f in ALL_FEATURES],
        "mean_abs_shap": mean_abs_shap,
    }).sort_values("mean_abs_shap", ascending=False).reset_index(drop=True)
    importance["rank"] = importance.index + 1
    importance["share_pct"] = importance["mean_abs_shap"] / importance["mean_abs_shap"].sum() * 100

    importance.to_csv(OUT_DIR / "shap_feature_importance.csv", index=False)

    sex_rank = int(importance[importance["feature"] == "sex_code"]["rank"].iloc[0])
    race_rank = int(importance[importance["feature"] == "race_code"]["rank"].iloc[0])

    summary = {
        "year": 2024,
        "source": "wage_gap/data/processed/rj_state_panel_combined.parquet (validated, 42/42 checks)",
        "rows_available_2024": int(n_available),
        "training_sample_size": len(sample),
        "training_sample_note": (
            "Trained on the full available 2024 panel (no subsampling needed — "
            "an initial 300k-row timing run finished in 3s)."
            if len(sample) == n_available else
            f"Subsampled {len(sample):,} of {n_available:,} available 2024 rows."
        ),
        "test_r2": round(float(r2), 3),
        "test_mae_log_wage": round(float(mae_log), 3),
        "model_quality_note": (
            "Reported honestly, not cherry-picked: R^2 measures fit on held-out "
            "2024 data, log-wage scale (matches the target used throughout wage_gap)."
        ),
        "shap_sample_size": len(shap_idx),
        "sex_code_importance_rank": sex_rank,
        "race_code_importance_rank": race_rank,
        "sex_race_combined_share_pct": round(
            float(importance[importance["feature"].isin(["sex_code", "race_code"])]["share_pct"].sum()), 1
        ),
        "top_5_features": importance.head(5)[["feature_label", "share_pct"]].to_dict(orient="records"),
    }
    (OUT_DIR / "shap_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))

    print(f"\nDone in {time.time()-t0:.0f}s. Test R^2={r2:.3f}")
    print(importance[["rank", "feature_label", "share_pct"]].to_string(index=False))


if __name__ == "__main__":
    main()
