import os
import numpy as np
from PIL import Image
from skimage.feature import hog
from skimage.color import rgb2gray
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
import joblib

# 1. 설정
DATA_PATH = 'dataset_small'
IMG_SIZE = (128, 128) # 형태 분석을 위해 해상도 유지

def extract_hog_features(img_path):
    try:
        # 이미지 로드 및 그레이스케일 변환
        img = Image.open(img_path).convert('RGB').resize(IMG_SIZE)
        img_np = np.array(img)
        gray_img = rgb2gray(img_np)
        
        # HOG 특징 추출 (모양과 테두리 분석)
        fd = hog(gray_img, orientations=9, pixels_per_cell=(16, 16),
                cells_per_block=(2, 2), visualize=False)
        return fd
    except Exception as e:
        return None

def train():
    X = []
    y = []
    class_names = sorted(os.listdir(DATA_PATH))
    
    print("이미지 형태 분석(HOG) 및 데이터 증강 중...")
    for idx, label in enumerate(class_names):
        label_path = os.path.join(DATA_PATH, label)
        if not os.path.isdir(label_path):
            continue
            
        print(f"분석 중: {label}...")
        files = os.listdir(label_path)
        for i, img_name in enumerate(files):
            img_path = os.path.join(label_path, img_name)
            
            # 1. 원본 특징 추출
            feat = extract_hog_features(img_path)
            if feat is not None:
                X.append(feat)
                y.append(idx)
                
                # 2. 데이터 증강: 좌우 반전 이미지 추가 (정확도 향상)
                img = Image.open(img_path).convert('RGB').resize(IMG_SIZE)
                flipped_img = img.transpose(Image.FLIP_LEFT_RIGHT)
                gray_flipped = rgb2gray(np.array(flipped_img))
                feat_flipped = hog(gray_flipped, orientations=9, pixels_per_cell=(16, 16),
                                 cells_per_block=(2, 2), visualize=False)
                X.append(feat_flipped)
                y.append(idx)
            
            if (i+1) % 50 == 0:
                print(f"  {i+1}/{len(files)} 완료")
                
    X = np.array(X)
    y = np.array(y)

    print(f"고정밀 학습 시작 (RandomForest, 특징 차원: {X.shape[1]})...")
    # 하이퍼파라미터 최적화
    clf = RandomForestClassifier(n_estimators=300, max_depth=None, 
                                 min_samples_split=2, random_state=42, n_jobs=-1)
    clf.fit(X, y)
    
    # 모델 및 라벨 저장
    os.makedirs('models', exist_ok=True)
    joblib.dump(clf, 'models/waste_model.pkl')
    with open("models/labels.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(class_names))
        
    print(f"HOG 기반 고정밀 모델 학습 완료 및 저장됨. (총 데이터수: {len(X)})")

if __name__ == "__main__":
    train()
