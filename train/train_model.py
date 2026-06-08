import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.applications import MobileNetV2
import os

# 1. 설정
DATA_PATH = 'dataset_small'
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 5

def train():
    if not os.path.exists(DATA_PATH):
        print(f"Error: '{DATA_PATH}' 폴더가 없습니다. 데이터셋을 준비해주세요.")
        return

    # 2. 데이터셋 로드 (학습용/검증용 분할)
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

    # 클래스 이름 확인 및 저장
    class_names = train_ds.class_names
    with open("labels.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(class_names))
    print(f"클래스 분류 완료: {class_names}")

    # 성능 최적화
    AUTOTUNE = tf.data.AUTOTUNE
    train_ds = train_ds.prefetch(buffer_size=AUTOTUNE)
    val_ds = val_ds.prefetch(buffer_size=AUTOTUNE)

    # 3. 모델 구축 (MobileNetV2 기반 전이 학습)
    base_model = MobileNetV2(input_shape=(224, 224, 3), include_top=False, weights='imagenet')
    base_model.trainable = False 

    model = models.Sequential([
        layers.Rescaling(1./127.5, offset=-1), 
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dense(len(class_names), activation='softmax')
    ])

    model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])

    # 4. 학습 시작
    print("학습을 시작합니다...")
    model.fit(train_ds, validation_data=val_ds, epochs=EPOCHS)

    # 5. 모델 저장
    model.save('waste_model.h5')
    print("모델 학습 완료 및 waste_model.h5 저장됨.")

if __name__ == "__main__":
    train()
