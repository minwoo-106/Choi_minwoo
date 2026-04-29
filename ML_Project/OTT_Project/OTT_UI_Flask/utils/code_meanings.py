CODE_MAPS = {
    "GENDER": {1: "남자", 2: "여자"},
    "AGE_GROUP": {1: "10대", 2: "20대", 3: "30대", 4: "40대", 5: "50대", 6: "60대", 7: "70세 이상"},
    "INCOME_GROUP": {1: "100만원 미만", 2: "100~199만원", 3: "200~299만원", 4: "300~399만원", 5: "400~499만원", 6: "500~599만원", 7: "600만원 이상", 9: "무응답"},
    "FAMILY_TYPE": {1: "1인가구", 2: "1세대가구", 3: "2세대가구", 4: "3세대가구", 5: "기타"},
    "MONTHLY_FEE_CODE": {1: "3,000원 미만", 2: "3,000원 이상 ~ 5,000원 미만", 3: "5,000원 이상 ~ 7,000원 미만", 4: "7,000원 이상 ~ 10,000원 미만", 5: "10,000원 이상 ~ 13,000원 미만", 6: "13,000원 이상 ~ 15,000원 미만", 7: "15,000원 이상", 8: "지인 계정 사용"},
    "HAS_AD_PLAN": {1: "예", 2: "아니오"},
    "AD_INTENT": {1: "전혀 이용하지 않을 것 같다", 2: "별로 이용하지 않을 것 같다", 3: "보통이다", 4: "이용할 것 같다", 5: "반드시 이용할 생각이다"},
    "USE_FREQUENCY": {1: "매일", 2: "주 4~6일", 3: "주 2~3일", 4: "주 1일", 5: "월 1~3일", 6: "2~3달에 1~2일 이하"},
    "WEEKDAY_TIME_CODE": {1: "06:00~08:59", 2: "09:00~11:59", 3: "12:00~13:59", 4: "14:00~16:59", 5: "17:00~19:59", 6: "20:00~22:59", 7: "23:00~01:59", 8: "주중에 이용하지 않음"},
    "WEEKEND_TIME_CODE": {1: "06:00~08:59", 2: "09:00~11:59", 3: "12:00~13:59", 4: "14:00~16:59", 5: "17:00~19:59", 6: "20:00~22:59", 7: "23:00~01:59", 8: "주말에 이용하지 않음"},
    "SEARCH_VIEW": {1: "전혀 그렇지 않다", 2: "그렇지 않은 편이다", 3: "보통이다", 4: "그런 편이다", 5: "매우 그렇다"},
    "RECOMMEND_VIEW": {1: "전혀 그렇지 않다", 2: "그렇지 않은 편이다", 3: "보통이다", 4: "그런 편이다", 5: "매우 그렇다"},
    "BINGE_WATCH": {1: "전혀 그렇지 않다", 2: "그렇지 않은 편이다", 3: "보통이다", 4: "그런 편이다", 5: "매우 그렇다"},
}
FIELD_LABELS = {"GENDER":"성별","AGE_GROUP":"연령대","INCOME_GROUP":"소득 구간","FAMILY_TYPE":"가구 형태","MONTHLY_FEE_CODE":"월 결제액","HAS_AD_PLAN":"광고 요금제 이용 여부","AD_INTENT":"광고 요금제 이용 의향","USE_FREQUENCY":"이용 빈도","WEEKDAY_TIME_CODE":"주중 이용 시간대","WEEKEND_TIME_CODE":"주말 이용 시간대","SEARCH_VIEW":"검색 시청 성향","RECOMMEND_VIEW":"추천 시청 성향","BINGE_WATCH":"몰아보기 성향","DEVICE_COUNT":"이용 기기 수","OTT_SERVICE_COUNT":"이용 OTT 수","CONTENT_TYPE_COUNT":"이용 콘텐츠 수","BROADCAST_TYPE_COUNT":"이용 방송 유형 수"}
DEFAULT_FORM_VALUES = {"GENDER":1,"AGE_GROUP":2,"INCOME_GROUP":4,"FAMILY_TYPE":1,"MONTHLY_FEE_CODE":4,"HAS_AD_PLAN":2,"AD_INTENT":3,"USE_FREQUENCY":3,"WEEKDAY_TIME_CODE":6,"WEEKEND_TIME_CODE":6,"SEARCH_VIEW":3,"RECOMMEND_VIEW":4,"BINGE_WATCH":3,"DEVICE_COUNT":2,"OTT_SERVICE_COUNT":2,"CONTENT_TYPE_COUNT":3,"BROADCAST_TYPE_COUNT":2}
FORM_FIELDS = ["GENDER","AGE_GROUP","INCOME_GROUP","FAMILY_TYPE","MONTHLY_FEE_CODE","HAS_AD_PLAN","AD_INTENT","USE_FREQUENCY","WEEKDAY_TIME_CODE","WEEKEND_TIME_CODE","SEARCH_VIEW","RECOMMEND_VIEW","BINGE_WATCH","DEVICE_COUNT","OTT_SERVICE_COUNT","CONTENT_TYPE_COUNT","BROADCAST_TYPE_COUNT"]
