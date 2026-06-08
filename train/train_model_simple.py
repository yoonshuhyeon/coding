import tensorflow as tf
from tensorflow.keras import layers, models
import os

# 1. 설정
DATA_PATH = 'dataset_small'
IMG_SIZE = (128, 128) # 해상도를 낮춰 메모리 절약
BATCH_SIZE = 16
EPOCHS = 3

def train():
    if not os.path.exists(DATA_PATH):
        print(f"Error: '{DATA_PATH}' 폴더가 없습니다.")
        return

    # 2. 데이터셋 로드
    train_ds = tf.keras.utils.image_dataset_from_directory(
        DATA_PATH,
        validation_split=0.2,
        subset="training",
        seed=123,
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE
    )

    val_ds = tf.keras.utils.image_dataset_from_directory(
        DATA_PATH,
        validation_split=0.2,
        subset="validation",
        seed=123,
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE
    )

    class_names = train_ds.class_names
    with open("labels.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(class_names))
    print(f"클래스 분류 완료: {class_names}")

    # 3. 초소형 CNN 모델 구축
    model = models.Sequential([
        layers.Rescaling(1./255, input_shape=(128, 128, 3)),
        layers.Conv2D(16, 3, padding='same', activation='relu'),
        layers.MaxPooling2D(),
        layers.Conv2D(32, 3, padding='same', activation='relu'),
        layers.MaxPooling2D(),
        layers.Flatten(),
        layers.Dense(64, activation='relu'),
        layers.Dense(len(class_names), activation='softmax')
    ])

    model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])

    print("학습을 시작합니다 (초소형 모델)...")
    model.fit(train_ds, validation_data=val_ds, epochs=EPOCHS)

    # 5. 모델 저장
    model.save('waste_model.h5')
    print("모델 학습 완료 및 waste_model.h5 저장됨.")

if __name__ == "__main__":
    train()
