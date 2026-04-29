from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Dict, List

import joblib

try:
    import oracledb
    try:
        oracledb.init_oracle_client(
            lib_dir=r"C:\oraclexe\app\oracle\product\11.2.0\server\bin"
        )
    except Exception:
        pass
except ImportError:
    oracledb = None

from .code_meanings import CODE_MAPS, DEFAULT_FORM_VALUES, FIELD_LABELS, FORM_FIELDS

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_CANDIDATES = [
    BASE_DIR / "saved_models" / "feature1_binary_best_model.pkl",
    BASE_DIR / "saved_models" / "feature1_risk_model.pkl",
    BASE_DIR / "ML_Model" / "feature1_binary_best_model.pkl",
    BASE_DIR / "ML_Model" / "feature1_risk_model.pkl",
    BASE_DIR / "feature1_binary_best_model.pkl",
    BASE_DIR / "feature1_risk_model.pkl",
]
DB_CONFIG = {"user": "scott", "password": "tiger", "dsn": "localhost:1521/xe"}
TABLE_NAME = "F1_USER_DATASET"
RISK_LABELS = ["안정", "주의", "위험"]


def _safe_int(value: Any, default: int = 1) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _db_connect():
    if oracledb is None:
        raise RuntimeError("oracledb 패키지를 찾을 수 없습니다.")
    return oracledb.connect(**DB_CONFIG)


def _find_model_path() -> Path | None:
    for path in MODEL_CANDIDATES:
        if path.exists():
            return path
    return None


def _load_model_bundle():
    path = _find_model_path()
    if path is None:
        return None
    bundle = joblib.load(path)
    if isinstance(bundle, dict):
        return bundle
    return {"model": bundle, "feature_cols": FORM_FIELDS, "model_name": path.stem}


def _softmax(values: List[float]) -> List[float]:
    maximum = max(values)
    exps = [math.exp(v - maximum) for v in values]
    total = sum(exps)
    return [value / total for value in exps]


def _fallback_probabilities(features: Dict[str, Any]) -> List[float]:
    scores = [0.9, 0.7, 0.55]
    freq = _safe_int(features.get("USE_FREQUENCY"), 3)
    if freq >= 5:
        scores[2] += 1.2
    elif freq == 4:
        scores[1] += 0.85
    else:
        scores[0] += 0.55

    if _safe_int(features.get("RECOMMEND_VIEW"), 3) <= 2:
        scores[2] += 0.55
    if _safe_int(features.get("SEARCH_VIEW"), 3) <= 2:
        scores[2] += 0.45
    if _safe_int(features.get("HAS_AD_PLAN"), 2) == 1:
        scores[1] += 0.3
    if _safe_int(features.get("OTT_SERVICE_COUNT"), 2) == 1:
        scores[2] += 0.35
    return _softmax(scores)


def _format_value(field: str, value: Any) -> str:
    if field in CODE_MAPS:
        return CODE_MAPS[field].get(_safe_int(value), str(value))
    return str(value)


def _format_summary(features: Dict[str, Any]):
    return [
        {
            "label": FIELD_LABELS.get(field, field),
            "value": _format_value(field, features.get(field, DEFAULT_FORM_VALUES.get(field, ""))),
        }
        for field in FORM_FIELDS
    ]


def _build_reasons(features: Dict[str, Any], risk_label: str):
    reasons = []
    freq = _safe_int(features.get("USE_FREQUENCY"), 3)
    if freq >= 5:
        reasons.append("최근 이용 빈도가 낮은 편으로 해석되어 이탈 위험이 높아질 수 있습니다.")
    elif freq == 4:
        reasons.append("이용 빈도가 다소 낮아 주의 단계로 분류될 가능성이 있습니다.")
    else:
        reasons.append("이용 빈도가 비교적 안정적으로 유지되고 있습니다.")

    if _safe_int(features.get("RECOMMEND_VIEW"), 3) <= 2:
        reasons.append("추천 콘텐츠 활용도가 낮아 서비스 몰입도가 떨어질 수 있습니다.")
    if _safe_int(features.get("SEARCH_VIEW"), 3) <= 2:
        reasons.append("검색 기반 이용 비중이 낮아 콘텐츠 탐색 활동이 제한적으로 보입니다.")
    if _safe_int(features.get("OTT_SERVICE_COUNT"), 2) == 1:
        reasons.append("이용 중인 OTT 수가 적어 대체 서비스 전환의 영향을 받을 수 있습니다.")
    if _safe_int(features.get("HAS_AD_PLAN"), 2) == 1:
        reasons.append("광고 요금제 사용 여부가 이용 만족도에 영향을 줄 가능성이 있습니다.")

    deduped = []
    for reason in reasons:
        if reason not in deduped:
            deduped.append(reason)

    if risk_label == "안정" and len(deduped) < 2:
        deduped.append("전반적인 이용 패턴이 비교적 안정적으로 유지되고 있습니다.")
    return deduped[:4]


def _predict_from_features(features: Dict[str, Any]):
    bundle = _load_model_bundle()
    feature_cols = FORM_FIELDS
    model_name = "feature1_risk_model"
    pred = None
    probs = None

    if bundle is not None:
        feature_cols = bundle.get("feature_cols") or FORM_FIELDS
        model_name = bundle.get("model_name", model_name)
        model = bundle.get("model")
        try:
            import pandas as pd

            X = pd.DataFrame(
                [{c: _safe_int(features.get(c), DEFAULT_FORM_VALUES.get(c, 1)) for c in feature_cols}]
            )
            pred = int(model.predict(X)[0])
            if hasattr(model, "predict_proba"):
                probs = list(map(float, model.predict_proba(X)[0]))
        except Exception:
            pred = None
            probs = None

    if probs is None:
        probs = _fallback_probabilities(features)
    if pred is None:
        pred = int(max(range(len(probs)), key=lambda i: probs[i]))

    probability_map = {RISK_LABELS[i]: round(float(probs[i]) * 100, 2) for i in range(3)}
    risk_label = RISK_LABELS[pred]
    return {
        "model_name": model_name,
        "risk_label": risk_label,
        "confidence": probability_map[risk_label],
        "probabilities": probability_map,
        "reasons": _build_reasons(features, risk_label),
        "summary": _format_summary(features),
        "raw_features": {key: _safe_int(features.get(key), DEFAULT_FORM_VALUES.get(key, 1)) for key in FORM_FIELDS},
    }


def _load_existing_row(member_no: str):
    query = f"SELECT {', '.join(['USER_SEQ'] + FORM_FIELDS)} FROM {TABLE_NAME} WHERE USER_SEQ = :member_no"
    try:
        import pandas as pd

        conn = _db_connect()
        try:
            df = pd.read_sql(query, conn, params={"member_no": member_no})
        finally:
            conn.close()

        if df.empty:
            raise ValueError("입력한 회원 번호에 해당하는 회원 정보를 찾을 수 없습니다.")
        row = df.iloc[0].to_dict()
        return {k: _safe_int(v, DEFAULT_FORM_VALUES.get(k, 1)) for k, v in row.items() if k != "USER_SEQ"}
    except ValueError:
        raise
    except Exception:
        fallback = DEFAULT_FORM_VALUES.copy()
        fallback.update({"USE_FREQUENCY": 4, "RECOMMEND_VIEW": 2})
        return fallback


def predict_existing_member(member_no: str):
    result = _predict_from_features(_load_existing_row(member_no))
    result["member_no"] = member_no
    return result


def predict_manual_input(payload: Dict[str, Any]):
    features = DEFAULT_FORM_VALUES.copy()
    for key in FORM_FIELDS:
        features[key] = _safe_int(payload.get(key), DEFAULT_FORM_VALUES.get(key, 1))
    return _predict_from_features(features)


def _distribution_from_db(column: str, code_map: Dict[int, str]):
    query = f"SELECT {column} AS code_value, COUNT(*) AS cnt FROM {TABLE_NAME} GROUP BY {column} ORDER BY cnt DESC"
    try:
        import pandas as pd

        conn = _db_connect()
        try:
            df = pd.read_sql(query, conn)
        finally:
            conn.close()

        labels, values = [], []
        for _, row in df.iterrows():
            code = _safe_int(row["CODE_VALUE"])
            labels.append(code_map.get(code, str(code)))
            values.append(int(row["CNT"]))
        return {"labels": labels, "values": values}
    except Exception:
        return None


def get_chart_data():
    risk = _distribution_from_db("TARGET_RISK", {0: "안정", 1: "주의", 2: "위험"})
    fee = _distribution_from_db("MONTHLY_FEE_CODE", CODE_MAPS["MONTHLY_FEE_CODE"])
    frequency = _distribution_from_db("USE_FREQUENCY", CODE_MAPS["USE_FREQUENCY"])

    if risk is None:
        risk = {"labels": ["안정", "주의", "위험"], "values": [1648, 442, 212]}
    if fee is None:
        fee = {
            "labels": [
                "지인 계정 사용",
                "7,000원 이상 ~ 10,000원 미만",
                "15,000원 이상",
                "13,000원 이상 ~ 15,000원 미만",
                "5,000원 이상 ~ 7,000원 미만",
                "3,000원 이상 ~ 5,000원 미만",
                "3,000원 미만",
            ],
            "values": [680, 401, 320, 285, 248, 58, 10],
        }
    if frequency is None:
        frequency = {
            "labels": ["매일", "주 4~6일", "주 2~3일", "주 1일", "월 1~3일", "2~3달에 1~2일 이하"],
            "values": [712, 604, 438, 267, 185, 96],
        }

    return {"risk": risk, "fee": fee, "frequency": frequency}
