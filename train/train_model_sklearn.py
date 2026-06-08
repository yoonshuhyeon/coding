import os
import numpy as np
from PIL import Image
from sklearn.ensemble import RandomForestClassifier
import joblib

# 1. 설정
DATA_PATH = 'dataset_small'
IMG_SIZE = (64, 64)

def load_data():
    X = []
    y = []
    class_names = sorted(os.listdir(DATA_PATH))
    
    for idx, label in enumerate(class_names):
        label_path = os.path.join(DATA_PATH, label)
        if not os.path.isdir(label_path):
            continue
            
        print(f"로드 중: {label}...")
        for img_name in os.listdir(label_path):
            try:
                img_path = os.path.join(label_path, img_name)
                img = Image.open(img_path).convert('RGB').resize(IMG_SIZE)
                X.append(np.array(img).flatten())
                y.append(idx)
            except Exception as e:
                continue
                
    return np.array(X), np.array(y), class_names

def train():
    print("데이터 로딩 중...")
    X, y, class_names = load_data()
    
    if len(X) == 0:
        print("Error: 학습할 데이터가 없습니다.")
        return

    print(f"학습 시작 (RandomForest, 데이터 개수: {len(X)})...")
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X, y)
    
    # 모델 및 라벨 저장
    joblib.dump(clf, 'waste_model.pkl')
    with open("labels.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(class_names))
        
    print("모델 학습 완료 및 waste_model.pkl 저장됨.")

if __name__ == "__main__":
    train()
