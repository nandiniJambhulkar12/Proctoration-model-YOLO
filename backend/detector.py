
# # newone
# from ultralytics import YOLO
# import cv2

# model = YOLO("model/best.pt")

# def detect_objects(image_path):
#     image = cv2.imread(image_path)

#     if image is None:
#         raise ValueError("Invalid image path")

#     results = model(image, conf=0.6)

#     detected_objects = []
#     for r in results:
#         for box in r.boxes:
#             detected_objects.append(
#                 model.names[int(box.cls[0])]
#             )

#     return detected_objects

from ultralytics import YOLO

# Load YOLO once (VERY IMPORTANT for performance)
model = YOLO("model/best.pt")

def detect_objects(frame):
    """
    frame: OpenCV image (numpy array)
    returns: list of detected object labels
    """

    if frame is None:
        raise ValueError("Invalid frame received")

    results = model(frame, conf=0.6)

    detected_objects = []

    for r in results:
        for box in r.boxes:
            label = model.names[int(box.cls[0])]
            detected_objects.append(label)

    return detected_objects
