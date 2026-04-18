import os
import gdown
import threading
import shutil
import uuid

# ---- Auto-download model in background ----
MODEL_PATH = "best.pt"
GOOGLE_DRIVE_ID = "1mKlucdwoCF3RLnmDucS2hoSiyBei6uph"

def download_model():
    if not os.path.exists(MODEL_PATH):
        print("Downloading model from Google Drive...")
        gdown.download(f"https://drive.google.com/uc?id={GOOGLE_DRIVE_ID}", MODEL_PATH, quiet=False)
        print("Model downloaded successfully!")

threading.Thread(target=download_model, daemon=True).start()
# --------------------------------------------

from fastapi import FastAPI, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database import create_tables, get_db
from auth import register_user, login_user, verify_token, get_all_users, google_login
from cv_module import analyze_room_image
from xai_module import run_xai
from genai_module import generate_room_image

# ─────────────────────────────────────────
# Create database tables on startup
# ─────────────────────────────────────────
create_tables()
print("✅ Database ready")

# ─────────────────────────────────────────
# Create FastAPI app
# ─────────────────────────────────────────
app = FastAPI(
    title="RenoVision API",
    version="1.0"
)

# ─────────────────────────────────────────
# CORS Middleware
# ─────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# ─────────────────────────────────────────
# Upload folder
# ─────────────────────────────────────────
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ─────────────────────────────────────────
# Route 1 — Home
# ─────────────────────────────────────────
@app.get("/")
def home():
    return {
        "message": "RenoVision API is running!",
        "version": "1.0"
    }


# ─────────────────────────────────────────
# Route 2 — Register new user
# ─────────────────────────────────────────
@app.post("/auth/register")
def register(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    if len(password) < 6:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": "Password must be at least 6 characters"
            }
        )
    result = register_user(db, name, email, password)
    if not result["success"]:
        return JSONResponse(status_code=400, content=result)
    return result


# ─────────────────────────────────────────
# Route 3 — Login existing user
# ─────────────────────────────────────────
@app.post("/auth/login")
def login(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    result = login_user(db, email, password)
    if not result["success"]:
        return JSONResponse(status_code=401, content=result)
    return result


# ─────────────────────────────────────────
# Route 4 — Google OAuth Login
# ─────────────────────────────────────────
@app.post("/auth/google")
def google_auth(
    name: str = Form(...),
    email: str = Form(...),
    google_uid: str = Form(...),
    db: Session = Depends(get_db)
):
    result = google_login(db, name, email, google_uid)
    return result


# ─────────────────────────────────────────
# Route 5 — Get all users (admin)
# ─────────────────────────────────────────
@app.get("/auth/users")
def get_users(db: Session = Depends(get_db)):
    users = get_all_users(db)
    return {
        "total_users": len(users),
        "users": users
    }


# ─────────────────────────────────────────
# Route 6 — Analyze room image
# ─────────────────────────────────────────
@app.post("/analyze")
async def analyze_room(
    file: UploadFile = File(...),
    budget: int = Form(50000),
    style: str = Form("modern"),
    token: str = Form(...),
    user_prompt: str = Form("")
):
    email = verify_token(token)
    if not email:
        return JSONResponse(
            status_code=401,
            content={"error": "Please login to use this feature"}
        )

    if file.content_type not in ["image/jpeg", "image/png"]:
        return JSONResponse(
            status_code=400,
            content={"error": "Only JPEG and PNG images are allowed"}
        )

    file_id = str(uuid.uuid4())
    file_extension = file.filename.split(".")[-1]
    file_path = f"{UPLOAD_FOLDER}/{file_id}.{file_extension}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    cv_results = analyze_room_image(file_path)

    if os.path.exists(file_path):
        os.remove(file_path)

    if cv_results.get("is_outdoor", False):
        return JSONResponse(
            status_code=400,
            content={
                "error": "outdoor_scene",
                "message": cv_results["message"],
                "is_outdoor": True
            }
        )

    xai_results = run_xai(
        room_type=cv_results["room_type"],
        detected_furniture=cv_results["detected_furniture"],
        budget=budget,
        style=style,
        density=cv_results["room_density"],
        user_prompt=user_prompt
    )

    genai_results = generate_room_image(
        room_type=cv_results["room_type"],
        style=style,
        budget=budget,
        recommendations=xai_results["recommendations"],
        user_prompt=user_prompt,
        detected_furniture=cv_results.get("detected_furniture", []),
        dimensions=cv_results.get("dimensions", None)
    )

    return {
        "status": "success",
        "user_email": email,
        "file_received": file.filename,
        "budget": budget,
        "style": style,
        "user_prompt": user_prompt,
        "cv_analysis": cv_results,
        "xai_results": xai_results,
        "generated_design": genai_results
    }


# ─────────────────────────────────────────
# Route 7 — Get recommendations
# ─────────────────────────────────────────
@app.post("/recommend")
async def get_recommendations(
    room_type: str = Form("living room"),
    furniture: str = Form(""),
    budget: int = Form(50000),
    style: str = Form("modern")
):
    furniture_list = furniture.split(",") if furniture else []
    return {
        "status": "success",
        "room_type": room_type,
        "detected_furniture": furniture_list,
        "budget": budget,
        "style": style,
        "recommendations": []
    }


# ─────────────────────────────────────────
# Route 8 — Get explanation
# ─────────────────────────────────────────
@app.post("/explain")
async def explain_recommendation(
    recommendation: str = Form(...),
    room_type: str = Form("living room"),
    budget: int = Form(50000)
):
    return {
        "status": "success",
        "recommendation": recommendation,
        "explanation": (
            f"This recommendation suits your "
            f"{room_type} and fits within "
            f"your budget of Rs.{budget}."
        )
    }


# ─────────────────────────────────────────
# Route 9 — Generate visualization
# ─────────────────────────────────────────
@app.post("/visualize")
async def generate_visualization(
    room_type: str = Form("living room"),
    style: str = Form("modern"),
    budget: int = Form(50000)
):
    return {
        "status": "success",
        "message": f"Generating {style} design for {room_type}..."
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)