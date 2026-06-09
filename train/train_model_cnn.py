import os
# Segmentation Fault 방지를 위해 CPU만 사용하도록 설정
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping

# 1. 설정
DATA_PATH = 'dataset_small'
IMG_SIZE = (224, 224)  # MobileNetV2 기본 입력 크기
BATCH_SIZE = 32
EPOCHS = 20
MODEL_SAVE_PATH = 'models/waste_model_cnn.h5'
LABEL_SAVE_PATH = 'models/labels.txt'

def train():
    # 2. 데이터 준비
    # 검증 데이터 분리를 위해 20% validation split 설정
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True,
        validation_split=0.2
    )

    train_generator = train_datagen.flow_from_directory(
        DATA_PATH,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='training'
    )

    validation_generator = train_datagen.flow_from_directory(
        DATA_PATH,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='validation'
    )

    # 클래스 라벨 저장
    class_names = sorted(train_generator.class_indices.keys())
    os.makedirs('models', exist_ok=True)
    with open(LABEL_SAVE_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(class_names))
    
    print(f"발견된 클래스: {class_names}")

    # 3. 모델 구성 (MobileNetV2 기반 전이 학습)
    base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
    base_model.trainable = False  # 사전 학습된 가중치 고정

    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(128, activation='relu')(x)
    x = Dropout(0.5)(x)
    predictions = Dense(len(class_names), activation='softmax')(x)

    model = Model(inputs=base_model.input, outputs=predictions)

    model.compile(optimizer='adam', loss='categorical_loss' if len(class_names) == 1 else 'categorical_crossentropy', metrics=['accuracy'])

    # 4. 콜백 설정
    checkpoint = ModelCheckpoint(MODEL_SAVE_PATH, monitor='val_accuracy', save_best_only=True, verbose=1)
    early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

    # 5. 학습 시작
    print("CNN 모델 학습 시작...")
    model.fit(
        train_generator,
        steps_per_epoch=train_generator.samples // BATCH_SIZE,
        validation_data=validation_generator,
        validation_steps=validation_generator.samples // BATCH_SIZE,
        epochs=EPOCHS,
        callbacks=[checkpoint, early_stopping]
    )

    print(f"모델 학습 완료 및 {MODEL_SAVE_PATH} 저장됨.")

if __name__ == "__main__":
    train()
