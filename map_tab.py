import json
from pathlib import Path

import folium
import streamlit as st
from folium.plugins import MarkerCluster
from streamlit.components.v1 import html

DATA_FILE = Path(__file__).parent / "data" / "전국휴지통표준데이터.json"


def load_trash_data():
    if not DATA_FILE.exists():
        return []

    with DATA_FILE.open("r", encoding="utf-8") as fp:
        data = json.load(fp)

    records = []
    for item in data.get("records", []):
        try:
            lat = float(item.get("위도", "0") or "0")
            lon = float(item.get("경도", "0") or "0")
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
        <div style='font-size:0.9rem; line-height:1.4; max-width: 280px; white-space: normal; word-break: break-word; overflow-wrap: anywhere;'>
            <div style='font-weight:700; margin-bottom:0.35rem;'>{record['설치장소명']}</div>
            <div style='display:grid; grid-template-columns: 70px 1fr; gap: 2px 6px; align-items: start;'>
                <div style='font-weight:700;'>종류:</div><div>{record['휴지통종류']}</div>
                <div style='font-weight:700;'>위치:</div><div>{record['시도명']} {record['시군구명']}</div>
            </div>
            <div style='margin-top:0.4rem;'>
                <div style='font-weight:700;'>주소:</div>
                <div>{address}</div>
            </div>
            <div style='display:grid; grid-template-columns: 70px 1fr; gap: 2px 6px; margin-top:0.35rem;'>
                <div style='font-weight:700;'>관리기관:</div><div>{record['관리기관명']}</div>
                <div style='font-weight:700;'>전화:</div><div>{record['관리기관전화번호']}</div>
            </div>
        </div>
    """


def run_map_tab():
    st.write("")
    st.markdown('<div class="section-title">🗺️ 내 근처 수거 인프라 지도</div>', unsafe_allow_html=True)
    st.write("전국 공공 휴지통 위치 데이터를 기반으로 가까운 수거 지점을 지도로 보여줍니다.")

    data = load_trash_data()
    if not data:
        st.warning("휴지통 위치 데이터 파일을 찾을 수 없습니다.")
        return

    provinces = sorted({record["시도명"] for record in data if record["시도명"]})
    selected_province = st.selectbox("시도/광역시 선택", ["전체"] + provinces, index=0)

    filtered = [record for record in data if selected_province == "전체" or record["시도명"] == selected_province]

    if selected_province != "전체":
        districts = sorted({record["시군구명"] for record in filtered if record["시군구명"]})
        selected_district = st.selectbox("시군구 선택", ["전체"] + districts, index=0)
        if selected_district != "전체":
            filtered = [record for record in filtered if record["시군구명"] == selected_district]

    st.markdown(f"**검색 결과:** {len(filtered)}개 휴지통 위치 표시")

    if not filtered:
        st.info("선택한 지역에 해당하는 휴지통 데이터가 없습니다.")
        return

    avg_lat = sum(record["위도"] for record in filtered) / len(filtered)
    avg_lon = sum(record["경도"] for record in filtered) / len(filtered)

    folium_map = folium.Map(
        location=[avg_lat, avg_lon],
        zoom_start=12,
        tiles="CartoDB positron",
        attr="&copy; OpenStreetMap contributors &copy; CARTO",
    )
    marker_cluster = MarkerCluster().add_to(folium_map)

    type_colors = {
        "일반쓰레기": "blue",
        "재활용쓰레기": "green",
        "음식물쓰레기": "orange",
        "기타": "gray",
    }

    for record in filtered:
        marker_color = type_colors.get(record["휴지통종류"], "cadetblue")
        popup = folium.Popup(
            build_popup(record),
            max_width=320,
            min_width=280,
        )
        folium.Marker(
            location=[record["위도"], record["경도"]],
            popup=popup,
            tooltip=record["설치장소명"],
            icon=folium.Icon(color=marker_color, icon="trash", prefix="fa"),
        ).add_to(marker_cluster)

    html(folium_map._repr_html_(), height=650)

    st.markdown(
        """
        **사용 팁**
        - 지도에서 마커를 클릭하면 휴지통 상세 정보를 확인할 수 있습니다.
        - 지역을 좁혀서 검색하면 더 빠르게 결과를 찾을 수 있습니다.
        - 필요하면 본 데이터와 연동해 근처 수거함 네비게이션까지 확장하세요.
        """
    )
