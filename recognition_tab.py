import streamlit as st
import tensorflow as tf
from PIL import Image
import numpy as np
import os

# 모델 및 라벨 로드
@st.cache_resource
def load_ai_model_cnn():
    model_path = "models/waste_model_cnn.h5"
    label_path = "models/labels.txt"
    
    if os.path.exists(model_path) and os.path.exists(label_path):
        # Keras 모델 로드
        try:
            model = tf.keras.models.load_model(model_path)
            with open(label_path, "r", encoding="utf-8") as f:
                labels = [line.strip() for line in f.readlines()]
            return model, labels
        except Exception as e:
            st.error(f"모델 로드 중 오류 발생: {e}")
            return None, None
    return None, None

def run_recognition_tab():
    st.write("")
    st.markdown("""
        <div class="camera-section">
            <div class="camera-header-title">📷 스마트 AI 품목 분석기 (CNN)</div>
            <p style="font-size: 0.9rem; color: #4A5A4E; margin-bottom: 0rem; line-height: 1.5;">
                MobileNetV2 딥러닝 엔진이 적용된 고정밀 분석기입니다. 사진을 촬영하거나 업로드하여 올바른 배출 방법을 확인하세요.
            </p>
        </div>
    """, unsafe_allow_html=True)

    model, labels = load_ai_model_cnn()

    col1, col2 = st.columns([1, 1])
    with col1:
        camera_file = st.camera_input("실시간 카메라 촬영")
    with col2:
        uploaded_image = st.file_uploader("사진 파일 선택 (JPG, PNG)", type=["jpg", "jpeg", "png"])

    active_image = camera_file if camera_file is not None else uploaded_image
    
    if active_image:
        if model is None:
            st.info("💡 CNN 모델 학습 파일을 찾을 수 없습니다. `train/train_model_cnn.py`를 실행하여 모델을 먼저 학습시켜 주세요.")
            st.image(active_image, caption="업로드된 이미지", use_container_width=True)
        else:
            # 이미지 로드 및 전처리
            img = Image.open(active_image).convert("RGB")
            st.image(img, caption="분석 대상 이미지", use_container_width=True)
            
            with st.spinner("딥러닝 신경망이 이미지를 정밀 분석 중입니다..."):
                # CNN 모델 입력 규격에 맞게 전처리 (224x224, normalized)
                img_resized = img.resize((224, 224))
                img_array = np.array(img_resized) / 255.0  # 스케일링
                img_array = np.expand_dims(img_array, axis=0)  # 배치 차원 추가
                
                # 예측
                predictions = model.predict(img_array)
                class_idx = np.argmax(predictions[0])
                confidence = 100 * predictions[0][class_idx]
                result_label = labels[class_idx]

            # 결과 표시
            st.success(f"분석 결과: **{result_label}** (신뢰도: {confidence:.2f}%)")
            
            # 품목별 가이드 매칭
            guides = {
                "plastic": "내용물을 비우고 라벨을 제거한 뒤 배출하세요.",
                "paper": "테이프나 스프링 등 이물질을 제거하고 납작하게 펴서 배출하세요.",
                "glass": "병뚜껑을 제거하고 깨끗이 씻어서 배출하세요. 깨진 유리는 신문지에 싸서 일반 쓰레기로 버리세요.",
                "can": "내용물을 비우고 캔 고리 등을 분리하여 압착 후 배출하세요.",
                "cardboard": "박스의 테이프와 송장을 제거하고 펼쳐서 배출하세요.",
                "metal": "캔류와 고철류를 구분하여 이물질 없이 배출하세요."
            }
            
            # 소문자로 변환하여 매칭 시도
            guide_text = guides.get(result_label.lower(), "해당 품목의 상세 배출 가이드는 '분리배출 가이드' 탭을 참고하세요.")
            
            st.markdown(f"""
                <div style="background-color: #EBF2ED; padding: 1.2rem; border-radius: 12px; border-left: 5px solid #0F2A17;">
                    <div style="font-weight: 700; color: #0F2A17; margin-bottom: 5px;">✅ 올바른 배출 방법</div>
                    <div style="color: #2F3E33; font-size: 0.95rem;">{guide_text}</div>
                </div>
            """, unsafe_allow_html=True)
