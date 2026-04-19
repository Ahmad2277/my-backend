from ultralytics import YOLO
from PIL import Image
import cv2
import numpy as np
import os
import time

print("=== CV MODULE LOADING ===")

model = None

FURNITURE_ITEMS = [
    "chair", "couch", "bench", "stool",
    "bed", "dining table", "desk",
    "tv", "laptop", "remote",
    "microwave", "oven", "refrigerator",
    "sink", "toaster", "cup", "bowl",
    "knife", "fork", "spoon",
    "toilet", "clock", "vase",
    "potted plant", "mirror", "book",
    "backpack", "suitcase", "bottle",
    "wine glass", "cell phone",
    "keyboard", "mouse", "monitor",
]

OUTDOOR_OBJECTS = [
    "car", "truck", "bus", "motorcycle",
    "bicycle", "traffic light",
    "stop sign", "fire hydrant",
    "person", "dog", "cat", "bird",
]

INDOOR_OBJECTS = [
    "couch", "bed", "chair", "dining table",
    "toilet", "tv", "refrigerator", "oven",
    "microwave", "sink", "laptop", "desk",
    "clock", "vase", "potted plant",
    "book", "remote", "keyboard", "mouse"
]


def get_model():
    global model
    if model is None:
        try:
            print(">>> LOADING MODEL FROM best.pt <<<")
            model = YOLO("best.pt")
            names = list(model.names.values())
            print(f">>> MODEL LOADED! Classes: {names} <<<")
        except Exception as e:
            print(f">>> MODEL LOAD FAILED: {str(e)} <<<")
            model = None
    return model


def is_outdoor_scene(all_detected_labels):
    outdoor_count = sum(
        1 for label in all_detected_labels
        if label in OUTDOOR_OBJECTS
    )
    indoor_count = sum(
        1 for label in all_detected_labels
        if label in INDOOR_OBJECTS
    )
    if outdoor_count > indoor_count and outdoor_count >= 2:
        return True
    strong_outdoor = ["car", "truck", "bus", "traffic light", "stop sign"]
    for obj in all_detected_labels:
        if obj in strong_outdoor:
            return True
    return False


def detect_all_objects(image_path):
    print(f">>> DETECT CALLED: {image_path} <<<")
    print(f">>> FILE EXISTS: {os.path.exists(image_path)} <<<")

    current_model = get_model()

    if current_model is None:
        print(">>> MODEL IS NONE - CANNOT DETECT <<<")
        return [], []

    try:
        print(">>> RUNNING YOLO INFERENCE <<<")
        results = current_model(
            image_path,
            verbose=True,
            conf=0.1,
            iou=0.45
        )
        print(f">>> INFERENCE DONE <<<")

        all_labels = []
        furniture_items = []

        for r in results:
            boxes = r.boxes
            print(f">>> BOXES FOUND: {len(boxes)} <<<")
            for box in boxes:
                label = current_model.names[int(box.cls)]
                confidence = float(box.conf)
                print(f">>> DETECTED: {label} = {confidence:.2f} <<<")
                all_labels.append(label)
                if label in FURNITURE_ITEMS and confidence > 0.1:
                    furniture_items.append({
                        "item": label,
                        "confidence": round(confidence * 100, 1)
                    })

        print(f">>> ALL LABELS: {all_labels} <<<")
        print(f">>> FURNITURE: {furniture_items} <<<")

    except Exception as e:
        print(f">>> INFERENCE ERROR: {str(e)} <<<")
        return [], []

    seen = {}
    for item in furniture_items:
        name = item["item"]
        if name not in seen or item["confidence"] > seen[name]["confidence"]:
            seen[name] = item

    return list(seen.values()), all_labels


def estimate_room_dimensions(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return None
    height, width = img.shape[:2]
    aspect_ratio = width / height
    if aspect_ratio > 1.5:
        room_width = "wide"
        estimated_sqft = "medium to large"
    elif aspect_ratio < 0.8:
        room_width = "narrow"
        estimated_sqft = "small"
    else:
        room_width = "standard"
        estimated_sqft = "medium"
    return {
        "image_width_px": width,
        "image_height_px": height,
        "aspect_ratio": round(aspect_ratio, 2),
        "room_width_type": room_width,
        "estimated_size": estimated_sqft,
    }


def classify_room(detected_items, dimensions=None):
    item_names = [item["item"] for item in detected_items]
    scores = {
        "bedroom": 0, "living room": 0,
        "kitchen": 0, "dining room": 0,
        "bathroom": 0, "study room": 0,
        "general room": 0
    }
    if "bed" in item_names: scores["bedroom"] += 15
    if "couch" in item_names: scores["living room"] += 12
    if "tv" in item_names: scores["living room"] += 8
    if "remote" in item_names: scores["living room"] += 4
    if "refrigerator" in item_names: scores["kitchen"] += 12
    if "oven" in item_names: scores["kitchen"] += 10
    if "microwave" in item_names: scores["kitchen"] += 8
    if "sink" in item_names: scores["kitchen"] += 7
    if "dining table" in item_names: scores["dining room"] += 10
    if "toilet" in item_names: scores["bathroom"] += 15
    if "laptop" in item_names: scores["study room"] += 9
    if "keyboard" in item_names: scores["study room"] += 8
    if "monitor" in item_names: scores["study room"] += 8
    if "desk" in item_names: scores["study room"] += 8

    if len(item_names) == 0 and dimensions:
        ratio = dimensions["aspect_ratio"]
        if ratio > 1.6:
            return "living room"
        elif ratio < 0.9:
            return "bedroom"
        else:
            return "general room"

    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return "general room"
    return best


def extract_colors(image_path):
    try:
        img = cv2.imread(image_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (150, 150))
        pixels = img.reshape(-1, 3).astype(np.float32)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
        _, labels, centers = cv2.kmeans(pixels, 3, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        colors = []
        for center in centers:
            hex_color = "#{:02x}{:02x}{:02x}".format(int(center[0]), int(center[1]), int(center[2]))
            colors.append(hex_color)
        return colors
    except Exception:
        return ["#888888", "#555555", "#333333"]


def estimate_room_density(detected_items):
    count = len(detected_items)
    if count == 0: return "empty"
    elif count <= 2: return "minimally furnished"
    elif count <= 5: return "moderately furnished"
    else: return "heavily furnished"


def analyze_room_image(image_path):
    try:
        detected_items, all_labels = detect_all_objects(image_path)
        if is_outdoor_scene(all_labels):
            return {
                "success": False,
                "is_outdoor": True,
                "error": "outdoor_scene",
                "message": "Outdoor scene detected.",
                "room_type": "outdoor",
                "detected_furniture": [],
                "dominant_colors": [],
                "room_density": "unknown",
                "furniture_count": 0,
                "dimensions": None
            }
        dimensions = estimate_room_dimensions(image_path)
        room_type = classify_room(detected_items, dimensions)
        dominant_colors = extract_colors(image_path)
        density = estimate_room_density(detected_items)
        return {
            "success": True,
            "is_outdoor": False,
            "room_type": room_type,
            "detected_furniture": detected_items,
            "dominant_colors": dominant_colors,
            "room_density": density,
            "furniture_count": len(detected_items),
            "dimensions": dimensions,
            "all_detected_objects": list(set(all_labels))
        }
    except Exception as e:
        print(f">>> ANALYZE ERROR: {str(e)} <<<")
        return {
            "success": False,
            "is_outdoor": False,
            "error": str(e),
            "room_type": "unknown",
            "detected_furniture": [],
            "dominant_colors": [],
            "room_density": "unknown",
            "furniture_count": 0,
            "dimensions": None
        }