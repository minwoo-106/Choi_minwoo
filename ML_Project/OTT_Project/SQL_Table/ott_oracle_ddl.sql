-- ============================================================
-- OTT 리텐션 프로젝트 Oracle DB DDL
-- 기준 데이터: 2024 방송매체이용행태조사 (유료OTT 이용자 2,671명)
-- B문14 응답코드 98(이용경험없음) 제외 후 필터링된 데이터
-- ============================================================


-- ============================================================
-- 시퀀스 (USER_SEQ 자동 생성용)
-- ============================================================
CREATE SEQUENCE SEQ_USER
    START WITH 1
    INCREMENT BY 1
    NOCACHE
    NOCYCLE;


-- ============================================================
-- 1. USERS 테이블
-- 성별, 연령대 기본 인구통계
-- ============================================================
CREATE TABLE USERS (
    USER_SEQ    NUMBER      NOT NULL,
    GENDER      NUMBER(1)   NOT NULL,
    -- 1=남자, 2=여자
    AGE_GROUP   NUMBER(1)   NOT NULL,
    -- 1=10대, 2=20대, 3=30대, 4=40대, 5=50대, 6=60대, 7=70세이상
    CONSTRAINT PK_USERS PRIMARY KEY (USER_SEQ)
);


-- ============================================================
-- 2. ECONOMY 테이블
-- 가구소득, 가족구성
-- ============================================================
CREATE TABLE ECONOMY (
    USER_SEQ        NUMBER      NOT NULL,
    INCOME_GROUP    NUMBER(1)   NOT NULL,
    -- 1=100만원미만, 2=100-199만원, 3=200-299만원, 4=300-399만원
    -- 5=400-499만원, 6=500-599만원, 7=600만원이상, 9=무응답
    FAMILY_TYPE     NUMBER(1)   NOT NULL,
    -- 1=1인가구, 2=1세대가구, 3=2세대가구, 4=3세대가구, 5=기타
    CONSTRAINT PK_ECONOMY PRIMARY KEY (USER_SEQ),
    CONSTRAINT FK_ECONOMY_USERS FOREIGN KEY (USER_SEQ) REFERENCES USERS(USER_SEQ)
);


-- ============================================================
-- 3. SUBSCRIPTION 테이블
-- 요금제 + 광고형 요금제 수용 의향 (Target 변수 포함)
--
-- [AD_INTENT 통합 로직]
-- B문15=1 (현재 광고형 이용자, 429명) → B문15-1 값 사용
-- B문15=2 (미이용자, 1886명)          → B문16 값 사용
-- B문15=NaN (356명)                   → NULL 저장, 모델 학습 시 제외
-- 두 문항 동일 척도 확인 완료:
--   1=전혀이용하지않을것같다 ~ 5=반드시이용할생각이다
-- ============================================================
CREATE TABLE SUBSCRIPTION (
    USER_SEQ            NUMBER      NOT NULL,
    MONTHLY_FEE_CODE    NUMBER(1),
    -- 월 이용 요금 구간 (B문14-1)
    -- 1=3천원미만, 2=3천-5천원미만, 3=5천-9천원미만, 4=9천-12천원미만
    -- 5=12천-15천원미만, 6=15천-20천원미만, 7=2만원이상, 8=지인계정사용
    HAS_AD_PLAN         NUMBER(1),
    -- 현재 광고형 요금제 이용 여부 (B문15)
    -- 1=예, 2=아니오
    AD_INTENT           NUMBER(1),
    -- [Target] 광고형 요금제 수용 의향 (B문15-1 또는 B문16 통합)
    -- 1=전혀이용하지않을것같다, 2=별로이용하지않을것같다, 3=보통이다
    -- 4=이용할수도있을것같다, 5=반드시이용할생각이다
    -- NULL=B문15 무응답자(356명), 모델 학습 시 제외
    CONSTRAINT PK_SUBSCRIPTION PRIMARY KEY (USER_SEQ),
    CONSTRAINT FK_SUBSCRIPTION_USERS FOREIGN KEY (USER_SEQ) REFERENCES USERS(USER_SEQ),
    CONSTRAINT CHK_AD_INTENT CHECK (AD_INTENT BETWEEN 1 AND 5 OR AD_INTENT IS NULL)
);


-- ============================================================
-- 4. USAGE_BEHAVIOR 테이블
-- OTT 이용 행태 (빈도, 시간대, 이용시간, 시청 패턴)
-- ============================================================
CREATE TABLE USAGE_BEHAVIOR (
    USER_SEQ            NUMBER      NOT NULL,
    USE_FREQUENCY       NUMBER(1),
    -- OTT 이용 빈도 (B문17)
    -- 1=매일, 2=1주일에5~6일, 3=1주일에3~4일
    -- 4=1주일에1~2일, 5=한달에1~3일, 6=2~3달에1~2일이하
    WEEKDAY_TIME_CODE   NUMBER(1),
    -- 평소 주중 주이용 시간대 (B문19)
    -- 1=06~08시, 2=09~11시, 3=12~14시, 4=15~17시
    -- 5=18~20시, 6=21~23시, 7=24~05시, 8=주중이용안함
    WEEKEND_TIME_CODE   NUMBER(1),
    -- 평소 주말 주이용 시간대 (B문20)
    -- 1=06~08시, 2=09~11시, 3=12~14시, 4=15~17시
    -- 5=18~20시, 6=21~23시, 7=24~05시, 8=주말이용안함
    USED_LAST_WEEK      NUMBER(1),
    -- 최근 일주일 이용 여부 (B문21)
    -- 1=이용한적있다, 2=이용한적없다
    AVG_MIN_WEEKDAY     NUMBER(5,1),
    -- 일평균 OTT 이용 시간(분) - 주중 (B문21-0 주중)
    AVG_MIN_WEEKEND     NUMBER(5,1),
    -- 일평균 OTT 이용 시간(분) - 주말 (B문21-0 주말)
    SEARCH_VIEW         NUMBER(1),
    -- 보고싶은 프로그램 검색해서 시청 (B문24_1)
    -- 1=전혀그렇지않다, 2=그렇지않다, 3=보통이다, 4=그렇다, 5=매우그렇다
    RECOMMEND_VIEW      NUMBER(1),
    -- OTT 추천 프로그램 시청 (B문24_2)
    -- 1=전혀그렇지않다, 2=그렇지않다, 3=보통이다, 4=그렇다, 5=매우그렇다
    BINGE_WATCH         NUMBER(1),
    -- 시리즈 몰아보기 선호 (B문26_2)
    -- 1=전혀그렇지않다, 2=그렇지않다, 3=보통이다, 4=그렇다, 5=매우그렇다
    CONSTRAINT PK_USAGE PRIMARY KEY (USER_SEQ),
    CONSTRAINT FK_USAGE_USERS FOREIGN KEY (USER_SEQ) REFERENCES USERS(USER_SEQ)
);


-- ============================================================
-- 5. USER_OTT_SERVICE 테이블 (복수응답 - B문14)
-- 현재 월정액/추가요금 이용 중인 OTT 서비스
-- PK = (USER_SEQ, SERVICE_CODE) 복합키
-- ============================================================
CREATE TABLE USER_OTT_SERVICE (
    USER_SEQ        NUMBER      NOT NULL,
    SERVICE_CODE    NUMBER(2)   NOT NULL,
    -- 1=웨이브(Wavve), 2=티빙(Tving), 3=U+모바일tv, 4=곰TV
    -- 5=네이버NOW, 6=위버스, 7=아프리카TV, 8=왓챠, 9=카카오TV
    -- 10=쿠팡플레이, 11=네이버시리즈온, 12=카카오페이지, 13=라프텔
    -- 14=스포티비나우, 15=네이버치지직, 20=넷플릭스
    -- 22=디즈니플러스, 23=아마존프라임, 24=애플TV+
    -- 25=유튜브프리미엄, 27=틱톡라이브구독
    CONSTRAINT PK_USER_OTT_SERVICE PRIMARY KEY (USER_SEQ, SERVICE_CODE),
    CONSTRAINT FK_OTT_SERVICE_USERS FOREIGN KEY (USER_SEQ) REFERENCES USERS(USER_SEQ)
);


-- ============================================================
-- 6. USER_DEVICE 테이블 (복수응답 - B문18)
-- OTT 이용 시 사용하는 기기
-- PK = (USER_SEQ, DEVICE_CODE) 복합키
-- ============================================================
CREATE TABLE USER_DEVICE (
    USER_SEQ        NUMBER      NOT NULL,
    DEVICE_CODE     NUMBER(1)   NOT NULL,
    -- 1=TV수상기, 2=데스크탑PC, 3=노트북, 4=스마트폰, 5=태블릿PC
    CONSTRAINT PK_USER_DEVICE PRIMARY KEY (USER_SEQ, DEVICE_CODE),
    CONSTRAINT FK_USER_DEVICE_USERS FOREIGN KEY (USER_SEQ) REFERENCES USERS(USER_SEQ)
);


-- ============================================================
-- 7. USER_CONTENT_TYPE 테이블 (복수응답 - B문23)
-- OTT에서 시청하는 콘텐츠 제작 유형
-- PK = (USER_SEQ, CONTENT_CODE) 복합키
-- ============================================================
CREATE TABLE USER_CONTENT_TYPE (
    USER_SEQ        NUMBER      NOT NULL,
    CONTENT_CODE    NUMBER(1)   NOT NULL,
    -- 1=지상파방송제작프로그램(KBS/MBC/SBS등)
    -- 2=유료방송채널제작프로그램(tvN/JTBC/YTN등)
    -- 3=OTT자체제작오리지널(넷플릭스/웨이브오리지널등)
    -- 4=영화
    -- 5=숏폼(유튜브숏츠/인스타릴스/틱톡)
    -- 6=기타(일상vlog/웹드라마등, 숏폼제외)
    CONSTRAINT PK_USER_CONTENT PRIMARY KEY (USER_SEQ, CONTENT_CODE),
    CONSTRAINT FK_USER_CONTENT_USERS FOREIGN KEY (USER_SEQ) REFERENCES USERS(USER_SEQ)
);


-- ============================================================
-- 8. USER_BROADCAST_TYPE 테이블 (복수응답 - B문23-1)
-- OTT로 시청한 지상파/유료방송 프로그램 장르
-- PK = (USER_SEQ, BROADCAST_CODE) 복합키
-- ============================================================
CREATE TABLE USER_BROADCAST_TYPE (
    USER_SEQ            NUMBER      NOT NULL,
    BROADCAST_CODE      NUMBER(1)   NOT NULL,
    -- 1=뉴스, 2=드라마, 3=스포츠, 4=시사/교양, 5=오락/연예, 6=기타
    CONSTRAINT PK_USER_BROADCAST PRIMARY KEY (USER_SEQ, BROADCAST_CODE),
    CONSTRAINT FK_USER_BROADCAST_USERS FOREIGN KEY (USER_SEQ) REFERENCES USERS(USER_SEQ)
);
