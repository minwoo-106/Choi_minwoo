import os

import joblib
import pandas as pd
import oracledb
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, balanced_accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

oracledb.init_oracle_client(
    lib_dir=r"C:\oraclexe\app\oracle\product\11.2.0\server\bin"
)

DB_CONFIG = {
    "user": "scott",
    "password": "tiger",
    "dsn": "localhost:1521/xe",
}

TABLE_NAME = "F1_USER_DATASET"
TARGET_COL = "TARGET_RISK"
MODEL_NAME = "SAFE+USE_FREQUENCY"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "saved_models")
MODEL_PATH = os.path.join(MODEL_DIR, "feature1_risk_model.pkl")

FEATURE_COLS = [
    "GENDER",
    "AGE_GROUP",
    "INCOME_GROUP",
    "FAMILY_TYPE",
    "MONTHLY_FEE_CODE",
    "HAS_AD_PLAN",
    "AD_INTENT",
    "WEEKDAY_TIME_CODE",
    "WEEKEND_TIME_CODE",
    "SEARCH_VIEW",
    "RECOMMEND_VIEW",
    "BINGE_WATCH",
    "DEVICE_COUNT",
    "OTT_SERVICE_COUNT",
    "CONTENT_TYPE_COUNT",
    "BROADCAST_TYPE_COUNT",
    "USE_FREQUENCY",
]

SELECT_COLS = FEATURE_COLS + [TARGET_COL]


def load_data() -> pd.DataFrame:
    query = f"SELECT {', '.join(SELECT_COLS)} FROM {TABLE_NAME}"
    conn = None
    try:
        conn = oracledb.connect(**DB_CONFIG)
        return pd.read_sql(query, conn)
    finally:
        if conn is not None:
            conn.close()


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna(subset=[TARGET_COL]).copy()
    df[TARGET_COL] = df[TARGET_COL].astype(int)
    return df


def build_model() -> Pipeline:
    return Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            (
                "model",
                ExtraTreesClassifier(
                    n_estimators=300,
                    max_depth=12,
                    min_samples_split=5,
                    min_samples_leaf=2,
                    class_weight="balanced",
                    random_state=42,
                    n_jobs=-1,
                ),
            ),
        ]
    )


def evaluate_model(model: Pipeline, X_test: pd.DataFrame, y_test: pd.Series) -> None:
    y_pred = model.predict(X_test)

    print("\n" + "=" * 60)
    print("테스트 성능")
    print("=" * 60)
    print(f"accuracy          : {accuracy_score(y_test, y_pred):.4f}")
    print(f"balanced_accuracy : {balanced_accuracy_score(y_test, y_pred):.4f}")

    print("\nConfusion Matrix")
    print(confusion_matrix(y_test, y_pred))

    print("\nClassification Report")
    print(
        classification_report(
            y_test,
            y_pred,
            digits=4,
            zero_division=0,
            target_names=["안정(0)", "주의(1)", "위험(2)"],
        )
    )


def save_model(model: Pipeline) -> None:
    os.makedirs(MODEL_DIR, exist_ok=True)

    bundle = {
        "model": model,
        "feature_cols": FEATURE_COLS,
        "model_name": MODEL_NAME,
    }
    joblib.dump(bundle, MODEL_PATH)

    print("\n모델 저장 완료")
    print(f"저장 경로 : {MODEL_PATH}")
    print(f"모델 이름 : {MODEL_NAME}")


def main() -> None:
    print("데이터 로딩 중...")
    df = preprocess(load_data())

    X = df[FEATURE_COLS].copy()
    y = df[TARGET_COL].copy()

    print(f"전체 데이터 수 : {len(df)}")
    print(f"사용 피처 수   : {len(FEATURE_COLS)}")
    print(f"타깃 분포\n{y.value_counts().sort_index()}")

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    model = build_model()

    print("\n학습 시작...")
    model.fit(X_train, y_train)
    print("학습 완료")

    evaluate_model(model, X_test, y_test)
    save_model(model)


if __name__ == "__main__":
    main()
