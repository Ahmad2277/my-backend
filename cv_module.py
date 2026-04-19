from ultralytics import YOLO
from PIL import Image
import cv2
import numpy as np
import os
import time

# ─────────────────────────────────────────
def get_model():
    global model
    if model is None:
        print("🔄 Loading Best model now...")
        import torch
        torch.set_num_threads(1)
        model = YOLO("best.pt")
        model.to('cpu')
        print("✅ Best model loaded on CPU!")
    return model

# ─────────────────────────────────────────
# ALL detectable objects
# ─────────────────────────────────────────
FURNITURE_ITEMS = [
    # Seating
    "chair", "couch", "bench", "stool",
    # Sleeping
    "bed",
    # Tables
    "dining table", "desk",
    # Entertainment
    "tv", "laptop", "remote",
    # Kitchen
    "microwave", "oven", "refrigerator",
    "sink", "toaster", "cup", "bowl",
    "knife", "fork", "spoon",
    # Bathroom
    "toilet",
    # Decoration
    "clock", "vase", "potted plant",
    "mirror", "book",
    # Storage
    "backpack", "suitcase",
    "bottle", "wine glass",
    # Electronics
    "cell phone", "keyboard", "mouse",
    "monitor", "printer",
]

# ─────────────────────────────────────────
# Objects that indicate OUTDOOR scene
# ─────────────────────────────────────────
OUTDOOR_OBJECTS = [
    "car", "truck", "bus", "motorcycle",
    "bicycle", "traffic light",
    "stop sign", "parking meter",
    "fire hydrant", "bench",
    "tree", "sky", "road",
    "person", "dog", "cat",
    "bird", "horse", "sheep", "cow",
    "elephant", "bear", "zebra", "giraffe"
]

# ─────────────────────────────────────────
# Indoor only objects — confirm indoor
# ─────────────────────────────────────────
INDOOR_OBJECTS = [
    "couch", "bed", "chair", "dining table",
    "toilet", "tv", "refrigerator", "oven",
    "microwave", "sink", "laptop", "desk",
    "clock", "vase", "potted plant", "mirror",
    "book", "remote", "keyboard", "mouse"
]


# ─────────────────────────────────────────
# Check if image is outdoor
# ─────────────────────────────────────────
def is_outdoor_scene(all_detected_labels):
    outdoor_count = sum(
        1 for label in all_detected_labels
        if label in OUTDOOR_OBJECTS
    )
    indoor_count = sum(
        1 for label in all_detected_labels
        if label in INDOOR_OBJECTS
    )

    # If more outdoor objects than indoor
    if outdoor_count > indoor_count and \
       outdoor_count >= 2:
        return True

    # Strong outdoor indicators
    strong_outdoor = [
        "car", "truck", "bus",
        "traffic light", "stop sign"
    ]
    for obj in all_detected_labels:
        if obj in strong_outdoor:
            return True

    return False


# ─────────────────────────────────────────
# Detect all objects in image
# ─────────────────────────────────────────
def detect_all_objects(image_path):
    print(f"🔍 Starting detection on: {image_path}")
    print(f"📁 File exists: {os.path.exists(image_path)}")
    
    current_model = get_model()
    print(f"✅ Model loaded: {current_model is not None}")
    
    results = current_model(
        image_path,
        verbose=True,
        conf=0.2,
        iou=0.45
    )
    
    print(f"📊 Raw results: {results}")
    
    all_labels = []
    furniture_items = []

    for r in results:
        print(f"📦 Boxes found: {len(r.boxes)}")
        for box in r.boxes:
            label = current_model.names[int(box.cls)]
            confidence = float(box.conf)
            print(f"  → Detected: {label} ({confidence:.2f})")
            all_labels.append(label)

            if label in FURNITURE_ITEMS and \
               confidence > 0.25:
                furniture_items.append({
                    "item": label,
                    "confidence": round(
                        confidence * 100, 1
                    )
                })

    print(f"🏠 All labels: {all_labels}")
    print(f"🛋️ Furniture items: {furniture_items}")

    # Remove duplicate furniture items
    seen = {}
    for item in furniture_items:
        name = item["item"]
        if name not in seen or \
           item["confidence"] > \
           seen[name]["confidence"]:
            seen[name] = item

    return list(seen.values()), all_labels


# ─────────────────────────────────────────
# Estimate room dimensions from image
# ─────────────────────────────────────────
def estimate_room_dimensions(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return None

    height, width = img.shape[:2]

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Detect edges
    edges = cv2.Canny(gray, 50, 150,
                      apertureSize=3)

    # Detect lines using Hough transform
    lines = cv2.HoughLinesP(
        edges, 1, np.pi / 180, 80,
        minLineLength=100, maxLineGap=10
    )

    horizontal_lines = 0
    vertical_lines = 0

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = abs(np.arctan2(
                y2 - y1, x2 - x1
            ) * 180 / np.pi)

            if angle < 20 or angle > 160:
                horizontal_lines += 1
            elif 70 < angle < 110:
                vertical_lines += 1

    # Estimate room size category
    # Based on image composition
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
        "horizontal_lines": horizontal_lines,
        "vertical_lines": vertical_lines,
        "room_width_type": room_width,
        "estimated_size": estimated_sqft,
        "structural_lines_detected":
            (horizontal_lines + vertical_lines)
    }


# ─────────────────────────────────────────
# Classify room type
# Using scoring system for accuracy
# ─────────────────────────────────────────
def classify_room(detected_items,
                  dimensions=None):
    item_names = [
        item["item"] for item in detected_items
    ]

    scores = {
        "bedroom": 0,
        "living room": 0,
        "kitchen": 0,
        "dining room": 0,
        "bathroom": 0,
        "study room": 0,
        "general room": 0
    }

    # Bedroom
    if "bed" in item_names:
        scores["bedroom"] += 15
    if "clock" in item_names:
        scores["bedroom"] += 2
    if "vase" in item_names:
        scores["bedroom"] += 1
    if "mirror" in item_names:
        scores["bedroom"] += 2

    # Living room
    if "couch" in item_names:
        scores["living room"] += 12
    if "tv" in item_names:
        scores["living room"] += 8
    if "potted plant" in item_names:
        scores["living room"] += 3
    if "remote" in item_names:
        scores["living room"] += 4
    if "vase" in item_names:
        scores["living room"] += 2

    # Kitchen
    if "refrigerator" in item_names:
        scores["kitchen"] += 12
    if "oven" in item_names:
        scores["kitchen"] += 10
    if "microwave" in item_names:
        scores["kitchen"] += 8
    if "sink" in item_names:
        scores["kitchen"] += 7
    if "toaster" in item_names:
        scores["kitchen"] += 5
    if "cup" in item_names:
        scores["kitchen"] += 3
    if "bowl" in item_names:
        scores["kitchen"] += 3
    if "knife" in item_names:
        scores["kitchen"] += 5

    # Dining room
    if "dining table" in item_names:
        scores["dining room"] += 10
    if "chair" in item_names:
        scores["dining room"] += 4
    if "wine glass" in item_names:
        scores["dining room"] += 6
    if "bowl" in item_names:
        scores["dining room"] += 3
    if "cup" in item_names:
        scores["dining room"] += 2

    # Bathroom
    if "toilet" in item_names:
        scores["bathroom"] += 15
    if "sink" in item_names:
        scores["bathroom"] += 5

    # Study room
    if "laptop" in item_names:
        scores["study room"] += 9
    if "book" in item_names:
        scores["study room"] += 7
    if "keyboard" in item_names:
        scores["study room"] += 8
    if "mouse" in item_names:
        scores["study room"] += 6
    if "monitor" in item_names:
        scores["study room"] += 8
    if "desk" in item_names:
        scores["study room"] += 8
    if "printer" in item_names:
        scores["study room"] += 5

    # If empty room — use dimensions to predict
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


# ─────────────────────────────────────────
# Extract dominant colors
# ─────────────────────────────────────────
def extract_colors(image_path):
    try:
        img = cv2.imread(image_path)
        img = cv2.cvtColor(
            img, cv2.COLOR_BGR2RGB
        )
        img = cv2.resize(img, (150, 150))
        pixels = img.reshape(
            -1, 3
        ).astype(np.float32)

        criteria = (
            cv2.TERM_CRITERIA_EPS +
            cv2.TERM_CRITERIA_MAX_ITER,
            20, 1.0
        )
        _, labels, centers = cv2.kmeans(
            pixels, 3, None, criteria,
            10, cv2.KMEANS_RANDOM_CENTERS
        )

        colors = []
        for center in centers:
            r = int(center[0])
            g = int(center[1])
            b = int(center[2])
            hex_color = "#{:02x}{:02x}{:02x}".format(
                r, g, b
            )
            colors.append(hex_color)

        return colors
    except Exception:
        return ["#888888", "#555555", "#333333"]


# ─────────────────────────────────────────
# Estimate room density
# ─────────────────────────────────────────
def estimate_room_density(detected_items):
    count = len(detected_items)
    if count == 0:
        return "empty"
    elif count <= 2:
        return "minimally furnished"
    elif count <= 5:
        return "moderately furnished"
    else:
        return "heavily furnished"


# ─────────────────────────────────────────
# MAIN FUNCTION
# ─────────────────────────────────────────
def analyze_room_image(image_path):
    try:
        # Detect all objects
        detected_items, all_labels = \
            detect_all_objects(image_path)

        # Check if outdoor scene
        if is_outdoor_scene(all_labels):
            return {
                "success": False,
                "is_outdoor": True,
                "error": "outdoor_scene",
                "message": "This appears to be an outdoor scene. RenoVision only works with indoor room photos. Please upload a photo taken inside a room.",
                "room_type": "outdoor",
                "detected_furniture": [],
                "dominant_colors": [],
                "room_density": "unknown",
                "furniture_count": 0,
                "dimensions": None
            }

        # Estimate dimensions
        dimensions = estimate_room_dimensions(
            image_path
        )

        # Classify room type
        room_type = classify_room(
            detected_items, dimensions
        )

        # Extract colors
        dominant_colors = extract_colors(
            image_path
        )

        # Estimate density
        density = estimate_room_density(
            detected_items
        )

        return {
            "success": True,
            "is_outdoor": False,
            "room_type": room_type,
            "detected_furniture": detected_items,
            "dominant_colors": dominant_colors,
            "room_density": density,
            "furniture_count": len(detected_items),
            "dimensions": dimensions,
            "all_detected_objects": list(
                set(all_labels)
            )
        }

    except Exception as e:
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