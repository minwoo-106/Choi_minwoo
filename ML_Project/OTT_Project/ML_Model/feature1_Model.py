import os

import joblib
import pandas as pd
import oracledb

oracledb.init_oracle_client(
    lib_dir=r"C:\oraclexe\app\oracle\product\11.2.0\server\bin"
)

DB_CONFIG = {
    "user": "scott",
    "password": "tiger",
    "dsn": "localhost:1521/xe",
}

TABLE_NAME = "F1_USER_DATASET"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "saved_models", "feature1_risk_model.pkl")


def load_model_bundle():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"모델 파일이 없습니다: {MODEL_PATH}")

    bundle = joblib.load(MODEL_PATH)
    model = bundle.get("model")
    feature_cols = bundle.get("feature_cols")
    model_name = bundle.get("model_name", "UNKNOWN")

    if model is None or feature_cols is None:
        raise ValueError("모델 파일 형식이 올바르지 않습니다.")

    return model, feature_cols, model_name


def load_user_data(user_seq: int, feature_cols: list[str]) -> pd.DataFrame:
    select_cols = ["USER_SEQ"] + feature_cols
    query = f"""
        SELECT {', '.join(select_cols)}
        FROM {TABLE_NAME}
        WHERE USER_SEQ = :user_seq
    """

    conn = None
    try:
        conn = oracledb.connect(**DB_CONFIG)
        return pd.read_sql(query, conn, params={"user_seq": user_seq})
    finally:
        if conn is not None:
            conn.close()


def risk_label_from_class(pred_class: int) -> str:
    return {0: "안정", 1: "주의", 2: "위험"}.get(pred_class, f"알 수 없음({pred_class})")


def predict_user(user_seq: int) -> None:
    model, feature_cols, model_name = load_model_bundle()
    df_user = load_user_data(user_seq, feature_cols)

    if df_user.empty:
        print(f"USER_SEQ {user_seq} 에 해당하는 데이터가 없습니다.")
        return

    X_user = df_user[feature_cols].copy()
    pred_class = int(model.predict(X_user)[0])
    pred_proba = model.predict_proba(X_user)[0]
    risk_label = risk_label_from_class(pred_class)
    confidence = pred_proba[pred_class] * 100

    print("\n" + "=" * 50)
    print("OTT 이탈 위험 예측 결과")
    print("=" * 50)
    print(f"모델명         : {model_name}")
    print(f"USER_SEQ       : {user_seq}")
    print(f"예측 클래스    : {pred_class}")
    print(f"예측 등급      : {risk_label}")
    print(f"예측 신뢰도    : {confidence:.2f}%")

    print("\n클래스별 확률")
    print(f"안정(0) : {pred_proba[0] * 100:.2f}%")
    print(f"주의(1) : {pred_proba[1] * 100:.2f}%")
    print(f"위험(2) : {pred_proba[2] * 100:.2f}%")


def main() -> None:
    try:
        user_seq = int(input("예측할 USER_SEQ를 입력하세요: ").strip())
        predict_user(user_seq)
    except ValueError:
        print("숫자만 입력하세요.")
    except Exception as e:
        print(f"오류 발생: {e}")


if __name__ == "__main__":
    main()
