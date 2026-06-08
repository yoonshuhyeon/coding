import os
import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input
from sklearn.ensemble import RandomForestClassifier
import joblib

# 1. 설정
DATA_PATH = 'dataset_small'
IMG_SIZE = (224, 224)

# 2. 특징 추출기 로드 (사전 학습된 MobileNetV2)
print("딥러닝 특징 추출기 로드 중...")
base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3), pooling='avg')

def extract_features(img_path):
    try:
        img = Image.open(img_path).convert('RGB').resize(IMG_SIZE)
        img_array = np.array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)
        
        features = base_model.predict(img_array, verbose=0)
        return features.flatten()
    except:
        return None

def train():
    X = []
    y = []
    class_names = sorted(os.listdir(DATA_PATH))
    
    print("데이터셋에서 고차원 특징 추출 중 (시간이 다소 소요될 수 있습니다)...")
    for idx, label in enumerate(class_names):
        label_path = os.path.join(DATA_PATH, label)
        if not os.path.isdir(label_path):
            continue
            
        print(f"분석 중: {label}...")
        files = os.listdir(label_path)
        for i, img_name in enumerate(files):
            img_path = os.path.join(label_path, img_name)
            feat = extract_features(img_path)
            if feat is not None:
                X.append(feat)
                y.append(idx)
            
            if (i+1) % 50 == 0:
                print(f"  {i+1}/{len(files)} 완료")
                
    X = np.array(X)
    y = np.array(y)

    print(f"최종 학습 시작 (RandomForest, 특징 차원: {X.shape[1]})...")
    # 좀 더 정교한 분류를 위해 트리 개수 증가
    clf = RandomForestClassifier(n_estimators=200, max_depth=20, random_state=42)
    clf.fit(X, y)
    
    # 모델 및 라벨 저장
    joblib.dump(clf, 'waste_model.pkl')
    with open("labels.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(class_names))
        
    print("성능 향상된 모델 학습 완료 및 waste_model.pkl 저장됨.")

if __name__ == "__main__":
    # TensorFlow 로그 억제
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    train()
