
RENOVATION_RULES = {
    "bedroom": [
        {
            "id": "BED001",
            "condition": lambda f, b, s: "bed" not in f and b >= 20000,
            "recommendation": "Add a comfortable bed frame and mattress",
            "reason": "No bed was detected in your bedroom. A good bed is the most essential furniture piece for a bedroom and directly impacts sleep quality.",
            "estimated_cost": 15000,
            "priority": "High",
            "style_tags": ["modern", "classic", "minimalist"]
        },
        {
            "id": "BED002",
            "condition": lambda f, b, s: "chair" not in f and b >= 15000,
            "recommendation": "Add a comfortable reading chair or accent chair",
            "reason": "Your bedroom lacks seating. An accent chair adds functionality and visual balance to the room.",
            "estimated_cost": 8000,
            "priority": "Medium",
            "style_tags": ["modern", "classic"]
        },
        {
            "id": "BED003",
            "condition": lambda f, b, s: "vase" not in f and b >= 5000,
            "recommendation": "Add decorative plants or vases",
            "reason": "Your bedroom has no decorative elements detected. Plants and vases improve air quality and add a calming aesthetic.",
            "estimated_cost": 2000,
            "priority": "Low",
            "style_tags": ["modern", "minimalist", "natural"]
        },
        {
            "id": "BED004",
            "condition": lambda f, b, s: b >= 30000 and s == "modern",
            "recommendation": "Install modern LED strip lighting behind bed headboard",
            "reason": "Modern bedrooms benefit greatly from ambient lighting. LED strips create a luxurious atmosphere and are energy efficient.",
            "estimated_cost": 5000,
            "priority": "Medium",
            "style_tags": ["modern"]
        },
        {
            "id": "BED005",
            "condition": lambda f, b, s: b >= 50000,
            "recommendation": "Add a wardrobe or built-in closet",
            "reason": "Your budget allows for proper storage. A wardrobe keeps the bedroom organized and clutter-free.",
            "estimated_cost": 35000,
            "priority": "High",
            "style_tags": ["modern", "classic", "minimalist"]
        },
    ],

    "living room": [
        {
            "id": "LIV001",
            "condition": lambda f, b, s: "couch" not in f and b >= 25000,
            "recommendation": "Add a sofa set or sectional couch",
            "reason": "No sofa was detected in your living room. A sofa is the centerpiece of any living room and essential for comfortable seating.",
            "estimated_cost": 20000,
            "priority": "High",
            "style_tags": ["modern", "classic", "minimalist"]
        },
        {
            "id": "LIV002",
            "condition": lambda f, b, s: "tv" not in f and b >= 30000,
            "recommendation": "Install a flat screen TV with wall mount",
            "reason": "No TV was detected. A wall-mounted TV saves floor space and serves as a focal point for the living room.",
            "estimated_cost": 25000,
            "priority": "Medium",
            "style_tags": ["modern"]
        },
        {
            "id": "LIV003",
            "condition": lambda f, b, s: "potted plant" not in f and b >= 5000,
            "recommendation": "Add indoor plants for natural freshness",
            "reason": "No plants detected. Indoor plants improve air quality, reduce stress and add natural beauty to living spaces.",
            "estimated_cost": 3000,
            "priority": "Low",
            "style_tags": ["modern", "natural", "minimalist"]
        },
        {
            "id": "LIV004",
            "condition": lambda f, b, s: b >= 40000 and s == "modern",
            "recommendation": "Add a modern center table and TV console",
            "reason": "Your budget allows for complete living room furniture. A center table ties the seating arrangement together.",
            "estimated_cost": 15000,
            "priority": "Medium",
            "style_tags": ["modern"]
        },
        {
            "id": "LIV005",
            "condition": lambda f, b, s: b >= 60000,
            "recommendation": "Install false ceiling with recessed lighting",
            "reason": "With your budget, a false ceiling dramatically elevates the living room aesthetic and adds ambient lighting options.",
            "estimated_cost": 45000,
            "priority": "High",
            "style_tags": ["modern", "classic"]
        },
    ],

    "kitchen": [
        {
            "id": "KIT001",
            "condition": lambda f, b, s: "refrigerator" not in f and b >= 30000,
            "recommendation": "Add a refrigerator",
            "reason": "No refrigerator detected. A refrigerator is an essential kitchen appliance for food storage and preservation.",
            "estimated_cost": 25000,
            "priority": "High",
            "style_tags": ["modern", "classic", "minimalist"]
        },
        {
            "id": "KIT002",
            "condition": lambda f, b, s: "microwave" not in f and b >= 15000,
            "recommendation": "Add a microwave oven",
            "reason": "No microwave detected. A microwave significantly speeds up cooking and reheating, making daily kitchen tasks easier.",
            "estimated_cost": 8000,
            "priority": "Medium",
            "style_tags": ["modern", "minimalist"]
        },
        {
            "id": "KIT003",
            "condition": lambda f, b, s: b >= 50000,
            "recommendation": "Install modular kitchen cabinets",
            "reason": "Your budget allows for modular storage. Cabinets maximize kitchen space and give a clean organized look.",
            "estimated_cost": 40000,
            "priority": "High",
            "style_tags": ["modern", "minimalist"]
        },
    ],

    "dining room": [
        {
            "id": "DIN001",
            "condition": lambda f, b, s: "dining table" not in f and b >= 20000,
            "recommendation": "Add a proper dining table with chairs",
            "reason": "No dining table detected. A dining table is essential for a dining room and brings the family together for meals.",
            "estimated_cost": 15000,
            "priority": "High",
            "style_tags": ["modern", "classic"]
        },
        {
            "id": "DIN002",
            "condition": lambda f, b, s: b >= 30000,
            "recommendation": "Add a chandelier or pendant light above dining area",
            "reason": "Proper lighting over a dining table creates ambiance and makes meals more enjoyable.",
            "estimated_cost": 10000,
            "priority": "Medium",
            "style_tags": ["modern", "classic"]
        },
    ],

    "bathroom": [
        {
            "id": "BAT001",
            "condition": lambda f, b, s: b >= 20000,
            "recommendation": "Install modern bathroom fixtures and fittings",
            "reason": "Upgrading fixtures improves water efficiency and gives the bathroom a fresh modern look.",
            "estimated_cost": 15000,
            "priority": "High",
            "style_tags": ["modern", "minimalist"]
        },
        {
            "id": "BAT002",
            "condition": lambda f, b, s: b >= 40000,
            "recommendation": "Add wall tiles and anti-slip floor tiles",
            "reason": "Proper tiling protects walls from moisture, prevents accidents, and dramatically improves bathroom appearance.",
            "estimated_cost": 25000,
            "priority": "High",
            "style_tags": ["modern", "classic", "minimalist"]
        },
    ],

    "study room": [
        {
            "id": "STU001",
            "condition": lambda f, b, s: "laptop" not in f and b >= 50000,
            "recommendation": "Add a computer setup with proper desk",
            "reason": "No computer detected in study room. A proper workstation setup improves productivity and posture.",
            "estimated_cost": 40000,
            "priority": "High",
            "style_tags": ["modern", "minimalist"]
        },
        {
            "id": "STU002",
            "condition": lambda f, b, s: b >= 15000,
            "recommendation": "Add proper task lighting and desk lamp",
            "reason": "Good lighting in a study room reduces eye strain during long study or work sessions.",
            "estimated_cost": 5000,
            "priority": "Medium",
            "style_tags": ["modern", "minimalist", "classic"]
        },
        {
            "id": "STU003",
            "condition": lambda f, b, s: "book" not in f and b >= 10000,
            "recommendation": "Add a bookshelf for organization",
            "reason": "No bookshelf detected. A bookshelf keeps study materials organized and makes the room look more scholarly.",
            "estimated_cost": 8000,
            "priority": "Medium",
            "style_tags": ["modern", "classic"]
        },
    ],

    "general room": [
        {
            "id": "GEN001",
            "condition": lambda f, b, s: b >= 10000,
            "recommendation": "Repaint walls with a fresh neutral color",
            "reason": "A fresh coat of paint is the most cost effective way to transform any room. Neutral colors make spaces feel larger and brighter.",
            "estimated_cost": 8000,
            "priority": "High",
            "style_tags": ["modern", "classic", "minimalist", "natural"]
        },
        {
            "id": "GEN002",
            "condition": lambda f, b, s: b >= 20000,
            "recommendation": "Improve lighting with new light fixtures",
            "reason": "Good lighting transforms the entire feel of a room. Replacing old fixtures with modern ones is a high impact low cost upgrade.",
            "estimated_cost": 10000,
            "priority": "High",
            "style_tags": ["modern", "classic", "minimalist"]
        },
    ]
}


# ─────────────────────────────────────────
# Generate recommendations with explanations
# ─────────────────────────────────────────
def generate_recommendations(room_type, detected_furniture,
                              budget, style):

    furniture_names = [item["item"] for item in detected_furniture]

    # Get rules for this room type
    # Fall back to general room if not found
    rules = RENOVATION_RULES.get(room_type,
            RENOVATION_RULES["general room"])

    recommendations = []

    for rule in rules:
        try:
            # Check if condition is met
            if rule["condition"](furniture_names, budget, style):

                # Check if style matches
                style_match = (
                    style in rule["style_tags"] or
                    len(rule["style_tags"]) == 0
                )

                # Check if budget covers this item
                budget_feasible = (
                    budget >= rule["estimated_cost"]
                )

                if budget_feasible:
                    recommendations.append({
                        "id": rule["id"],
                        "recommendation": rule["recommendation"],
                        "reason": rule["reason"],
                        "estimated_cost": rule["estimated_cost"],
                        "priority": rule["priority"],
                        "style_match": style_match,
                        "budget_remaining_after": budget - rule["estimated_cost"]
                    })

        except Exception:
            continue

    # Sort by priority
    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    recommendations.sort(
        key=lambda x: priority_order.get(x["priority"], 3)
    )

    return recommendations


# ─────────────────────────────────────────
# Generate overall renovation summary
# ─────────────────────────────────────────
def generate_summary(room_type, recommendations,
                     budget, style, density):

    total_cost = sum(r["estimated_cost"]
                     for r in recommendations)
    high_priority = [r for r in recommendations
                     if r["priority"] == "High"]
    affordable = [r for r in recommendations
                  if r["estimated_cost"] <= budget]

    if len(recommendations) == 0:
        summary = f"Your {room_type} looks well furnished! Only minor improvements are suggested within your budget."
    elif len(high_priority) > 0:
        summary = f"Your {room_type} needs {len(high_priority)} high priority improvements. The most important is: {high_priority[0]['recommendation']}."
    else:
        summary = f"Your {room_type} is in decent shape. We found {len(recommendations)} optional improvements to enhance it."

    return {
        "summary": summary,
        "total_recommendations": len(recommendations),
        "high_priority_count": len(high_priority),
        "total_estimated_cost": total_cost,
        "budget_sufficient": total_cost <= budget,
        "affordable_count": len(affordable)
    }


# ─────────────────────────────────────────
# MAIN FUNCTION — call this from main.py
# ─────────────────────────────────────────
def run_xai(room_type, detected_furniture,
            budget, style, density,
            user_prompt=""):

    recommendations = generate_recommendations(
        room_type, detected_furniture,
        budget, style
    )

    # Add user prompt as top recommendation
    # so it appears in suggestions box
    if user_prompt and user_prompt.strip():
        prompt_rec = {
            "id": "PROMPT001",
            "recommendation": user_prompt,
            "reason": (
                f"This is your custom request. "
                f"The AI has incorporated "
                f"'{user_prompt}' into both the "
                f"renovation recommendations and "
                f"the generated design image."
            ),
            "estimated_cost": 0,
            "priority": "High",
            "style_match": True,
            "budget_remaining_after": budget,
            "is_prompt_based": True
        }
        recommendations.insert(0, prompt_rec)

    summary = generate_summary(
        room_type, recommendations,
        budget, style, density
    )

    if user_prompt and user_prompt.strip():
        summary["user_prompt"] = user_prompt
        summary["summary"] = (
            f"Based on your request "
            f"'{user_prompt}' and room analysis: "
            + summary["summary"]
        )

    return {
        "success": True,
        "room_type": room_type,
        "style": style,
        "budget": budget,
        "user_prompt": user_prompt,
        "summary": summary,
        "recommendations": recommendations
    }