import json
from pathlib import Path

import folium
import streamlit as st
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static

DATA_FILE = Path(__file__).parent / "data" / "trash_locations.json"

@st.cache_data
def load_trash_data():
    if not DATA_FILE.exists():
        return []

    with DATA_FILE.open("r", encoding="utf-8") as fp:
        data = json.load(fp)

    records = []
    for item in data.get("records", []):
        try:
            lat_str = item.get("위도", "0")
            lon_str = item.get("경도", "0")
            if not lat_str or not lon_str: continue
            lat = float(lat_str)
            lon = float(lon_str)
            if lat == 0 or lon == 0: continue
        except ValueError:
            continue

        records.append({
            "설치장소명": item.get("설치장소명", "-"),
            "시도명": item.get("시도명", "-") or "-",
            "시군구명": item.get("시군구명", "-") or "-",
            "소재지도로명주소": item.get("소재지도로명주소", "-") or "-",
            "소재지지번주소": item.get("소재지지번주소", "-") or "-",
            "세부위치": item.get("세부위치", "-") or "-",
            "휴지통종류": item.get("휴지통종류", "-") or "-",
            "관리기관명": item.get("관리기관명", "-") or "-",
            "관리기관전화번호": item.get("관리기관전화번호", "-") or "-",
            "위도": lat,
            "경도": lon,
        })

    return records


def build_popup(record):
    address = record['소재지도로명주소'] or record['소재지지번주소'] or '-'
    return f"""
        <div style='font-size:0.9rem; line-height:1.4; width: 200px;'>
            <div style='font-weight:700; margin-bottom:0.35rem;'>{record['설치장소명']}</div>
            <b>종류:</b> {record['휴지통종류']}<br>
            <b>위치:</b> {record['시도명']} {record['시군구명']}<br>
            <b>주소:</b> {address}<br>
            <b>관리:</b> {record['관리기관명']}
        </div>
    """


def run_map_tab():
    st.write("")
    st.markdown('<div class="section-title">🗺️ 내 근처 수거 인프라 지도</div>', unsafe_allow_html=True)
    st.write("전국 공공 데이터 기반의 수거 지점 지도입니다.")

    data = load_trash_data()
    if not data:
        st.warning("휴지통 위치 데이터 파일을 찾을 수 없습니다.")
        return

    # 필터링 UI
    col1, col2 = st.columns(2)
    with col1:
        provinces = sorted({record["시도명"] for record in data if record["시도명"]})
        selected_province = st.selectbox("시도 선택", ["전체"] + provinces, index=0)
    
    filtered = [record for record in data if selected_province == "전체" or record["시도명"] == selected_province]

    with col2:
        districts = sorted({record["시군구명"] for record in filtered if record["시군구명"]})
        selected_district = st.selectbox("시군구 선택", ["전체"] + districts, index=0)
    
    if selected_district != "전체":
        filtered = [record for record in filtered if record["시군구명"] == selected_district]

    # 너무 많은 데이터는 브라우저를 멈추게 하므로 제한
    MAX_MARKERS = 1000
    display_data = filtered
    if len(filtered) > MAX_MARKERS:
        st.info(f"결과가 너무 많아 상위 {MAX_MARKERS}개만 표시합니다. 지역을 더 좁혀보세요.")
        display_data = filtered[:MAX_MARKERS]

    st.markdown(f"**표시 중:** {len(display_data)}개 / **전체 검색:** {len(filtered)}개")

    if not display_data:
        st.info("선택한 지역에 해당하는 데이터가 없습니다.")
        return

    # 지도 중심 계산
    avg_lat = sum(record["위도"] for record in display_data) / len(display_data)
    avg_lon = sum(record["경도"] for record in display_data) / len(display_data)

    # 지도 생성 (가장 표준적인 OpenStreetMap 사용)
    folium_map = folium.Map(
        location=[avg_lat, avg_lon],
        zoom_start=13,
    )
    
    marker_cluster = MarkerCluster().add_to(folium_map)

    for record in display_data:
        popup = folium.Popup(build_popup(record), max_width=250)
        folium.Marker(
            location=[record["위도"], record["경도"]],
            popup=popup,
            tooltip=record["설치장소명"],
            icon=folium.Icon(color="green", icon="info-sign"),
        ).add_to(marker_cluster)

    # 렌더링 (folium_static이 배포 환경에서 더 안정적임)
    folium_static(folium_map, width=700, height=500)

    st.markdown("💡 **Tip**: 지도를 확대하거나 마커를 클릭하여 상세 정보를 확인하세요.")
