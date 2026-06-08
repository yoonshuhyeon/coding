import streamlit as st
import pandas as pd
from recognition_tab import run_recognition_tab
from map_tab import run_map_tab

@st.cache_data
def load_waste_data():
    try:
        # 다양한 인코딩 시도 (EUC-KR, CP949)
        df = pd.read_csv("data/생활쓰레기배출정보.csv", encoding="cp949")
        # 데이터 정제: 시도명 + 시군구명을 합쳐 지역명 생성
        df['지역명'] = df['시도명'] + " " + df['시군구명']
        return df
    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
        return None

waste_df = load_waste_data()

st.set_page_config(
    page_title="쓰담쓰담",
    page_icon="🌿",
    layout="centered"  
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght=300;400;500;700&family=Playfair+Display:ital,wght@0,600;1,600&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Noto Sans KR', sans-serif;
        background-color: #F8FAF8;
        color: #2F3E33;
    }

    * {
        transition: all 0.25s ease-in-out;
    }

    [data-testid="stExpander"] {
        border-radius: 8px !important;
        margin-bottom: 0.8rem !important;
    }

    [data-testid="stExpander"] summary {
        background-color: #EBF2ED !important;
        padding: 0.5rem 0.8rem !important;
    }

    [data-testid="stExpander"] summary p,
    [data-testid="stExpander"] summary span,
    [data-testid="stExpander"] summary svg {
        color: #0F2A17 !important;
        fill: #0F2A17 !important;
        font-weight: 500 !important;
    }

    [data-testid="stExpander"] details[open] summary {
        background-color: #0F2A17 !important;
    }

    [data-testid="stExpander"] details[open] summary p,
    [data-testid="stExpander"] details[open] summary span {
        color: #FFFFFF !important;
    }
    
    [data-testid="stExpander"] details[open] summary svg {
        fill: #FFFFFF !important;
        color: #FFFFFF !important;
    }

    [data-testid="stExpander"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stExpander"] [data-testid="stMarkdownContainer"] li,
    [data-testid="stExpander"] [data-testid="stMarkdownContainer"] span {
        color: var(--text-color, #2F3E33) !important; /* 배경이 검어지면 글씨는 알아서 하얗게 변함 */
    }
    
    .header-banner {
        background: linear-gradient(135deg, #0F2A17 0%, #1A4425 100%);
        padding: 3rem 2rem;
        border-radius: 24px;
        color: #FFFFFF;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(15, 42, 23, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    .header-tag {
        font-family: 'Playfair Display', serif;
        font-style: italic;
        color: #A3C9A8;
        font-size: 1.1rem;
        font-weight: 600;
        letter-spacing: 0.1em;
        margin-bottom: 0.5rem;
    }

    .header-title {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.8rem;
        letter-spacing: -0.05em;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .header-subtitle {
        font-size: 1rem;
        font-weight: 300;
        opacity: 0.85;
        max-width: 500px;
        margin: 0 auto;
        line-height: 1.6;
    }

/* 카메라 */
    .camera-section {
        background-color: #FFFFFF;
        padding: 2rem;
        border-radius: 20px;
        border: 1px solid rgba(15, 42, 23, 0.08);
        box-shadow: 0 10px 25px rgba(15, 42, 23, 0.03);
        margin-bottom: 1.5rem;
    }

    .camera-header-title {
        font-size: 1.35rem;
        font-weight: 700;
        color: #0F2A17;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .responsive-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); /* 반응형 핵심: 좁아지면 1열, 넓어지면 2열 */
        gap: 1.2rem;
        margin-top: 1rem;
        margin-bottom: 1.5rem;
    }

    .info-card {
        background-color: #FFFFFF;
        padding: 1.8rem;
        border-radius: 18px;
        border: 1px solid rgba(15, 42, 23, 0.06);
        box-shadow: 0 4px 20px rgba(15, 42, 23, 0.02);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    .info-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 30px rgba(15, 42, 23, 0.07);
        border-color: #1A4425;
    }
    
    .card-badge {
        display: inline-block;
        background-color: #EBF2ED;
        color: #0F2A17;
        font-weight: 700;
        font-size: 0.75rem;
        padding: 0.3rem 0.8rem;
        border-radius: 30px;
        align-self: flex-start;
        margin-bottom: 1rem;
    }

    .card-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #0F2A17;
        margin-bottom: 0.8rem;
        letter-spacing: -0.02em;
    }
    
    .card-content {
        font-size: 0.95rem;
        color: #4A5A4E;
        line-height: 1.6;
    }
    
    /* 지도 */
    .map-placeholder {
        background-color: #F1F5F2;
        border: 1px solid rgba(15, 42, 23, 0.1);
        border-radius: 20px;
        padding: 4.5rem 2rem;
        text-align: center;
        color: #0F2A17;
        margin: 1.5rem 0;
        box-shadow: inset 0 2px 10px rgba(0, 0, 0, 0.01);
    }
    
    .map-icon {
        font-size: 3rem;
        margin-bottom: 1.2rem;
        filter: drop-shadow(0 4px 10px rgba(15, 42, 23, 0.1));
    }
    
    .badge-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); /* 기기 폭에 맞춰 한 줄 혹은 여러 줄 자동 배치 */
        gap: 12px;
        margin: 1.5rem 0;
    }
    
    .badge-box {
        background-color: #FFFFFF;
        border: 1px solid rgba(15, 42, 23, 0.06);
        padding: 1.2rem 0.8rem;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.01);
    }
    
    .badge-box:hover {
        background-color: #0F2A17;
        border-color: #0F2A17;
    }
    
    .badge-box:hover .badge-title {
        color: #FFFFFF;
    }
    
    .badge-box:hover .badge-desc {
        color: #A3C9A8;
    }
    
    .badge-emoji {
        font-size: 2rem;
        margin-bottom: 8px;
    }
    
    .badge-title {
        font-weight: 700;
        color: #0F2A17;
        font-size: 1rem;
    }
    
    .badge-desc {
        font-size: 0.75rem;
        color: #6B7C70;
        margin-top: 4px;
        line-height: 1.3;
    }

    .section-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #0F2A17;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
        letter-spacing: -0.03em;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: #EBF2ED;
        padding: 6px;
        border-radius: 14px;
        flex-wrap: wrap;
    }

    .stTabs [data-baseweb="tab"] {
        height: 48px;
        background-color: transparent;
        border-radius: 10px;
        color: #4A5A4E;
        font-weight: 500;
        border: none;
        padding: 0px 16px;
        font-size: 0.95rem;
        flex-grow: 1;
        text-align: center;
    }

    .stTabs [aria-selected="true"] {
        background-color: #0F2A17 !important;
        color: #FFFFFF !important;
        font-weight: 700;
        box-shadow: 0 4px 15px rgba(15, 42, 23, 0.2);
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="header-banner">
        <div class="header-tag">The green standard</div>
<<<<<<< HEAD:app.py
        <div class="header-title">🍀 쓰담쓰담 (쓰레기를 담다)</div>
=======
        <div class="header-title">🍀 쓰담쓰담 (쓰레기를 담다.)</div>
>>>>>>> 6c6a2b12b8a171be1b6e145e9b50630a56f5cc0f:greenguide.py
        <div class="header-subtitle">지속 가능한 삶을 위한 맞춤형 분리수거 플랫폼.<br>우리 지역의 세부 규정부터 정확한 수거함 안내까지 한눈에 조회하세요.</div>
    </div>
""", unsafe_allow_html=True)


tab1, tab2, tab3, tab4 = st.tabs([
    "✍️ 분리배출 가이드", 
    "📍 지역별 제도 안내", 
    "📷 분리수거 인식", 
    "🗺️ 주변 분리수거함 지도"
])

with tab1: 
    st.write("")
    st.markdown('<div class="section-title">✍️ 분리배출 핵심 4대 공식</div>', unsafe_allow_html=True)
    st.write("버리기 전 한 번의 확인이 자원의 가치를 완전히 바꿉니다.")
    
    st.markdown("""
        <div class="badge-grid">
            <div class="badge-box">
                <div class="badge-emoji">💧</div>
                <div class="badge-title">비운다</div>
                <div class="badge-desc">용기 안에 담겨있는 내용물은 깨끗이 비우고 배출합니다.</div>
            </div>
            <div class="badge-box">
                <div class="badge-emoji">✨</div>
                <div class="badge-title">헹군다</div>
                <div class="badge-desc">재활용품에 묻어있는 이물질, 음식물 등은 닦거나 한 번 헹궈서 배출합니다.</div>
            </div>
            <div class="badge-box">
                <div class="badge-emoji">🏷️</div>
                <div class="badge-title">분리한다</div>
                <div class="badge-desc">라벨 등의 다른 재질 부분은 제거하여 배출합니다.</div>
            </div>
            <div class="badge-box">
                <div class="badge-emoji">🔀</div>
                <div class="badge-title">섞지 않는다</div>
                <div class="badge-desc">소재가 서로 다른 품목은 절대 섞이지 않게 구분해 배출합니다.</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    
    with st.expander("🥤 플라스틱 · 비닐류"):
        st.write("""
        - **페트(PET):** 페트는 일반 플라스틱과 분류해서 배출해야 합니다. 페트병은 내부를 물로 깨끗이 씻은 뒤 붙은 라벨을 제거 후 압착하여 페트병 전용 수거 장소에 배출합니다.
        - **플라스틱류:** 내용물을 비운 뒤, 깨끗이 씻어서 다른 재질로 된 뚜껑, 포장지, 랩 등은 따로 제거하고 가능한 한 압착하여 배출합니다.
        - **비닐류:** 비닐류는 큰 봉투 등에 따로 모아서 배출해야 합니다. 또한 비닐 내부에 이물질이 묻어있으면 재활용이 불가하므로 이물질이 묻은 부위를 씻어내거나 닦아서 배출합니다.
        """)
        
    with st.expander("📦 종이팩 · 종이박스류"):
        st.write("""
        - **종이팩:** 내용물을 비우고 가급적 물로 헹군 뒤 반드시 일반 폐지와 혼합되지 않게 배출해야 합니다.
        - **박스류:** 상자 겉에 부착된 비닐 투명 테이프, 금속 철핀, 운송장 종이 바코드 등을 모조리 제거하고 납작하게 접어서 함께 묶거나 적재해 버려야 합니다.
        """)
        
    with st.expander("🥫 금속캔 · 고압용기류"):
        st.write("""
        - **음료 캔류:** 내용물 오염이 없도록 물로 세척한 후 발로 가볍게 밟아 형태를 부피 감소 시켜 배출합니다.
        - **압축 가스통(부탄가스 등):** 폭발 방지를 위해 반드시 통풍이 수월한 탁 트인 야외에서 전용 가스 펀처나 송곳을 이용해 측면 또는 바닥 면에 구멍을 확실하게 뚫어 잔존 가스를 방출한 후 고철류로 배출합니다.
        """)
        
    with st.expander("🫙 유리병 · 빈용기류"):
        st.write("""
        - **재사용 유리:** 병뚜껑을 제거한 뒤 내용물을 비우고 물로 깨끗이 씻어서 소매점에서 환불받거나 재활용품 버리는 곳에 배출하면 됩니다. 단, 깨진 유리병은 안전 사고를 방지하기 위해 신문지 등에 여러겹 싸서 쓰레기 봉투에 버리면 됩니다.
        - **재활용 유리:** 작은 유리병등은 유리 제품으로 분류하여 배출하고, 액자, 거울, 책상 유리 등 대형 유리 제품은 일반 대형폐기물 처리 방법에 따라 배출합니다.
        """)

with tab2:
    st.write("")
    st.markdown('<div class="section-title">🔍 내 지역 맞춤 정보 검색</div>', unsafe_allow_html=True)
    st.write("아래에서 사시는 자치구를 설정하시면 즉시 동네 특화 배출 수칙을 알려드립니다.")
    
    if waste_df is not None:
        region_list = sorted(waste_df['지역명'].unique())
        selected_region = st.selectbox(
            "행정구역 선택",
            region_list,
            index=0,
            label_visibility="collapsed"
        )
        
        # 선택된 지역 데이터 필터링
        region_data = waste_df[waste_df['지역명'] == selected_region].iloc[0]
        
        st.write("")
        
        st.markdown(f"""
            <div class="responsive-grid">
                <div class="info-card">
                    <div>
                        <span class="card-badge">생활쓰레기</span>
                        <div class="card-title">📅 배출 일정 및 방법</div>
                    </div>
                    <div class="card-content">
                        • <b>배출 요일:</b> {region_data['생활쓰레기배출요일']}<br>
                        • <b>배출 시간:</b> {region_data['생활쓰레기배출시작시각']} ~ {region_data['생활쓰레기배출종료시각']}<br>
                        • <b>배출 방법:</b> {region_data['생활쓰레기배출방법']}
                    </div>
                </div>
                <div class="info-card">
                    <div>
                        <span class="card-badge">음식물 폐기물</span>
                        <div class="card-title">📅 배출 일정 및 방법</div>
                    </div>
                    <div class="card-content">
                        • <b>배출 요일:</b> {region_data['음식물쓰레기배출요일']}<br>
                        • <b>배출 시간:</b> {region_data['음식물쓰레기배출시작시각']} ~ {region_data['음식물쓰레기배출종료시각']}<br>
                        • <b>배출 방법:</b> {region_data['음식물쓰레기배출방법']}
                    </div>
                </div>
                <div class="info-card">
                    <div>
                        <span class="card-badge">재활용품</span>
                        <div class="card-title">📅 배출 일정 및 방법</div>
                    </div>
                    <div class="card-content">
                        • <b>배출 요일:</b> {region_data['재활용품배출요일']}<br>
                        • <b>배출 시간:</b> {region_data['재활용품배출시작시각']} ~ {region_data['재활용품배출종료시각']}<br>
                        • <b>배출 방법:</b> {region_data['재활용품배출방법']}
                    </div>
                </div>
                <div class="info-card">
                    <div>
                        <span class="card-badge">문의처</span>
                        <div class="card-title">📞 관리 부서 안내</div>
                    </div>
                    <div class="card-content">
                        • <b>부서명:</b> {region_data['관리부서명']}<br>
                        • <b>전화번호:</b> {region_data['관리부서전화번호']}<br>
                        • 궁금하신 점은 해당 부서로 문의하시면 가장 정확한 안내를 받으실 수 있습니다.
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("데이터를 불러올 수 없습니다. CSV 파일을 확인해주세요.")


with tab3:
    run_recognition_tab()
        
with tab4:
    run_map_tab()

st.markdown("""
    <div style="margin-top: 5rem; text-align: center; color: #7F8E81; font-size: 0.8rem; border-top: 1px solid rgba(15, 42, 23, 0.08); padding-top: 2rem; line-height: 1.8; letter-spacing: 0.03em;">
        © 2026 그린가이드 (Green Guide). All rights reserved.<br>
        본 서비스는 전반적인 공공 에코 가이드를 돕는 프로토타입이며, 세부 규정은 해당 거주 지역의 구청 청소행정과에 문의 시 가장 정확합니다.
    </div>
""", unsafe_allow_html=True)
