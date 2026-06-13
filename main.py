import cv2
import os
import time
from datetime import datetime
from detection.detector import YOLODetector
from detection.config import VIDEO_SOURCE, CONF_THRESHOLD

def ensure_dir(path):
    """Создаёт папку, если её нет"""
    if not os.path.exists(path):
        os.makedirs(path)

def main():
    # Папка для сохранения кадров с рамками
    output_dir = "detection_frames"
    ensure_dir(output_dir)

    # Инициализация детектора
    print("Загрузка модели YOLOv8...")
    detector = YOLODetector()
    print("Модель загружена.")

    # Открытие видео
    cap = cv2.VideoCapture(VIDEO_SOURCE)
    if not cap.isOpened():
        print(f"Ошибка: не удалось открыть видео {VIDEO_SOURCE}")
        return

    frame_count = 0
    saved_count = 0
    start_time = time.time()

    print(f"Обработка видео из {VIDEO_SOURCE}...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1

        # Обрабатываем каждый кадр (можно добавить frame_skip, но для демонстрации оставим все)
        detections = detector.detect(frame)
        people_count = len(detections)

        # Рисуем рамки
        for (x1, y1, x2, y2, conf) in detections:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f'person {conf:.2f}', (x1, y1-5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        # Сохраняем каждый 10-й кадр, чтобы не забить диск (можно сохранять все, но для экономии места)
        if frame_count % 10 == 0:
            out_path = os.path.join(output_dir, f"frame_{frame_count:06d}.jpg")
            cv2.imwrite(out_path, frame)
            saved_count += 1
            print(f"[{frame_count}] Сохранён кадр: {out_path}, людей: {people_count}")

        # (Опционально) Вывод в консоль без сохранения каждого кадра
        if frame_count % 50 == 0:
            print(f"Обработано кадров: {frame_count}, людей на последнем кадре: {people_count}")

    cap.release()
    elapsed = time.time() - start_time
    print(f"\nОбработка завершена. Всего кадров: {frame_count}, сохранено: {saved_count}")
    print(f"Затрачено времени: {elapsed:.2f} сек. Средняя скорость: {frame_count/elapsed:.2f} FPS")

if __name__ == "__main__":
    main()