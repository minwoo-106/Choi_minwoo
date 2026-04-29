import warnings

import pandas as pd

from utils.code_meanings import CODE_MEANINGS
from utils.predictor import PredictionError, TABLE_NAME, _connect_oracle, load_model_bundle

warnings.filterwarnings("ignore")


class ChartDataError(Exception):
    pass


FEATURE_COLS = [
    "USER_SEQ",
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


def _decode(field, value):
    sections = [
        CODE_MEANINGS.get("users", {}),
        CODE_MEANINGS.get("economy", {}),
        CODE_MEANINGS.get("subscription", {}),
        CODE_MEANINGS.get("usage_behavior", {}),
    ]
    for section in sections:
        if field in section:
            return section[field].get(int(value), str(value))
    return str(value)


def _load_frame():
    query = f"SELECT {', '.join(FEATURE_COLS)} FROM {TABLE_NAME}"
    conn = None
    try:
        conn = _connect_oracle()
        df = pd.read_sql(query, conn)
        if df.empty:
            raise ChartDataError("차트로 표시할 데이터가 없습니다.")
        return df
    except PredictionError as exc:
        raise ChartDataError(str(exc)) from exc
    except Exception as exc:
        raise ChartDataError(f"차트 데이터를 불러오지 못했습니다: {exc}") from exc
    finally:
        if conn is not None:
            conn.close()


def _distribution(df, column, top_n=None):
    series = df[column].dropna().astype(int).map(lambda value: _decode(column, value))
    counts = series.value_counts()
    if top_n is not None:
        counts = counts.head(top_n)
    return {"labels": counts.index.tolist(), "values": counts.values.tolist()}


def get_dashboard_data():
    df = _load_frame()
    model, feature_cols, _ = load_model_bundle()

    x = df[feature_cols].copy()
    pred = pd.Series(model.predict(x), name="PRED")
    risk_map = {0: "안정", 1: "주의", 2: "위험"}
    risk_counts = pred.map(risk_map).value_counts().reindex(["안정", "주의", "위험"], fill_value=0)

    return {
        "summary": {
            "total_members": int(len(df)),
            "stable_members": int(risk_counts.get("안정", 0)),
            "caution_members": int(risk_counts.get("주의", 0)),
            "risk_members": int(risk_counts.get("위험", 0)),
        },
        "risk_distribution": {
            "labels": risk_counts.index.tolist(),
            "values": risk_counts.values.tolist(),
        },
        "age_distribution": _distribution(df, "AGE_GROUP"),
        "frequency_distribution": _distribution(df, "USE_FREQUENCY"),
        "fee_distribution": _distribution(df, "MONTHLY_FEE_CODE"),
    }
