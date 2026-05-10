import os
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score

# Encode helpers
PKG_MAP = {"simple": 1, "basic": 2, "luxury": 3}
LOC_MAP = {"rural": 1, "tier2": 2, "metro": 3, "premium": 4}

DATASETS = {
    "wedding": "wedding_dataset.csv",
    "birthday_private_party": "birthday_private_party_dataset.csv",
    "corporate_event": "corporate_event_dataset.csv",
    "engagement_reception": "engagement_reception_dataset.csv",
}

# ✅ IMPORTANT: keep same order everywhere (train + backend)
ALL_SERVICE_IDS = [
    "bridegroom", "haldi", "sangeeth", "mehendi",
    "wedding", "food", "band", "makeup", "photo"
]

def add_service_flags(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converts selected_services like 'food|photo|makeup' into 0/1 columns.
    """
    df = df.copy()
    if "selected_services" not in df.columns:
        df["selected_services"] = ""

    # safe string
    df["selected_services"] = df["selected_services"].fillna("").astype(str)

    def to_set(s: str):
        return set([x.strip() for x in s.split("|") if x.strip()])

    selected_sets = df["selected_services"].apply(to_set)

    for sid in ALL_SERVICE_IDS:
        df[sid] = selected_sets.apply(lambda st: 1 if sid in st else 0)

    return df

def prep(df: pd.DataFrame):
    df = df.copy()

    # ✅ required columns check (avoid silent errors)
    required = ["guests", "package", "location", "services_count", "total_budget"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing column in dataset: {col}")

    # ✅ map to numeric
    df["package"] = df["package"].map(PKG_MAP)
    df["location"] = df["location"].map(LOC_MAP)

    # If dataset has rule_total, use it; else create fallback rule_total=0
    if "rule_total" not in df.columns:
        df["rule_total"] = 0

    # Add flags from selected_services
    df = add_service_flags(df)

    # ✅ Fill any NaNs after mapping
    df["package"] = df["package"].fillna(1).astype(int)
    df["location"] = df["location"].fillna(2).astype(int)
    df["services_count"] = df["services_count"].fillna(0).astype(int)
    df["guests"] = df["guests"].fillna(0).astype(int)
    df["rule_total"] = df["rule_total"].fillna(0).astype(float)

    feature_cols = [
        "guests", "package", "location", "services_count", "rule_total",
        *ALL_SERVICE_IDS
    ]

    X = df[feature_cols]
    y = df["total_budget"].astype(float)

    return X, y, feature_cols

def train_one(event_key, csv_file):
    df = pd.read_csv(csv_file)

    X, y, feature_cols = prep(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(
        n_estimators=400,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)

    pred = model.predict(X_test)
    r2 = r2_score(y_test, pred)

    os.makedirs("models", exist_ok=True)
    out_path = os.path.join("models", f"{event_key}_budget_model.pkl")
    joblib.dump(model, out_path)

    # ✅ Save feature order also (so backend uses same order)
    feat_path = os.path.join("models", f"{event_key}_features.txt")
    with open(feat_path, "w", encoding="utf-8") as f:
        f.write("\n".join(feature_cols))

    print(f"✅ {event_key}: saved -> {out_path} | R2={r2:.3f}")
    print(f"   Features saved -> {feat_path}")

def main():
    for k, f in DATASETS.items():
        if not os.path.exists(f):
            print(f"❌ Missing dataset file: {f}")
            continue
        train_one(k, f)

if __name__ == "__main__":
    main()
