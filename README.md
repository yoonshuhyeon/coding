# 🍀 그린가이드 (Green Guide)

지속 가능한 삶을 위한 맞춤형 분리수거 플랫폼입니다. 우리 지역의 세부 규정부터 정확한 수거함 안내까지 한눈에 조회할 수 있습니다.

## ✨ 주요 기능

1.  **✍️ 분리배출 가이드**: 품목별(플라스틱, 종이, 금속, 유리 등) 올바른 분리배출 방법을 안내합니다.
2.  **📍 지역별 제도 안내**: 행정구역별 생활쓰레기, 음식물 쓰레기, 재활용품 배출 일정 및 방법을 검색할 수 있습니다.
3.  **📷 분리수거 인식**: AI(HOG 특징 기반 RandomForest)를 활용하여 촬영한 사진 속 품목을 분석하고 배출 가이드를 제공합니다.
4.  **🗺️ 주변 분리수거함 지도**: 공공 데이터를 기반으로 내 주변의 공공 휴지통 및 수거함 위치를 지도로 보여줍니다.

## 🚀 시작하기

### 설치 방법

```bash
# 저장소 복제
git clone https://github.com/사용자명/그린가이드.git
cd 그린가이드

# 가상환경 생성 및 활성화 (권장)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 실행 방법

```bash
streamlit run greenguide.py
```

## 📂 프로젝트 구조

- `greenguide.py`: 메인 애플리케이션 실행 파일
- `recognition_tab.py`: AI 인식 탭 모듈
- `map_tab.py`: 지도 서비스 탭 모듈
- `data/`: 지역별 배출 정보 및 수거함 위치 데이터 (CSV, JSON)
- `models/`: 학습된 AI 모델 및 라벨링 데이터
- `train/`: AI 모델 학습 스크립트
- `requirements.txt`: 프로젝트 의존성 목록

## 🛠 사용 기술

- **Frontend/App**: Streamlit
- **Data Analysis**: Pandas, Numpy
- **AI/ML**: Scikit-learn, Scikit-image (HOG Features), Joblib
- **Visualization**: Folium, Streamlit-folium

## 📄 라이선스

이 프로젝트는 프로토타입 목적으로 제작되었습니다.
데이터 출처: 공공데이터포털
