import os
import warnings

import joblib
import pandas as pd

warnings.filterwarnings("ignore")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "saved_models", "feature1_risk_model.pkl")


CODE_GUIDE = {
    "GENDER": "1:남자, 2:여자",
    "AGE_GROUP": "1:10대, 2:20대, 3:30대, 4:40대, 5:50대, 6:60대, 7:70세 이상",
    "INCOME_GROUP": "1:100만원 미만, 2:100~199만원, 3:200~299만원, 4:300~399만원, 5:400~499만원, 6:500~599만원, 7:600만원 이상, 9:무응답",
    "FAMILY_TYPE": "1:1인가구, 2:1세대가구, 3:2세대가구, 4:3세대가구, 5:기타",
    "MONTHLY_FEE_CODE": "1:3000원 미만, 2:3000~5000원 미만, 3:5000~7000원 미만, 4:7000~10000원 미만, 5:10000~13000원 미만, 6:13000~15000원 미만, 7:15000원 이상, 8:지인 계정 사용",
    "HAS_AD_PLAN": "1:예, 2:아니오",
    "AD_INTENT": "1:전혀 이용 안 할 것, 2:별로 이용 안 할 것, 3:보통, 4:이용할 것, 5:반드시 이용",
    "USE_FREQUENCY": "1:매일, 2:주4~6일, 3:주2~3일, 4:주1일, 5:월1~3일, 6:2~3달에 1~2일 이하",
    "WEEKDAY_TIME_CODE": "1:06~08시, 2:09~11시, 3:12~13시, 4:14~16시, 5:17~19시, 6:20~22시, 7:23~01시, 8:주중 이용 안함",
    "WEEKEND_TIME_CODE": "1:06~08시, 2:09~11시, 3:12~13시, 4:14~16시, 5:17~19시, 6:20~22시, 7:23~01시, 8:주말 이용 안함",
    "SEARCH_VIEW": "1:전혀 그렇지 않다, 2:그렇지 않은 편이다, 3:보통이다, 4:그런 편이다, 5:매우 그렇다",
    "RECOMMEND_VIEW": "1:전혀 그렇지 않다, 2:그렇지 않은 편이다, 3:보통이다, 4:그런 편이다, 5:매우 그렇다",
    "BINGE_WATCH": "1:전혀 그렇지 않다, 2:그렇지 않은 편이다, 3:보통이다, 4:그런 편이다, 5:매우 그렇다",
}


def load_model_bundle():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"모델 파일이 없습니다: {MODEL_PATH}")

    bundle = joblib.load(MODEL_PATH)

    if not isinstance(bundle, dict):
        raise ValueError("모델 파일 형식이 올바르지 않습니다.")

    model = bundle.get("model")
    feature_cols = bundle.get("feature_cols")
    model_name = bundle.get("model_name", "UNKNOWN")

    if model is None or feature_cols is None:
        raise ValueError("모델 파일에 model 또는 feature_cols 정보가 없습니다.")

    return model, feature_cols, model_name


def risk_label_from_class(pred_class: int) -> str:
    label_map = {
        0: "안정",
        1: "주의",
        2: "위험",
    }
    return label_map.get(pred_class, f"알 수 없음({pred_class})")


def input_int_value(col_name: str) -> int:
    while True:
        try:
            guide = CODE_GUIDE.get(col_name)
            if guide:
                print(f"\n[{col_name}] {guide}")

            value = int(input(f"{col_name} 값을 입력하세요: ").strip())

            if col_name in [
                "DEVICE_COUNT",
                "OTT_SERVICE_COUNT",
                "CONTENT_TYPE_COUNT",
                "BROADCAST_TYPE_COUNT",
            ] and value < 0:
                print("0 이상의 숫자를 입력하세요.")
                continue

            return value

        except ValueError:
            print("숫자만 입력하세요.")


def make_input_df(feature_cols):
    print("\n" + "=" * 60)
    print("신규 사용자 정보 입력")
    print("=" * 60)

    user_data = {}
    for col in feature_cols:
        user_data[col] = input_int_value(col)

    return pd.DataFrame([user_data])


def predict_new_user():
    model, feature_cols, model_name = load_model_bundle()

    print(f"\n모델명: {model_name}")
    print("사용 피처:", feature_cols)

    df_input = make_input_df(feature_cols)

    pred_class = int(model.predict(df_input)[0])
    pred_proba = model.predict_proba(df_input)[0]
    risk_label = risk_label_from_class(pred_class)
    confidence = round(pred_proba[pred_class] * 100, 2)

    print("\n" + "=" * 60)
    print("신규 사용자 예측 결과")
    print("=" * 60)
    print(f"예측 클래스    : {pred_class}")
    print(f"예측 등급      : {risk_label}")
    print(f"예측 신뢰도    : {confidence}%")

    print("\n클래스별 확률")
    print(f"안정(0) : {pred_proba[0] * 100:.2f}%")
    print(f"주의(1) : {pred_proba[1] * 100:.2f}%")
    print(f"위험(2) : {pred_proba[2] * 100:.2f}%")

    print("\n입력값 확인")
    print(df_input.to_string(index=False))


if __name__ == "__main__":
    try:
        predict_new_user()
    except Exception as e:
        print(f"오류 발생: {e}")
