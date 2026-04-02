import os
import warnings
import joblib
import pandas as pd

from utils.code_meanings import CODE_MEANINGS

warnings.filterwarnings("ignore")

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

class PredictionError(Exception):
    pass

DB_CONFIG = {
    "user": "scott",
    "password": "tiger",
    "dsn": "localhost:1521/xe",
}

TABLE_NAME = "F1_USER_DATASET"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH_CANDIDATES = [
    os.path.join(BASE_DIR, "..", "saved_models", "feature1_risk_model.pkl"),
    os.path.join(BASE_DIR, "..", "..", "saved_models", "feature1_risk_model.pkl"),
    os.path.join(BASE_DIR, "..", "..", "ML_Model", "feature1_risk_model.pkl"),
]

RAW_COLS = [
    "USER_SEQ",
    "GENDER",
    "AGE_GROUP",
    "INCOME_GROUP",
    "FAMILY_TYPE",
    "MONTHLY_FEE_CODE",
    "HAS_AD_PLAN",
    "AD_INTENT",
    "USE_FREQUENCY",
    "WEEKDAY_TIME_CODE",
    "WEEKEND_TIME_CODE",
    "SEARCH_VIEW",
    "RECOMMEND_VIEW",
    "BINGE_WATCH",
    "DEVICE_COUNT",
    "OTT_SERVICE_COUNT",
    "CONTENT_TYPE_COUNT",
    "BROADCAST_TYPE_COUNT",
]

KOREAN_LABELS = {
    "GENDER": "성별",
    "AGE_GROUP": "연령대",
    "INCOME_GROUP": "월 소득 구간",
    "FAMILY_TYPE": "가구 형태",
    "MONTHLY_FEE_CODE": "월 결제액 구간",
    "HAS_AD_PLAN": "광고형 요금제 이용 여부",
    "AD_INTENT": "광고형 요금제 의향",
    "USE_FREQUENCY": "이용 빈도",
    "WEEKDAY_TIME_CODE": "주중 이용 시간대",
    "WEEKEND_TIME_CODE": "주말 이용 시간대",
    "SEARCH_VIEW": "검색 시청 성향",
    "RECOMMEND_VIEW": "추천 시청 성향",
    "BINGE_WATCH": "몰아보기 성향",
    "DEVICE_COUNT": "기기 수",
    "OTT_SERVICE_COUNT": "이용 OTT 수",
    "CONTENT_TYPE_COUNT": "이용 콘텐츠 종류 수",
    "BROADCAST_TYPE_COUNT": "이용 방송 유형 수",
}

def _resolve_model_path():
    for path in MODEL_PATH_CANDIDATES:
        if os.path.exists(path):
            return path
    raise PredictionError("모델 파일을 찾지 못했습니다. feature1_risk_model.pkl 파일 위치를 확인해주세요.")

def _load_model_bundle():
    model_path = _resolve_model_path()
    bundle = joblib.load(model_path)
    if not isinstance(bundle, dict):
        raise PredictionError("모델 파일 형식이 올바르지 않습니다.")
    model = bundle.get("model")
    feature_cols = bundle.get("feature_cols")
    if model is None or feature_cols is None:
        raise PredictionError("모델 파일에 필요한 정보가 없습니다.")
    return model, feature_cols

def _decode_value(field, value):
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

def _build_input_summary(row):
    summary = {}
    for col, value in row.items():
        label = KOREAN_LABELS.get(col, col)
        if pd.isna(value):
            summary[label] = "-"
        elif col in {"DEVICE_COUNT", "OTT_SERVICE_COUNT", "CONTENT_TYPE_COUNT", "BROADCAST_TYPE_COUNT"}:
            summary[label] = f"{int(value)}"
        else:
            summary[label] = _decode_value(col, value)
    return summary

def _make_reasons(row, risk_label, confidence):
    reasons = []
    use_freq = int(row.get("USE_FREQUENCY", 0)) if pd.notna(row.get("USE_FREQUENCY")) else None
    ad_intent = int(row.get("AD_INTENT", 0)) if pd.notna(row.get("AD_INTENT")) else None
    binge = int(row.get("BINGE_WATCH", 0)) if pd.notna(row.get("BINGE_WATCH")) else None
    recommend = int(row.get("RECOMMEND_VIEW", 0)) if pd.notna(row.get("RECOMMEND_VIEW")) else None

    if risk_label == "안정":
        if use_freq and use_freq <= 2:
            reasons.append("이용 빈도가 높아 안정적으로 서비스를 사용하는 패턴으로 해석됐습니다.")
        else:
            reasons.append("전반적인 이용 패턴이 유지형 사용자에 가까워 안정군으로 분류됐습니다.")
        if ad_intent and ad_intent >= 4:
            reasons.append("광고형 요금제 수용 의향이 높은 편이라 이탈 방지 전략 여지가 있습니다.")
        if binge and binge >= 4:
            reasons.append("몰아보기 성향이 있어 콘텐츠 몰입 자체는 비교적 긍정적으로 해석됐습니다.")
    elif risk_label == "주의":
        reasons.append("이탈 가능성이 높게 보이진 않지만, 유지 신호와 이탈 신호가 함께 보여 주의군으로 분류됐습니다.")
        if use_freq and use_freq >= 3:
            reasons.append("이용 빈도가 아주 높지 않아 재방문 유도 전략이 필요할 수 있습니다.")
        if recommend and recommend <= 2:
            reasons.append("추천 시청 성향이 낮아 콘텐츠 탐색 피로가 생길 가능성이 있습니다.")
    else:
        reasons.append("최근 이용 패턴이 약하거나 유지 신호가 부족해 위험군으로 분류됐습니다.")
        if use_freq and use_freq >= 4:
            reasons.append("이용 빈도가 낮은 편으로 해석돼 이탈 위험에 크게 반영됐습니다.")
        if ad_intent and ad_intent <= 2:
            reasons.append("광고형 요금제 수용 의향이 낮아 유지 전략 선택지가 좁을 수 있습니다.")
        if recommend and recommend <= 2:
            reasons.append("추천 소비 성향이 낮아 플랫폼 체류 유인이 약할 수 있습니다.")

    reasons.append(f"예측 신뢰도는 {confidence}%이며, 행동 기반 지표가 이번 판단에 크게 반영됐습니다.")
    return reasons

def _risk_label(pred_class):
    return {0: "안정", 1: "주의", 2: "위험"}.get(int(pred_class), "주의")

def _format_result(row, pred_class, pred_proba, user_seq=None):
    risk_label = _risk_label(pred_class)
    confidence = round(float(pred_proba[int(pred_class)]) * 100, 2)
    stable = round(float(pred_proba[0]) * 100, 2)
    caution = round(float(pred_proba[1]) * 100, 2)
    risk = round(float(pred_proba[2]) * 100, 2)
    input_summary = _build_input_summary(row)
    reasons = _make_reasons(row, risk_label, confidence)

    return {
        "user_seq": user_seq,
        "risk_label": risk_label,
        "confidence": confidence,
        "probabilities": {
            "stable": stable,
            "caution": caution,
            "risk": risk,
        },
        "reasons": reasons,
        "input_summary": input_summary,
    }

def _load_user_data(user_seq):
    if oracledb is None:
        raise PredictionError("oracledb 패키지가 설치되어 있지 않습니다.")
    query = f'''
        SELECT {", ".join(RAW_COLS)}
        FROM {TABLE_NAME}
        WHERE USER_SEQ = :user_seq
    '''
    conn = None
    try:
        conn = oracledb.connect(**DB_CONFIG)
        return pd.read_sql(query, conn, params={"user_seq": user_seq})
    finally:
        if conn is not None:
            conn.close()

def predict_from_user_seq(user_seq):
    model, feature_cols = _load_model_bundle()
    df_user = _load_user_data(user_seq)
    if df_user.empty:
        raise PredictionError("해당 사용자 번호를 찾지 못했습니다.")
    missing_cols = [col for col in feature_cols if col not in df_user.columns]
    if missing_cols:
        raise PredictionError("예측에 필요한 컬럼이 누락되었습니다.")
    x_user = df_user[feature_cols].copy()
    pred_class = int(model.predict(x_user)[0])
    pred_proba = model.predict_proba(x_user)[0]
    row = x_user.iloc[0].to_dict()
    return _format_result(row, pred_class, pred_proba, user_seq=user_seq)

def predict_from_manual_input(payload):
    model, feature_cols = _load_model_bundle()
    data = {}
    for col in feature_cols:
        value = str(payload.get(col, "")).strip()
        if value == "":
            raise PredictionError("직접 입력 항목을 모두 입력해주세요.")
        try:
            data[col] = int(value)
        except ValueError:
            raise PredictionError("입력값 형식이 올바르지 않습니다.")
    x_manual = pd.DataFrame([data])[feature_cols]
    pred_class = int(model.predict(x_manual)[0])
    pred_proba = model.predict_proba(x_manual)[0]
    row = x_manual.iloc[0].to_dict()
    return _format_result(row, pred_class, pred_proba, user_seq="직접 입력")
