import cv2
import time
import mediapipe as mp
from ultralytics import YOLO
from backend.proctor import handle_violation

# ==============================
# LOAD MODEL & CAMERA
# ==============================
model = YOLO("model/best.pt")
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

user_id = "student_1"
CONFIDENCE_THRESHOLD = 0.4

# ==============================
# TIMING
# ==============================
PERSIST_TIME = 1.0  # seconds
phone_start_time = None
face_start_time = None

# ==============================
# MEDIAPIPE FACE DETECTOR
# ==============================
mp_face = mp.solutions.face_detection
face_detector = mp_face.FaceDetection(
    model_selection=0,
    min_detection_confidence=0.4
)

# ==============================
# EVENT DECISION
# ==============================
def detect_event(detected_objects, face_count):
    global phone_start_time, face_start_time
    now = time.time()

    # --------------------------
    # MULTIPLE PERSON (STRICT)
    # --------------------------
    if face_count > 1:
        if face_start_time is None:
            face_start_time = now
        elif now - face_start_time >= PERSIST_TIME:
            return "multiple_faces"
    else:
        face_start_time = None

    # --------------------------
    # PHONE DETECTION
    # --------------------------
    phone_like = ("cell phone" in detected_objects) or ("remote" in detected_objects)
    has_bottle = "bottle" in detected_objects

    if phone_like and not has_bottle:
        if phone_start_time is None:
            phone_start_time = now
        elif now - phone_start_time >= PERSIST_TIME:
            return "phone_detected"
    else:
        phone_start_time = None

    return None

# ==============================
# MAIN LOOP
# ==============================
while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Camera error")
        break

    # --------------------------
    # YOLO OBJECT DETECTION
    # --------------------------
    results = model(frame, conf=CONFIDENCE_THRESHOLD)
    detected_objects = []

    for r in results:
        for box in r.boxes:
            label = model.names[int(box.cls[0])]
            detected_objects.append(label)

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                frame, label, (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2
            )

    # --------------------------
    # FACE DETECTION (NO FILTER)
    # --------------------------
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_results = face_detector.process(rgb)

    face_count = len(face_results.detections) if face_results.detections else 0

    # draw face boxes
    if face_results.detections:
        h, w = frame.shape[:2]
        for det in face_results.detections:
            bbox = det.location_data.relative_bounding_box
            x1 = int(bbox.xmin * w)
            y1 = int(bbox.ymin * h)
            x2 = int((bbox.xmin + bbox.width) * w)
            y2 = int((bbox.ymin + bbox.height) * h)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)

    # --------------------------
    # EVENT DECISION
    # --------------------------
    event = detect_event(detected_objects, face_count)

    if event:
        status, warnings, reason = handle_violation(event, user_id)
    else:
        status, warnings, reason = "ok", None, "normal behavior"

    # --------------------------
    # DISPLAY
    # --------------------------
    cv2.putText(
        frame,
        f"Status: {status}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 0, 255),
        2
    )

    if warnings is not None:
        cv2.putText(
            frame,
            f"Warnings: {warnings}/2",
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            2
        )

    cv2.putText(
        frame,
        f"Faces detected: {face_count}",
        (20, 120),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 0, 0),
        2
    )

    cv2.imshow("AI Proctoring", frame)

    # --------------------------
    # EXIT
    # --------------------------
    if status == "terminate":
        print("❌ Exam terminated")
        break

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
