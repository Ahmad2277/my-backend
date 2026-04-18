import os
import base64
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


# ─────────────────────────────────────────
# Build prompt that:
# 1. Includes user custom request
# 2. Keeps existing furniture in image
# 3. Adds suggested furniture
# 4. Matches room dimensions
# ─────────────────────────────────────────
def build_prompt(room_type, style,
                 budget, recommendations,
                 user_prompt="",
                 detected_furniture=None,
                 dimensions=None):

    style_descriptions = {
        "modern": "modern minimalist, clean lines, neutral tones, contemporary furniture, sleek surfaces",
        "classic": "classic elegant, warm tones, traditional furniture, ornate details, timeless",
        "minimalist": "minimalist, uncluttered, monochrome, zen, simple clean surfaces",
        "natural": "natural organic, indoor plants, wood textures, earthy tones, biophilic"
    }

    if budget < 20000:
        budget_desc = "budget friendly"
    elif budget < 50000:
        budget_desc = "mid range"
    elif budget < 150000:
        budget_desc = "premium"
    else:
        budget_desc = "luxury high end"

    style_desc = style_descriptions.get(
        style, "modern contemporary"
    )

    # ── Existing furniture to KEEP ──
    existing_furniture = []
    if detected_furniture:
        existing_furniture = [
            item["item"]
            for item in detected_furniture
            if not item.get("is_prompt_based")
        ]

    # ── New furniture to ADD ──
    new_suggestions = []
    if recommendations:
        for rec in recommendations:
            if not rec.get("is_prompt_based"):
                new_suggestions.append(
                    rec["recommendation"]
                )

    # ── Room size context ──
    size_context = ""
    if dimensions:
        size = dimensions.get(
            "estimated_size", "medium"
        )
        size_context = (
            f"The room is {size} sized. "
            f"Arrange furniture proportionally "
            f"to fit the room dimensions. "
        )

    # ── Build the prompt ──
    if user_prompt and user_prompt.strip():
        # User prompt takes highest priority
        prompt = (
            f"A professionally renovated "
            f"{room_type} interior. "
            f"EXACT USER REQUEST: {user_prompt}. "
            f"Style: {style_desc}. "
            f"{budget_desc} renovation. "
        )

        if existing_furniture:
            prompt += (
                f"Keep these existing items "
                f"visible and prominent: "
                f"{', '.join(existing_furniture[:5])}. "
            )

        if new_suggestions:
            prompt += (
                f"Also include: "
                f"{', '.join(new_suggestions[:3])}. "
            )

        prompt += (
            f"{size_context}"
            f"Photorealistic interior design "
            f"photography, well lit, 8K quality, "
            f"architectural digest style. "
            f"No people. Show the full room."
        )

    else:
        # Standard prompt
        prompt = (
            f"A beautifully renovated {room_type}, "
            f"{style_desc}, {budget_desc}. "
        )

        if existing_furniture:
            prompt += (
                f"The room already has these "
                f"items — keep them in the design: "
                f"{', '.join(existing_furniture[:5])}. "
            )

        if new_suggestions:
            prompt += (
                f"Add these new elements: "
                f"{', '.join(new_suggestions[:3])}. "
            )

        prompt += (
            f"{size_context}"
            f"Professional interior design "
            f"photography, well lit bright room, "
            f"photorealistic, high quality 8K, "
            f"architectural digest style. "
            f"No people. Show the full room view."
        )

    return prompt


# ─────────────────────────────────────────
# Generate room design using DALL-E 3
# ─────────────────────────────────────────
def generate_room_image(
    room_type, style, budget,
    recommendations, user_prompt="",
    detected_furniture=None,
    dimensions=None
):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or \
       api_key == "sk-your-actual-key-here":
        return {
            "success": False,
            "error": "OpenAI API key not configured",
            "image_base64": None
        }

    try:
        prompt = build_prompt(
            room_type, style, budget,
            recommendations, user_prompt,
            detected_furniture, dimensions
        )

        print(f"DALL-E 3 prompt: {prompt[:150]}...")

        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="hd",
            n=1,
            response_format="b64_json"
        )

        image_base64 = response.data[0].b64_json

        print("Image generated successfully!")

        return {
            "success": True,
            "image_base64": image_base64,
            "prompt_used": prompt,
            "format": "image/png",
            "model_used": "DALL-E 3 HD"
        }

    except Exception as e:
        error_msg = str(e)
        print(f"DALL-E 3 error: {error_msg}")

        if "insufficient_quota" in error_msg:
            return {
                "success": False,
                "error": "OpenAI quota exceeded. Add credits at platform.openai.com",
                "image_base64": None
            }
        elif "invalid_api_key" in error_msg:
            return {
                "success": False,
                "error": "Invalid OpenAI API key",
                "image_base64": None
            }
        elif "content_policy" in error_msg:
            return {
                "success": False,
                "error": "Image blocked by content policy",
                "image_base64": None
            }
        else:
            return {
                "success": False,
                "error": f"Generation failed: {error_msg}",
                "image_base64": None
            }