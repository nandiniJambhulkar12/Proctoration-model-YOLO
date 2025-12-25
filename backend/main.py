
# from fastapi import FastAPI
# from backend.detector import detect_objects
# from backend.proctor import handle_violation

# app = FastAPI()


# def map_objects_to_event(detected_objects):
#     if detected_objects.count("person") > 1:
#         return "multiple_faces"

#     if "cell phone" in detected_objects or "remote" in detected_objects:
#         return "phone_detected"

#     return None


# @app.post("/proctor")
# def proctor_exam(data: dict):
#     """
#     Input:
#     {
#         "user_id": "student_1",
#         "image_path": "test.jpg"
#     }
#     """

#     user_id = data["user_id"]
#     image_path = data["image_path"]

#     detected_objects = detect_objects(image_path)

#     event = map_objects_to_event(detected_objects)

#     if event:
#         status, warnings, reason = handle_violation(event, user_id)
#     else:
#         status, warnings, reason = "ok", 0, "Normal behavior"

#     return {
#         "detected_objects": detected_objects,
#         "event": event,
#         "status": status,
#         "warnings": warnings,
#         "reason": reason
#     }






from fastapi import FastAPI, UploadFile, File
import cv2
import numpy as np

from backend.detector import detect_objects
from backend.proctor import handle_violation

app = FastAPI(title="AI Proctoring API")


def map_objects_to_event(detected_objects):
    if detected_objects.count("person") > 1:
        return "multiple_faces"

    if "cell phone" in detected_objects or "remote" in detected_objects:
        return "phone_detected"

    return None


@app.post("/proctor")
async def proctor_exam(
    user_id: str,
    file: UploadFile = File(...)
):
    """
    Receives an image frame from frontend (webcam screenshot)
    """

    # ✅ Read image bytes
    image_bytes = await file.read()

    # ✅ Convert bytes → OpenCV image
    np_img = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    if frame is None:
        return {
            "status": "error",
            "reason": "Invalid image"
        }

    # ✅ YOLO detection
    detected_objects = detect_objects(frame)

    # ✅ Proctoring logic
    event = map_objects_to_event(detected_objects)

    if event:
        status, warnings, reason = handle_violation(event, user_id)
    else:
        status, warnings, reason = "ok", 0, "Normal behavior"

    return {
        "status": status,
        "warnings": warnings,
        "reason": reason,
        "event": event,
        "detected_objects": detected_objects
    }
