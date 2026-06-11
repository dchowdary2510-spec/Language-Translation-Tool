from ultralytics import YOLO
import cv2

# Fast YOLO model
model = YOLO("yolov8n.pt")


def detect_and_track(frame, confidence=0.3, selected_classes=None):

    # Resize frame for faster processing
    frame = cv2.resize(frame, (640, 480))

    # Convert selected class names to class IDs
    class_ids = None

    if selected_classes:
        class_ids = [
            idx
            for idx, name in model.names.items()
            if name in selected_classes
        ]

    # Run tracking
    results = model.track(
        frame,
        persist=True,
        conf=confidence,
        classes=class_ids,
        verbose=False
    )

    result = results[0]

    names = result.names

    annotated_frame = frame.copy()

    if result.boxes is not None:

        for box in result.boxes:

            x1, y1, x2, y2 = map(
                int,
                box.xyxy[0]
            )

            cls_id = int(box.cls[0])

            confidence_score = float(
                box.conf[0]
            )

            class_name = names[cls_id]

            tracking_id = "N/A"

            if box.id is not None:
                tracking_id = int(box.id[0])

            label = (
                f"{class_name} "
                f"ID:{tracking_id} "
                f"{confidence_score:.2f}"
            )

            cv2.rectangle(
                annotated_frame,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )

            cv2.putText(
                annotated_frame,
                label,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2
            )

    return annotated_frame, results