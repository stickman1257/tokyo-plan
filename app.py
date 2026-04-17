# ============================================================
# 🗼 도쿄 2박 3일 가족 여행 플래너 - Streamlit App
# ============================================================
# 실행 방법:
#   pip install streamlit folium streamlit-folium
#   streamlit run app.py
# ============================================================

import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(
    page_title="🗼 도쿄 2박3일 가족여행 플래너",
    page_icon="🗼",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }

    .main-header {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        padding: 1.5rem 2rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    .main-header h1 { margin: 0; font-size: 2rem; }
    .main-header p  { margin: 0.3rem 0 0 0; opacity: 0.9; font-size: 0.95rem; }

    .schedule-card {
        background: #ffffff;
        border-left: 5px solid #ee5a24;
        border-radius: 10px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .schedule-card.transport { background: #f0f4ff; border-left-color: #3498db; }
    .schedule-card.meal      { background: #fff8f0; border-left-color: #f39c12; }
    .schedule-card.hotel     { background: #f0fff4; border-left-color: #27ae60; }

    .checklist-item {
        background: white;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        border-left: 5px solid #ee5a24;
    }
    .checklist-item h4 { margin: 0 0 0.3rem 0; color: #ee5a24; }

    .rest-card {
        background: #fffaf5;
        border: 1px solid #ffd6b5;
        border-radius: 10px;
        padding: 0.9rem 1.2rem;
        margin-bottom: 0.6rem;
    }
    .rest-card h5 { margin: 0 0 0.2rem 0; color: #d35400; }

    .hotel-card {
        background: white;
        border-radius: 14px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border-top: 4px solid #ee5a24;
    }
    .hotel-card h3 { color: #ee5a24; margin-top: 0; }

    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"]      { padding: 10px 20px; font-size: 1rem; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 데이터 정의
# ============================================================

JPY_TO_KRW = 9.5  # 1엔 ≈ 9.5원 (참고용)

def yen(amt: int) -> str:
    krw = int(amt * JPY_TO_KRW)
    return f"¥{amt:,} (≈₩{krw:,})"

# ---------- 관광지 ----------
SPOTS = {
    "narita_airport": {
        "name": "나리타 공항 (成田空港)",
        "lat": 35.7647, "lon": 140.3864,
        "hours": "24시간", "fee": 0,
        "desc": "도쿄의 관문. 스카이라이너 탑승으로 우에노까지 41분.",
    },
    "ueno_park": {
        "name": "우에노 공원 (上野公園)",
        "lat": 35.7142, "lon": 139.7713,
        "hours": "05:00~23:00", "fee": 0,
        "desc": "도쿄 최대 공원. 국립박물관·동물원·연못 밀집. 스카이라이너 하차역 우에노에서 도보 5분.",
        "tips": "5월 장미원 개화. 국립서양미술관(UNESCO) 무료 상설전시.",
    },
    "ameyoko": {
        "name": "아메요코 (アメ横)",
        "lat": 35.7082, "lon": 139.7741,
        "hours": "10:00~20:00 (매장별 상이)", "fee": 0,
        "desc": "우에노역 앞 400m 시장 거리. 해산물·과자·화장품 저렴한 쇼핑.",
        "tips": "기념품 최적지! 귀국 선물 여기서 해결.",
    },
    "ginza": {
        "name": "긴자 (銀座)",
        "lat": 35.6717, "lon": 139.7649,
        "hours": "상시 (백화점 10:30~20:00)", "fee": 0,
        "desc": "도쿄 최고급 쇼핑 거리. 숙소 인근. 저녁 산책·식사 코스.",
        "tips": "긴자 식스 옥상 정원 무료. 주말 오후 보행자 천국.",
    },
    "shibuya": {
        "name": "시부야 스크램블 교차로 (渋谷スクランブル)",
        "lat": 35.6594, "lon": 139.7005,
        "hours": "24시간", "fee": 0,
        "desc": "세계 최대 규모 교차로. 하루 50만명 통행. 스크램블 스퀘어 전망대에서 조망 추천.",
        "tips": "스타벅스 시부야점 2층에서 무료 조망 가능!",
    },
    "shibuya_sky": {
        "name": "시부야 스카이 (SHIBUYA SKY)",
        "lat": 35.6581, "lon": 139.7016,
        "hours": "10:00~22:30 (최종입장 21:20)", "fee": 2000,
        "desc": "스크램블 스퀘어 46층, 230m 옥상 전망대. 360° 파노라마 뷰.",
        "tips": "사전 예약 강력 추천. 맑은 날엔 후지산도 보임!",
    },
    "shinjuku_gyoen": {
        "name": "신주쿠 교엔 (新宿御苑)",
        "lat": 35.6852, "lon": 139.7100,
        "hours": "09:00~18:00 (월요일 휴원)", "fee": 500,
        "desc": "58.3ha 광대한 정원. 일본·프랑스·영국식 세 가지 정원.",
        "tips": "5월 초 장미원 절정. 벤치 많아 부모님 쉬기 좋음.",
    },
    "shinjuku_omoide": {
        "name": "오모이데 요코초 (思い出横丁)",
        "lat": 35.6939, "lon": 139.7008,
        "hours": "17:00~24:00 (가게마다 상이)", "fee": 0,
        "desc": "신주쿠역 서쪽 출구 앞 좁은 골목 야키토리 이자카야 거리.",
        "tips": "연기 자욱한 레트로 분위기. 꼬치 1串 ¥150~350.",
    },
    "tokyo_station": {
        "name": "도쿄역 마루노우치 (東京駅丸の内)",
        "lat": 35.6812, "lon": 139.7671,
        "hours": "24시간 (그란스타 07:00~22:00)", "fee": 0,
        "desc": "1914년 건축 붉은 벽돌 역사. 그란스타 지하 식품관·라멘 스트리트. 긴자에서 도보 15분.",
        "tips": "도쿄 바나나·긴자 쇼콜라 귀국 선물 쇼핑 최적지!",
    },
}

# ---------- 숙소 (긴자 지역 추천) ----------
HOTELS = [
    {
        "name": "미츠이 가든 호텔 긴자 프리미어",
        "name_jp": "三井ガーデンホテル銀座プレミア",
        "area": "긴자",
        "star": "★★★★",
        "price_per_night_krw": 350000,
        "room_type": "모더레이트 트윈 × 2실",
        "total_2nights_krw": 700000,
        "lat": 35.6713, "lon": 139.7652,
        "access": "긴자역 도보 3분 / 신바시역 도보 5분",
        "airport_access": "긴자 → 히비야선 → 우에노 (약 10분) → Skyliner → 나리타",
        "pros": [
            "긴자 중심가, 쇼핑·식사 접근성 최고",
            "우에노(Skyliner) 히비야선 직통 10분",
            "도쿄역 도보 15분 (3일차 편리)",
            "같은 층 방 2개 배정 요청 가능",
        ],
    },
    {
        "name": "도미인 PREMIUM 긴자",
        "name_jp": "ドーミーインPREMIUM銀座",
        "area": "히가시긴자",
        "star": "★★★★",
        "price_per_night_krw": 300000,
        "room_type": "더블/트윈 × 2실",
        "total_2nights_krw": 600000,
        "lat": 35.6671, "lon": 139.7660,
        "access": "히가시긴자역 도보 2분 / 긴자역 도보 5분",
        "airport_access": "히가시긴자 → 아사쿠사선 → 케이세이 우에노 → Skyliner → 나리타",
        "pros": [
            "무료 온천(대욕장) 시설 완비 — 여행 피로 해소",
            "야식 서비스(무료 라멘·아이스) 제공",
            "한국인 여행자에게 높은 만족도",
            "가격 대비 품질 우수, 2박 합계 ₩60만",
        ],
    },
    {
        "name": "더 게이트 호텔 긴자 by HULIC",
        "name_jp": "THE GATE HOTEL銀座 by HULIC",
        "area": "긴자",
        "star": "★★★★",
        "price_per_night_krw": 390000,
        "room_type": "슈페리어 트윈 × 2실",
        "total_2nights_krw": 780000,
        "lat": 35.6700, "lon": 139.7640,
        "access": "긴자역 도보 1분 (최고 입지!)",
        "airport_access": "긴자 → 히비야선 → 우에노 → Skyliner → 나리타",
        "pros": [
            "긴자역 바로 앞 — 이동 피로 제로",
            "루프탑 바에서 도쿄 야경 감상",
            "세련된 부티크 호텔 인테리어",
            "도쿄역 도보 15분 (3일차 편리)",
        ],
    },
]

# ---------- 일정 ----------
ITINERARY = {
    "day1": {
        "date": "5월 1일 (목) - Day 1",
        "theme": "나리타 도착 → 우에노 탐방 → 긴자 숙소",
        "schedules": [
            {
                "time": "08:35",
                "end_time": "11:00",
                "title": "✈️ 인천 → 나리타 비행",
                "type": "transport",
                "detail": "인천공항 08:35 출발 → 나리타공항 11:00 도착 (비행 약 2시간 25분)",
                "info": "기내 수하물 규정 확인 필수. 입국 카드 기내에서 미리 작성!",
            },
            {
                "time": "11:00",
                "end_time": "12:20",
                "title": "🛂 입국 심사 & 수화물 수취",
                "type": "transport",
                "detail": "입국 심사 + 짐 찾기 약 60~80분 소요. 1층에서 Suica 교통카드 구매 가능.",
                "info": "Visit Japan Web 앱으로 사전 등록 시 입국 심사 줄 단축 가능!",
            },
            {
                "time": "12:30",
                "title": "🚃 나리타 → 우에노 (스카이라이너)",
                "type": "transport",
                "detail": "나리타공항 → 케이세이우에노역. 스카이라이너 41분 직통.",
                "info": "클룩 패스 사용 (왕복 포함). 지정석이므로 탑승 전 좌석 지정 필수!",
                "tips": "수화물이 많으면 1층 짐 보관소(코인로커)에 먼저 맡기고 탑승하는 것도 방법.",
                "transport_options": [
                    {
                        "method": "🚃 스카이라이너 (Skyliner)",
                        "duration": "41분",
                        "cost_per_person": None,
                        "cost_total_4": 0,
                        "cost_display": "클룩 패스 포함",
                        "detail": "쾌적한 특급 열차. 지정석. 클룩 패스로 무료 이용!",
                        "recommended": True,
                    },
                    {
                        "method": "🚌 리무진 버스",
                        "duration": "약 80~100분",
                        "cost_per_person": 1000,
                        "cost_total_4": 4000,
                        "cost_display": yen(4000),
                        "detail": "짐 많으면 편리하나 교통 상황에 따라 지연 가능.",
                        "recommended": False,
                    },
                ],
            },
            {
                "time": "13:20",
                "title": "🏨 우에노역 코인로커 짐 보관",
                "type": "hotel",
                "detail": "케이세이우에노역 또는 JR우에노역 코인로커에 무거운 짐 보관 (약 ¥600~900).",
                "info": "체크인 가능 시간(15:00) 전이므로 짐은 로커에 맡기고 가볍게 관광!",
                "tips": "대형 캐리어용 로커(400엔짜리 X, 700~900엔짜리 이용). IC카드 결제 가능.",
            },
            {
                "time": "13:30",
                "title": "🍜 점심: 우에노 맛집",
                "type": "meal",
                "detail": "우에노역 근처 점심 식사.",
                "info": f"예산: 1인 ¥1,500~2,500 | 4인 약 {yen(8000)}",
                "tips": "추천 ① 나다이 우나토토 (名代宇奈とと) — 가성비 장어덮밥 체인, 우에노역 1분 ¥900~1,600 / 추천 ② 이센 혼텐 (井泉本店) — 돈카츠 원조집, 오카치마치 1분, ¥1,500~2,500",
            },
            {
                "time": "14:30",
                "end_time": "15:30",
                "title": "🌳 우에노 공원 산책",
                "type": "spot",
                "spot_key": "ueno_park",
                "detail": "우에노 공원 산책 + 연못(시노바즈 연못) 감상. 박물관 방문도 선택 가능.",
                "info": "입장료 무료 | 05:00~23:00",
                "tips": "도쿄국립박물관 (상설전 ¥1,000), 국립서양미술관 상설전 무료. 부모님 쉬시기 좋은 벤치 많음.",
            },
            {
                "time": "15:30",
                "end_time": "17:00",
                "title": "🛍️ 아메요코 시장 구경",
                "type": "spot",
                "spot_key": "ameyoko",
                "detail": "JR우에노역 맞은편 400m 시장 골목. 건어물·과자·화장품·잡화 등 저렴한 쇼핑.",
                "info": "입장료 무료 | 대부분 10:00~20:00",
                "tips": "귀국 선물 미리 사두면 3일차 편함! 과자 묶음, 화장품 저렴.",
            },
            {
                "time": "17:00",
                "title": "🚃 우에노 → 긴자 (히비야선)",
                "type": "transport",
                "transport_options": [
                    {
                        "method": "🚃 도쿄메트로 히비야선 직통",
                        "duration": "약 10분",
                        "cost_per_person": 195,
                        "cost_total_4": 780,
                        "cost_display": "클룩 3일 패스 포함",
                        "detail": "우에노역 → 긴자역 직통, 환승 없음. 코인로커 짐 찾아서 탑승.",
                        "recommended": True,
                    },
                    {
                        "method": "🚕 택시",
                        "duration": "약 15분",
                        "cost_per_person": None,
                        "cost_total_4": 1500,
                        "cost_display": yen(1500),
                        "detail": "짐 많으면 택시가 편리.",
                        "recommended": False,
                    },
                ],
            },
            {
                "time": "17:30",
                "title": "🏨 숙소 체크인",
                "type": "hotel",
                "detail": "긴자 지역 숙소 체크인. 방 배정 후 짐 풀고 저녁 준비.",
                "info": "체크인 보통 15:00~. 방 2개 같은 층 요청 미리 해두기.",
            },
            {
                "time": "19:00",
                "title": "🍽️ 저녁: 긴자 맛집",
                "type": "meal",
                "detail": "숙소 주변 긴자 저녁 식사.",
                "info": f"예산: 1인 ¥2,500~4,000 | 4인 약 {yen(12000)}",
                "tips": "추천 ① 규카츠 모토무라 긴자점 — 규카츠(소고기 돈카츠) ¥2,000~2,500 / 추천 ② 긴자 텐이치 (天一) — 텐푸라 ¥3,000~5,000",
            },
        ],
    },
    "day2": {
        "date": "5월 2일 (금) - Day 2",
        "theme": "시부야 오전 & 신주쿠 오후·저녁",
        "schedules": [
            {
                "time": "08:00",
                "title": "🍳 호텔 조식",
                "type": "meal",
                "detail": "호텔 조식 뷔페 또는 근처 편의점 간단 아침.",
                "info": "호텔 조식 약 ¥1,500/인 | 편의점 약 ¥500/인",
            },
            {
                "time": "09:00",
                "title": "🚃 긴자 → 시부야 이동",
                "type": "transport",
                "transport_options": [
                    {
                        "method": "🚃 히비야선 → 후쿠토신선 환승",
                        "duration": "약 20분",
                        "cost_per_person": 250,
                        "cost_total_4": 1000,
                        "cost_display": "클룩 3일 패스 포함",
                        "detail": "긴자역 → (히비야선) → 나카메구로 → (후쿠토신선) → 시부야. 또는 긴자→롯폰기→시부야 루트.",
                        "recommended": True,
                    },
                    {
                        "method": "🚕 택시",
                        "duration": "약 20분",
                        "cost_per_person": None,
                        "cost_total_4": 2500,
                        "cost_display": yen(2500),
                        "detail": "오전 시간대 혼잡 가능. 전철이 더 효율적.",
                        "recommended": False,
                    },
                ],
            },
            {
                "time": "09:30",
                "end_time": "10:00",
                "title": "🚦 시부야 스크램블 교차로",
                "type": "spot",
                "spot_key": "shibuya",
                "detail": "세계에서 가장 유명한 스크램블 교차로. 교차로 한가운데서 사방 촬영.",
                "info": "입장료 무료 | 24시간",
                "tips": "스타벅스 시부야점 2층에서 교차로 전체를 무료로 내려다볼 수 있음! 아침 9시대 줄 없어서 추천.",
            },
            {
                "time": "10:00",
                "end_time": "11:30",
                "title": "🌇 시부야 스카이 전망대",
                "type": "spot",
                "spot_key": "shibuya_sky",
                "detail": "스크램블 스퀘어 46층 230m 옥상 전망대. 도쿄 360° 파노라마 뷰.",
                "info": f"입장료 1인 {yen(2000)} | 4인 합계 {yen(8000)} | 10:00~22:30",
                "tips": "사전 예약 필수 (당일 매진 잦음). 엘리베이터 이용. 바람이 강하니 자켓 챙기기!",
            },
            {
                "time": "12:00",
                "title": "🍜 점심: 시부야 맛집",
                "type": "meal",
                "detail": "시부야역 주변 점심 식사.",
                "info": f"예산: 1인 ¥1,200~2,000 | 4인 약 {yen(6000)}",
                "tips": "추천 ① 이치란 라멘 시부야점 — 개인 칸막이 부스, 돼지뼈 라멘 ¥1,490 / 추천 ② 카츠키치 시부야점 — 돈카츠 ¥1,200~2,000, 줄 짧음",
            },
            {
                "time": "13:30",
                "title": "🚃 시부야 → 신주쿠 이동",
                "type": "transport",
                "transport_options": [
                    {
                        "method": "🚃 JR 야마노테선",
                        "duration": "약 5분 (2정거장)",
                        "cost_per_person": 160,
                        "cost_total_4": 640,
                        "cost_display": yen(640) + " (Suica, 패스 미적용)",
                        "detail": "시부야역 → 에비스 → 신주쿠역. 빠르고 편리.",
                        "recommended": True,
                    },
                    {
                        "method": "🚶 도보",
                        "duration": "약 20분 (1.6km)",
                        "cost_per_person": 0,
                        "cost_total_4": 0,
                        "cost_display": "무료",
                        "detail": "캣 스트리트 경유. 날씨 좋으면 추천.",
                        "recommended": False,
                    },
                ],
            },
            {
                "time": "14:00",
                "end_time": "16:30",
                "title": "🌳 신주쿠 교엔 정원 산책",
                "type": "spot",
                "spot_key": "shinjuku_gyoen",
                "detail": "넓은 잔디밭과 일본식·서양식 정원을 여유롭게 산책.",
                "info": f"입장료 1인 {yen(500)} | 4인 합계 {yen(2000)} | 09:00~18:00",
                "tips": "신주쿠문 입구 추천. 5월 장미원 만개. 벤치에서 쉬며 부모님 피로 회복.",
            },
            {
                "time": "16:30",
                "end_time": "18:30",
                "title": "🛍️ 신주쿠 쇼핑",
                "type": "spot",
                "spot_key": "shinjuku_omoide",
                "detail": "이세탄 백화점, 루미네 1·2, 요도바시 카메라 등 신주쿠 쇼핑 타임.",
                "info": "백화점 ~20:00 | 무료입장",
                "tips": "이세탄 지하 식품관 디저트 구경 추천. 가전·면세품은 요도바시.",
            },
            {
                "time": "18:30",
                "end_time": "20:00",
                "title": "🍢 저녁: 오모이데 요코초",
                "type": "meal",
                "detail": "신주쿠역 서쪽 출구 바로 앞 좁은 골목 야키토리 이자카야 거리.",
                "info": f"예산: 1인 ¥2,500~3,500 | 4인 약 {yen(12000)}",
                "tips": "연기 자욱한 레트로 분위기. 꼬치·맥주 조합 최고. 일찍 가야 자리 있음 (18:30 추천). 대안: 신주쿠 츠나하치 (텐푸라, 1923년 창업, ¥2,500~4,000)",
            },
            {
                "time": "20:30",
                "title": "🚃 신주쿠 → 긴자 숙소 복귀",
                "type": "transport",
                "transport_options": [
                    {
                        "method": "🚃 마루노우치선 직통",
                        "duration": "약 20분",
                        "cost_per_person": 210,
                        "cost_total_4": 840,
                        "cost_display": "클룩 3일 패스 포함",
                        "detail": "신주쿠 → 긴자 직통. 환승 없음.",
                        "recommended": True,
                    },
                    {
                        "method": "🚕 택시",
                        "duration": "약 25분",
                        "cost_per_person": None,
                        "cost_total_4": 2500,
                        "cost_display": yen(2500),
                        "detail": "저녁 식사 후 피곤하시면 택시.",
                        "recommended": False,
                    },
                ],
            },
        ],
    },
    "day3": {
        "date": "5월 3일 (토) - Day 3",
        "theme": "도쿄역 탐방 → 우에노 → 스카이라이너 → 귀국",
        "schedules": [
            {
                "time": "07:30",
                "title": "🏨 체크아웃 & 짐 보관",
                "type": "hotel",
                "detail": "체크아웃 후 호텔 프론트에 짐 보관 (무료). GOODLUG 이용 시 짐은 이미 공항으로 발송됨.",
                "info": "GOODLUG: 전날 저녁~당일 오전 픽업 → 나리타 공항 수령 서비스 (₩25,500)",
                "tips": "GOODLUG 사용 시 Day 3 내내 짐 없이 여행! 사전 예약 필수.",
            },
            {
                "time": "08:00",
                "title": "🚶 긴자 → 도쿄역 (도보 or 전철)",
                "type": "transport",
                "transport_options": [
                    {
                        "method": "🚶 도보",
                        "duration": "약 15분 (1.2km)",
                        "cost_per_person": 0,
                        "cost_total_4": 0,
                        "cost_display": "무료",
                        "detail": "마루노우치 대로 따라 15분. 아침 산책 겸 추천.",
                        "recommended": True,
                    },
                    {
                        "method": "🚃 히비야선 1정거장",
                        "duration": "약 3분",
                        "cost_per_person": 180,
                        "cost_total_4": 720,
                        "cost_display": "클룩 패스 포함",
                        "detail": "긴자역 → 히비야역 → 도보 5분.",
                        "recommended": False,
                    },
                ],
            },
            {
                "time": "08:30",
                "end_time": "10:30",
                "title": "🏛️ 도쿄역 마루노우치 + 그란스타",
                "type": "spot",
                "spot_key": "tokyo_station",
                "detail": "1914년 붉은 벽돌 역사 외관 감상 → 그란스타 도쿄 지하 식품관·라멘 스트리트 구경.",
                "info": "입장료 무료 | 그란스타 07:00~22:00",
                "tips": "도쿄 바나나, 긴자 쇼콜라, 갓파바시 과자 — 귀국 선물 여기서 마무리!",
            },
            {
                "time": "10:30",
                "title": "🚃 도쿄역 → 우에노 이동",
                "type": "transport",
                "transport_options": [
                    {
                        "method": "🚃 JR 야마노테선 / 게이힌토호쿠선",
                        "duration": "약 8분 (3정거장)",
                        "cost_per_person": 160,
                        "cost_total_4": 640,
                        "cost_display": yen(640) + " (Suica, 패스 미적용)",
                        "detail": "도쿄역 → 우에노역. 빠르고 직통.",
                        "recommended": True,
                    },
                    {
                        "method": "🚕 택시",
                        "duration": "약 10분",
                        "cost_per_person": None,
                        "cost_total_4": 1500,
                        "cost_display": yen(1500),
                        "detail": "짐 있을 경우 택시가 편리.",
                        "recommended": False,
                    },
                ],
            },
            {
                "time": "11:00",
                "end_time": "13:00",
                "title": "🛍️ 아메요코 기념품 쇼핑 & 점심",
                "type": "spot",
                "spot_key": "ameyoko",
                "detail": "아메요코에서 마지막 기념품 구매 + 점심 식사.",
                "info": "입장료 무료",
                "tips": "추천 점심 ① 도쿄역 라멘 스트리트 (돌아오는 길) — 8개 명점 ¥1,200~1,800 / ② 아메요코 카이센동 — 신선 해산물 덮밥 ¥1,500~2,500",
            },
            {
                "time": "13:00",
                "title": "🏨 호텔로 돌아가 짐 픽업",
                "type": "hotel",
                "detail": "GOODLUG 미이용 시: 우에노 → 긴자(히비야선 10분) → 짐 픽업 → 다시 우에노로.",
                "info": "GOODLUG 이용 시 이 단계 생략! 공항에서 수령.",
                "tips": "시간 여유 있으면 긴자 주변 마지막 쇼핑 가능.",
            },
            {
                "time": "14:30",
                "title": "🚃 우에노역 → 나리타 (스카이라이너)",
                "type": "transport",
                "detail": "케이세이우에노역에서 스카이라이너 탑승. 나리타공항 15:11 도착.",
                "info": "클룩 패스 사용 (왕복 포함). 좌석 지정 미리 해두기!",
                "tips": "15:11 나리타 도착 → 약 3시간 45분 여유. 면세점 쇼핑 충분히 가능.",
                "transport_options": [
                    {
                        "method": "🚃 스카이라이너 (Skyliner)",
                        "duration": "41분",
                        "cost_per_person": None,
                        "cost_total_4": 0,
                        "cost_display": "클룩 패스 포함",
                        "detail": "케이세이우에노 → 나리타공항 제1터미널. 지정석 쾌적.",
                        "recommended": True,
                    },
                ],
            },
            {
                "time": "15:15",
                "title": "🛫 나리타 공항 도착 & 출국 수속",
                "type": "transport",
                "detail": "도착 후 체크인 카운터 → 보안검색 → 출국 심사. 면세점 쇼핑.",
                "info": "출발 3시간 전 도착 목표. 면세점 마지막 쇼핑 타임!",
                "tips": "GOODLUG 이용 시 카운터에서 짐 수령 후 위탁. 면세품 적립 잊지 말기.",
            },
            {
                "time": "18:55",
                "end_time": "21:45",
                "title": "✈️ 나리타 → 인천 귀국",
                "type": "transport",
                "detail": "나리타공항 18:55 출발 → 인천공항 21:45 도착.",
                "info": "수고하셨습니다! 즐거운 여행 되세요 🎌",
            },
        ],
    },
}

# ---------- 준비물 체크리스트 ----------
CHECKLIST_BOOK = [
    {
        "title": "스카이라이너 + 도쿄 메트로 3일 패스",
        "price": "₩52,000 / 인 (4인 ₩208,000)",
        "desc": "공항 ↔ 우에노 스카이라이너 왕복 + 도쿄 메트로 3일 무제한 포함",
        "url": "https://www.klook.com/ko/activity/1410-skyliner-tokyo/",
        "tips": "출발 전 반드시 예약! QR코드로 개찰구 통과. 지정석이므로 승차 전 좌석 지정.",
        "urgent": True,
    },
    {
        "title": "짐 배송 서비스 (GOODLUG)",
        "price": "₩25,500",
        "desc": "긴자 숙소 → 나리타 공항 사전 배송. Day 3 짐 없이 가볍게 여행 가능",
        "url": "https://www.goodlugg.com/delivery/guide?city=31",
        "tips": "출발 1~2일 전 예약 필수. Day 3 아침에 픽업 → 나리타에서 수령. 강력 추천!",
        "urgent": True,
    },
    {
        "title": "이심 (eSIM) 예약",
        "price": "서비스별 상이",
        "desc": "일본 데이터 전용 eSIM. 현지 유심 없이 즉시 데이터 사용 가능",
        "url": "https://www.usimsa.com/partners/130406",
        "tips": "출발 하루 전 활성화 권장. 4인 각자 또는 핫스팟 공유 방식 선택.",
        "urgent": True,
    },
    {
        "title": "시부야 스카이 사전 예약",
        "price": f"¥2,000/인 (4인 {yen(8000)})",
        "desc": "Day 2 오전 10:00 시부야 스카이 전망대. 당일 매진 잦음",
        "url": "https://www.shibuya-sky.com/",
        "tips": "공식 사이트에서 사전 예약 필수. 날짜·시간 지정.",
        "urgent": False,
    },
]

PACKING_LIST = [
    ("여권 + 사본", "필수! 사본은 여권과 별도 보관"),
    ("엔화 현금", "1인 ¥30,000~50,000 준비 (소규모 가게 현금 필요)"),
    ("신용카드", "해외결제 되는 카드 1~2장 (비자/마스터)"),
    ("편한 운동화", "하루 8,000~12,000보 예상. 발이 편한 신발 필수"),
    ("우산 / 우비", "5월 도쿄 간헐적 비. 접이식 우산 추천"),
    ("선크림", "5월 자외선 강함. SPF 50 이상 권장"),
    ("보조배터리", "하루 종일 지도 앱 사용으로 배터리 소모 큼"),
    ("상비약", "두통약, 소화제, 밴드 (일본 약국 언어 장벽)"),
    ("여행자 보험", "출발 전 가입 (의료비 일본 매우 비쌈)"),
    ("Visit Japan Web", "앱 사전 등록으로 입국 심사 시간 단축"),
    ("Google Maps 오프라인", "도쿄 지도 미리 다운로드"),
    ("Suica 앱 or 실물", "JR 노선 및 편의점 결제용 (클룩 패스는 메트로 전용)"),
]


# ============================================================
# 헤더
# ============================================================
st.markdown("""
<div class="main-header">
    <h1>🗼 도쿄 2박 3일 가족 여행 플래너</h1>
    <p>2026.05.01 (목) ~ 05.03 (토) | 4인 가족 (부모님 + 누나 + 본인) | 나리타 ↔ 우에노 스카이라이너</p>
</div>
""", unsafe_allow_html=True)


# ============================================================
# 탭 구성
# ============================================================
tab0, tab1, tab2, tab3 = st.tabs([
    "📋 출발 전 준비",
    "🗓️ 일자별 상세 일정",
    "🗺️ 여행지 지도",
    "🏨 숙소 추천",
])


# ============================================================
# Tab 0: 출발 전 준비
# ============================================================
with tab0:
    st.markdown("### 📋 출발 전 예약 / 준비 체크리스트")
    st.markdown("---")

    st.markdown("#### ✅ 사전 예약 필수 항목")
    for item in CHECKLIST_BOOK:
        border_color = "#ee5a24" if item["urgent"] else "#3498db"
        badge = "🔴 **긴급 예약**" if item["urgent"] else "🔵 **예약 필요**"
        with st.expander(f"{badge} &nbsp; **{item['title']}** — {item['price']}", expanded=item["urgent"]):
            st.markdown(f"**내용:** {item['desc']}")
            st.info(f"💡 **TIP:** {item['tips']}")
            st.markdown(f"🔗 [예약 바로가기]({item['url']})")

    st.markdown("---")
    st.markdown("#### 🧳 짐 챙김 목록")

    col_a, col_b = st.columns(2)
    half = len(PACKING_LIST) // 2
    for i, (item_name, desc) in enumerate(PACKING_LIST):
        col = col_a if i < half else col_b
        with col:
            st.markdown(f"- **{item_name}** — {desc}")

    st.markdown("---")
    st.markdown("#### 💱 환율 참고 (시뮬레이션)")
    ex_col1, ex_col2, ex_col3 = st.columns(3)
    with ex_col1:
        st.metric("1 JPY", f"≈ {JPY_TO_KRW} KRW")
    with ex_col2:
        st.metric("¥10,000", f"≈ ₩{int(10000 * JPY_TO_KRW):,}")
    with ex_col3:
        st.metric("¥50,000", f"≈ ₩{int(50000 * JPY_TO_KRW):,}")
    st.caption("⚠️ 실제 환율은 출발 전 확인하세요.")


# ============================================================
# Tab 1: 일자별 상세 일정
# ============================================================
with tab1:
    day_tabs = st.tabs([
        "📅 Day 1 (5/1 목) — 우에노·긴자",
        "📅 Day 2 (5/2 금) — 시부야·신주쿠",
        "📅 Day 3 (5/3 토) — 도쿄역·귀국",
    ])
    day_keys = ["day1", "day2", "day3"]

    for idx, day_tab in enumerate(day_tabs):
        with day_tab:
            day_data = ITINERARY[day_keys[idx]]
            st.markdown(f"### {day_data['date']}")
            st.markdown(f"**테마:** {day_data['theme']}")
            st.markdown("---")

            for item in day_data["schedules"]:
                time_display = item["time"]
                if item.get("end_time"):
                    time_display += f" ~ {item['end_time']}"

                with st.expander(f"**{item['time']}** {item['title']}", expanded=False):
                    st.markdown(f"⏰ **{time_display}**")
                    if item.get("detail"):
                        st.markdown(item["detail"])

                    if item.get("info"):
                        st.info(f"ℹ️ {item['info']}")

                    if item.get("tips"):
                        st.success(f"💡 **TIP:** {item['tips']}")

                    # 관광지 상세
                    if item.get("spot_key") and item["spot_key"] in SPOTS:
                        spot = SPOTS[item["spot_key"]]
                        cols = st.columns(3)
                        with cols[0]:
                            st.metric("운영 시간", spot["hours"])
                        with cols[1]:
                            fee_text = "무료" if spot["fee"] == 0 else yen(spot["fee"])
                            st.metric("1인 입장료", fee_text)
                        with cols[2]:
                            total_fee = "무료" if spot["fee"] == 0 else yen(spot["fee"] * 4)
                            st.metric("4인 합계", total_fee)

                    # 이동 수단 비교
                    if item.get("transport_options"):
                        st.markdown("---")
                        st.markdown("**🚗 이동 수단 비교**")
                        cols = st.columns(len(item["transport_options"]))
                        for t_idx, opt in enumerate(item["transport_options"]):
                            with cols[t_idx]:
                                if opt.get("recommended"):
                                    st.markdown("⭐ **추천!**")
                                st.markdown(f"**{opt['method']}**")
                                st.markdown(f"- ⏱️ 소요: **{opt['duration']}**")
                                st.markdown(f"- 💰 4인: **{opt['cost_display']}**")
                                st.caption(opt["detail"])


# ============================================================
# Tab 2: 지도
# ============================================================
with tab2:
    st.markdown("### 🗺️ 3일간 방문 장소 지도")
    st.markdown("마커를 클릭하면 장소 정보를 확인할 수 있습니다.")

    col_l1, col_l2, col_l3, col_l4 = st.columns(4)
    with col_l1:
        st.markdown("🔴 **1일차** (5/1)")
    with col_l2:
        st.markdown("🔵 **2일차** (5/2)")
    with col_l3:
        st.markdown("🟢 **3일차** (5/3)")
    with col_l4:
        st.markdown("🟠 **숙소** (긴자)")

    m = folium.Map(location=[35.68, 139.75], zoom_start=12, tiles="cartodbpositron")

    day_spots = {
        "day1": {
            "color": "red",
            "label": "1일차 (5/1 목)",
            "spots": ["narita_airport", "ueno_park", "ameyoko", "ginza"],
        },
        "day2": {
            "color": "blue",
            "label": "2일차 (5/2 금)",
            "spots": ["shibuya", "shibuya_sky", "shinjuku_gyoen", "shinjuku_omoide"],
        },
        "day3": {
            "color": "green",
            "label": "3일차 (5/3 토)",
            "spots": ["tokyo_station", "ueno_park", "narita_airport"],
        },
    }

    for day_key, info in day_spots.items():
        for spot_key in info["spots"]:
            spot = SPOTS[spot_key]
            fee_text = "무료" if spot["fee"] == 0 else f"¥{spot['fee']:,}"
            popup_html = f"""
            <div style="min-width:200px;font-family:sans-serif;">
                <b style="font-size:14px;">{spot['name']}</b><br>
                <span style="color:#666;font-size:12px;">{info['label']}</span>
                <hr style="margin:4px 0;">
                <b>운영:</b> {spot['hours']}<br>
                <b>입장료:</b> {fee_text}<br>
                <p style="font-size:12px;color:#444;margin-top:4px;">{spot['desc']}</p>
            </div>
            """
            folium.Marker(
                location=[spot["lat"], spot["lon"]],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=spot["name"],
                icon=folium.Icon(color=info["color"], icon="info-sign"),
            ).add_to(m)

    # 숙소 마커
    for hotel in HOTELS:
        popup_html = f"""
        <div style="min-width:200px;font-family:sans-serif;">
            <b style="font-size:14px;">🏨 {hotel['name']}</b><br>
            <span style="color:#666;">{hotel['area']}</span>
            <hr style="margin:4px 0;">
            <b>1박:</b> ₩{hotel['price_per_night_krw']:,}<br>
            <b>접근성:</b> {hotel['access']}
        </div>
        """
        folium.Marker(
            location=[hotel["lat"], hotel["lon"]],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"🏨 {hotel['name']}",
            icon=folium.Icon(color="orange", icon="home"),
        ).add_to(m)

    # 경로선 Day 1
    day1_coords = [
        [SPOTS["narita_airport"]["lat"], SPOTS["narita_airport"]["lon"]],
        [SPOTS["ueno_park"]["lat"], SPOTS["ueno_park"]["lon"]],
        [SPOTS["ameyoko"]["lat"], SPOTS["ameyoko"]["lon"]],
        [SPOTS["ginza"]["lat"], SPOTS["ginza"]["lon"]],
    ]
    folium.PolyLine(day1_coords, color="red", weight=3, opacity=0.6, dash_array="8").add_to(m)

    # 경로선 Day 2
    day2_coords = [
        [SPOTS["ginza"]["lat"], SPOTS["ginza"]["lon"]],
        [SPOTS["shibuya"]["lat"], SPOTS["shibuya"]["lon"]],
        [SPOTS["shinjuku_gyoen"]["lat"], SPOTS["shinjuku_gyoen"]["lon"]],
        [SPOTS["shinjuku_omoide"]["lat"], SPOTS["shinjuku_omoide"]["lon"]],
        [SPOTS["ginza"]["lat"], SPOTS["ginza"]["lon"]],
    ]
    folium.PolyLine(day2_coords, color="blue", weight=3, opacity=0.6, dash_array="8").add_to(m)

    # 경로선 Day 3
    day3_coords = [
        [SPOTS["ginza"]["lat"], SPOTS["ginza"]["lon"]],
        [SPOTS["tokyo_station"]["lat"], SPOTS["tokyo_station"]["lon"]],
        [SPOTS["ueno_park"]["lat"], SPOTS["ueno_park"]["lon"]],
        [SPOTS["narita_airport"]["lat"], SPOTS["narita_airport"]["lon"]],
    ]
    folium.PolyLine(day3_coords, color="green", weight=3, opacity=0.6, dash_array="8").add_to(m)

    st_folium(m, height=600, use_container_width=True)


# ============================================================
# Tab 3: 숙소 추천
# ============================================================
with tab3:
    st.markdown("### 🏨 긴자 지역 숙소 추천 (4인 가족 기준)")
    st.markdown("**조건:** 긴자 지역 | 방 2개 | 우에노(스카이라이너) 접근 편리 | 2박 합계 ₩100만 이하")
    st.markdown("---")

    for h_idx, hotel in enumerate(HOTELS):
        is_best = h_idx == 1  # 도미인이 가성비 베스트
        with st.container():
            col_info, col_price = st.columns([3, 1])

            with col_info:
                badge = "⭐ **가성비 추천** " if is_best else ""
                st.markdown(f"#### {badge}{hotel['name']} {hotel['star']}")
                st.caption(f"{hotel['name_jp']} | {hotel['area']} 지역")

                st.markdown(f"**객실 타입:** {hotel['room_type']}")
                st.markdown(f"**접근성:** {hotel['access']}")
                st.markdown(f"**공항 가는 법:** {hotel['airport_access']}")

                st.markdown("**추천 이유:**")
                for pro in hotel["pros"]:
                    st.markdown(f"- ✅ {pro}")

            with col_price:
                st.metric("1박 요금", f"₩{hotel['price_per_night_krw']:,}")
                saving_pct = (1000000 - hotel["total_2nights_krw"]) / 1000000 * 100
                st.metric(
                    "2박 합계",
                    f"₩{hotel['total_2nights_krw']:,}",
                    delta=f"₩100만 대비 {saving_pct:.0f}% 절약",
                    delta_color="normal",
                )
                if hotel["total_2nights_krw"] <= 650000:
                    st.success("💰 가성비 최고!")
                elif hotel["total_2nights_krw"] <= 1000000:
                    st.info("✅ 예산 이내")

            st.markdown("---")

    st.markdown("### 💰 예상 전체 비용 요약 (4인)")

    cost_cols = st.columns(3)
    with cost_cols[0]:
        st.markdown("**✈️ 이동·교통**")
        st.markdown(f"- 스카이라이너 왕복: **₩208,000** (4인)")
        st.markdown(f"- 메트로 3일 패스: **포함**")
        st.markdown(f"- JR 별도 이용: **약 {yen(3000)}**")
        st.markdown(f"- 택시 예비비: **약 {yen(5000)}**")

    with cost_cols[1]:
        st.markdown("**🎫 입장료**")
        st.markdown(f"- 시부야 스카이: **{yen(8000)}** (4인)")
        st.markdown(f"- 신주쿠 교엔: **{yen(2000)}** (4인)")
        st.markdown(f"- 그 외 관광지: **무료**")

    with cost_cols[2]:
        st.markdown("**🍽️ 식비 (4인 3일)**")
        st.markdown(f"- 하루 약 {yen(20000)}~{yen(25000)}")
        st.markdown(f"- 3일 합계: **약 {yen(65000)}**")
        st.markdown(f"- 짐 배송(GOODLUG): **₩25,500**")


# ============================================================
# 사이드바
# ============================================================
with st.sidebar:
    st.markdown("## 📋 여행 요약")
    st.markdown("---")

    st.markdown("**✈️ 출국**")
    st.markdown("5/1 (목) 인천 08:35 → 나리타 11:00")

    st.markdown("**✈️ 귀국**")
    st.markdown("5/3 (토) 나리타 18:55 → 인천 21:45")

    st.markdown("---")
    st.markdown("**🚃 스카이라이너**")
    st.markdown("우에노 ↔ 나리타 **41분** (클룩 패스)")

    st.markdown("---")
    st.markdown("**📍 3일 경로 요약**")
    st.markdown("Day 1: 나리타 → **우에노** → 긴자")
    st.markdown("Day 2: **시부야** → **신주쿠**")
    st.markdown("Day 3: **도쿄역** → 우에노 → 나리타")

    st.markdown("---")
    st.markdown("**👨‍👩‍👧‍👦 여행 인원**")
    st.markdown("4명 (50~60대 부모님 + 누나 + 본인)")

    st.markdown("---")
    st.markdown("**📱 필수 앱**")
    st.markdown("- **Google Maps** — 길 찾기")
    st.markdown("- **Visit Japan Web** — 입국 사전 등록")
    st.markdown("- **Suica 앱** — 교통카드")
    st.markdown("- **Papago** — 실시간 번역")
    st.markdown("- **GOODLUG** — 짐 배송")

    st.markdown("---")
    st.markdown(f"**💱 환율** 1 JPY ≈ {JPY_TO_KRW} KRW")
    st.caption("⚠️ 요금·운영시간은 참고용입니다. 여행 전 재확인하세요.")
