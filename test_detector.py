from backend.detector import detect_objects

image_path = "test.jpg"

objects = detect_objects(image_path)

print("Detected objects:", objects)
