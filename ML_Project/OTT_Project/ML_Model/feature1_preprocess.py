import pandas as pd
import oracledb
oracledb.init_oracle_client(lib_dir=r"C:\oraclexe\app\oracle\product\11.2.0\server\bin")
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


# -----------------------------
# 1. Oracle DB 연결 정보
# -----------------------------
DB_CONFIG = {
    "user": "scott",
    "password": "tiger",
    "host": "localhost",
    "port": 1521,
    "service_name": "xe"
}


# -----------------------------
# 2. Oracle에서 데이터 불러오기
# -----------------------------
def load_data():
    dsn = oracledb.makedsn(
        DB_CONFIG["host"],
        DB_CONFIG["port"],
        service_name=DB_CONFIG["service_name"]
    )

    conn = oracledb.connect(
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        dsn=dsn
    )

    query = "SELECT * FROM F1_USER_DATASET"
    df = pd.read_sql(query, conn)

    conn.close()
    return df


# -----------------------------
# 3. 전처리 함수
# -----------------------------
def preprocess_data(df: pd.DataFrame):
    print("원본 데이터 크기:", df.shape)
    print(df.head())

    # USER_SEQ는 식별자라서 제거
    if "USER_SEQ" in df.columns:
        df = df.drop(columns=["USER_SEQ"])

    # 타깃 분리
    X = df.drop(columns=["TARGET_RISK"])
    y = df["TARGET_RISK"]

    # 범주형 / 수치형 컬럼 구분
    categorical_cols = [
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
        "USED_LAST_WEEK",
        "SEARCH_VIEW",
        "RECOMMEND_VIEW",
        "BINGE_WATCH",
    ]

    numeric_cols = [
        "AVG_MIN_WEEKDAY",
        "AVG_MIN_WEEKEND",
        "DEVICE_COUNT",
        "OTT_SERVICE_COUNT",
        "CONTENT_TYPE_COUNT",
        "BROADCAST_TYPE_COUNT",
        "TOTAL_AVG_MIN",
    ]

    # 실제 존재하는 컬럼만 사용
    categorical_cols = [col for col in categorical_cols if col in X.columns]
    numeric_cols = [col for col in numeric_cols if col in X.columns]

    # 범주형 원-핫 인코딩
    X_encoded = pd.get_dummies(X, columns=categorical_cols, drop_first=False)

    # 수치형 스케일링
    scaler = StandardScaler()
    existing_numeric_cols = [col for col in numeric_cols if col in X_encoded.columns]
    X_encoded[existing_numeric_cols] = scaler.fit_transform(X_encoded[existing_numeric_cols])

    # train / test 분리
    X_train, X_test, y_train, y_test = train_test_split(
        X_encoded,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    print("\n전처리 후 X shape:", X_encoded.shape)
    print("X_train shape:", X_train.shape)
    print("X_test shape:", X_test.shape)
    print("\n타깃 분포:")
    print(y.value_counts().sort_index())

    return X_train, X_test, y_train, y_test, scaler


# -----------------------------
# 4. 실행부
# -----------------------------
if __name__ == "__main__":
    df = load_data()
    X_train, X_test, y_train, y_test, scaler = preprocess_data(df)

    print("\n전처리 완료!")