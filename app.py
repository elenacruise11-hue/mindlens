"""
✅ MindLens AI Wellness – FastAPI App (v5.2)
Offline-safe stress scan + graceful chatbot fallback
"""

# -------------------------------------------------------------------------
# ✅ TensorFlow / DeepFace Compatibility Patch
# -------------------------------------------------------------------------
import sys
try:
    import tensorflow as tf
    from tensorflow import keras

    if not hasattr(keras.layers, "LocallyConnected2D"):
        class LocallyConnected2D(tf.keras.layers.Layer):
            def __init__(self, *a, **kw): super().__init__()
            def call(self, x): return x
        keras.layers.LocallyConnected2D = LocallyConnected2D

    sys.modules["tensorflow.keras.layers"] = keras.layers
    sys.modules["keras.layers"] = keras.layers
    print("✅ DeepFace patch applied")
except Exception as e:
    print("⚠ DeepFace patch failed:", e)


# -------------------------------------------------------------------------
# ✅ IMPORTS
# -------------------------------------------------------------------------
import os
import uuid
import datetime
import cv2
import numpy as np
import httpx
import jwt
from typing import Optional
from fastapi import FastAPI, Request, File, UploadFile, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv


from database import supabase_client
from models import (
    UserSignup, UserLogin, OTPVerification, AuthResponse,
    HabitResponse, HabitSubmission
)
from auth_utils import (
    hash_password, verify_password, generate_otp, send_otp_email,
    validate_email_format, validate_password_strength, create_access_token
)

from stress_analysis import StressAnalyzer
from model_manager import init_models, model_manager
from offline_storage import offline_storage, is_network_error




# -------------------------------------------------------------------------
# ✅ SETUP
# -------------------------------------------------------------------------
load_dotenv()

app = FastAPI(title="MindLens AI Wellness", version="5.2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/public", StaticFiles(directory="public"), name="public")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
JWT_SECRET = os.getenv("JWT_SECRET_KEY", "secret123")


# -------------------------------------------------------------------------
# ✅ HELPERS
# -------------------------------------------------------------------------
def iso_now():
    return datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc
    ).isoformat()


def dual_route(path):
    def wrap(fn):
        app.get(f"/{path}", response_class=HTMLResponse)(fn)
        app.get(f"/{path}.html", response_class=HTMLResponse)(fn)
        return fn
    return wrap


def page(request, file, **kw):
    return templates.TemplateResponse(file, {"request": request, **kw})


# -------------------------------------------------------------------------
# ✅ UI ROUTES
# -------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return page(request, "index.html")


@dual_route("signup")
async def signup_page(request: Request): return page(request, "signup.html")


@dual_route("verify-otp")
async def verify_otp_page(request: Request): return page(request, "verify-otp.html")


@dual_route("homepage")
async def homepage(request: Request): return page(request, "homepage.html")


@dual_route("habit-tracker")
async def habit_page(request: Request): return page(request, "habit-tracker.html")


@dual_route("stress-scanner")
async def stress_page(request: Request): return page(request, "stress-scanner.html")


@dual_route("chatbot")
async def chatbot_page(request: Request): return page(request, "chatbot.html")


@dual_route("dashboard")
async def dashboard_page(request: Request): return page(request, "dashboard.html")


# -------------------------------------------------------------------------
# ✅ SIGNUP
# -------------------------------------------------------------------------
@app.post("/signup", response_model=AuthResponse)
async def signup(data: UserSignup):
    try:
        if not validate_email_format(data.email):
            return AuthResponse(success=False, message="Invalid email")

        strong, msg = validate_password_strength(data.password)
        if not strong:
            return AuthResponse(success=False, message=msg)

        exists = supabase_client.table("users") \
            .select("*") \
            .eq("email", data.email) \
            .execute()

        if exists.data:
            return AuthResponse(success=False, message="User already exists")

        hashed = hash_password(data.password[:72])

        new_user = {
            "id": str(uuid.uuid4()),
            "full_name": data.full_name,
            "email": data.email,
            "password_hash": hashed,
            "is_verified": False,
            "created_at": iso_now()
        }

        supabase_client.table("users").insert(new_user).execute()

        otp = generate_otp()
        supabase_client.table("otp").insert({
            "email": data.email,
            "otp_code": otp,
            "expires_at": iso_now(),
            "created_at": iso_now()
        }).execute()

        await send_otp_email(data.email, otp, data.full_name)

        return AuthResponse(success=True, message="OTP sent")

    except Exception as e:
        error_msg = str(e)
        print("[Signup Error]", e)
        
        # Check for network/connection errors
        if "ConnectError" in str(type(e).__name__) or "getaddrinfo" in error_msg or "httpx" in error_msg:
            return AuthResponse(
                success=False, 
                message="Cannot connect to database. Please check your internet connection and try again."
            )
        
        return AuthResponse(success=False, message="Signup failed")


# -------------------------------------------------------------------------
# ✅ VERIFY OTP
# -------------------------------------------------------------------------
@app.post("/verify", response_model=AuthResponse)
async def verify(otp_data: OTPVerification):
    try:
        res = (
            supabase_client.table("otp")
            .select("*")
            .eq("email", otp_data.email)
            .eq("otp_code", otp_data.otp)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )

        if not res.data:
            return AuthResponse(success=False, message="Invalid OTP")

        supabase_client.table("users") \
            .update({"is_verified": True}) \
            .eq("email", otp_data.email) \
            .execute()

        return AuthResponse(success=True, message="Email verified")

    except Exception as e:
        print("[Verify Error]", e)
        return AuthResponse(success=False, message="OTP verification failed")


# -------------------------------------------------------------------------
# ✅ LOGIN
# -------------------------------------------------------------------------
@app.post("/login", response_model=AuthResponse)
async def login(data: UserLogin):
    try:
        res = supabase_client.table("users") \
            .select("*") \
            .eq("email", data.email) \
            .execute()

        if not res.data:
            return AuthResponse(success=False, message="User not found")

        user = res.data[0]

        if not verify_password(data.password[:72], user["password_hash"]):
            return AuthResponse(success=False, message="Invalid password")

        if not user.get("is_verified", False):
            return AuthResponse(success=False, message="Verify email first")

        token = create_access_token({"sub": user["email"], "user_id": user["id"]})

        # Return the token in the response
        return {
            "success": True,
            "message": "Login successful",
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user["id"],
                "email": user["email"],
                "full_name": user["full_name"]
            }
        }

    except Exception as e:
        error_msg = str(e)
        print("[Login Error]", e)
        
        # Check for network/connection errors
        if "ConnectError" in str(type(e).__name__) or "getaddrinfo" in error_msg or "httpx" in error_msg:
            return {
                "success": False, 
                "message": "Cannot connect to database. Please check your internet connection and try again."
            }
        
        return {"success": False, "message": "Login failed"}


# -------------------------------------------------------------------------
# ✅ HABITS
# -------------------------------------------------------------------------
@app.post("/submit-habits", response_model=HabitResponse)
async def habits(data: HabitSubmission):
    try:
        body = data.dict()
        body["id"] = str(uuid.uuid4())
        body["created_at"] = iso_now()

        # Try to insert into Supabase DB
        try:
            supabase_client.table("habits").insert(body).execute()
            print(f"✅ Habit saved to Supabase: {body['id']}")
        except Exception as db_error:
            # If network error, save to offline storage instead
            if is_network_error(db_error):
                offline_storage.create_habit(body)
                print(f"⚠️ Supabase unavailable, saved to offline storage: {body['id']}")
            else:
                raise  # Re-raise if it's not a network error
        
        # Predict wellness score using real ML model
        prediction = model_manager.predict_wellness(body)

        return HabitResponse(
            success=True, 
            message="Saved successfully", 
            habit_id=body["id"],
            wellness_score=prediction["wellness_score"]
        )

    except Exception as e:
        error_msg = str(e)
        print("[Habit Error]", e)
        
        # Check for network/connection errors
        if is_network_error(e):
            # Still try to save offline and return success
            try:
                body = data.dict()
                body["id"] = str(uuid.uuid4())
                body["created_at"] = iso_now()
                offline_storage.create_habit(body)
                prediction = model_manager.predict_wellness(body)
                
                return HabitResponse(
                    success=True,
                    message="Saved offline (no internet connection)",
                    habit_id=body["id"],
                    wellness_score=prediction["wellness_score"]
                )
            except:
                pass
        
        return HabitResponse(success=False, message="Error saving habit")



# -------------------------------------------------------------------------
# ✅ INIT ANALYZERS
# -------------------------------------------------------------------------
stress_analyzer = StressAnalyzer()
init_models()


# -------------------------------------------------------------------------
# ✅ AUTHENTICATION DEPENDENCY
# -------------------------------------------------------------------------
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload.get("sub")  # Returns email
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")


# -------------------------------------------------------------------------
# ✅ UPDATED STRESS SCAN (REAL ML PREDICTION)
# -------------------------------------------------------------------------
@app.post("/scan")
async def scan(
    image: UploadFile = File(...), 
    user_id_form: str = Form(None, alias="user_id")
):
    try:
        # Try to get authenticated user (optional)
        user_id = None
        try:
            from fastapi import Request
            # This is a simplified approach - scan works without auth
            if user_id_form:
                user_id = user_id_form
        except:
            pass
        
        print(f"[Scan] Starting scan (user_id: {user_id})")

        raw = await image.read()
        arr = np.frombuffer(raw, np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        print(f"[Scan] Image decoded successfully, shape: {img.shape}")

        # Extract ALL features using updated analyzer
        features = stress_analyzer.extract_features(img)
        print(f"[Scan] Features extracted: {list(features.keys())}")

        # Get prediction using REAL ML model
        prediction = model_manager.predict_stress(features)
        print(f"[Scan] Prediction: {prediction}")

        # Generate ID
        scan_id = str(uuid.uuid4())

        # Save image to static/scans
        filename = f"{scan_id}.jpg"
        filepath = os.path.join("static", "scans", filename)
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        cv2.imwrite(filepath, img)
        print(f"[Scan] Image saved to: {filepath}")
        
        image_url = f"/static/scans/{filename}"

        # Prepare response data
        response_data = {
            "id": scan_id,
            "emotion": features.get("emotion", "neutral"),
            "emotion_confidence": features.get("emotion_confidence", 0.5),
            "mouth_open": features.get("mouth_open", 0.0),
            "eyebrow_raise": features.get("eyebrow_raise", 0.0),
            "jaw_clench_score": features.get("jaw_clench_score", 0.0),
            "posture_quality": features.get("posture_quality", "unknown"),
            "slouch_score": features.get("slouch_score", 0.0),
            "head_tilt_angle": features.get("head_tilt_angle", 0.0),
            "shoulder_alignment_diff": features.get("shoulder_alignment_diff", 0.0),
            "spine_curve_ratio": features.get("spine_curve_ratio", 0.0),
            "pose_confidence": features.get("pose_confidence", 0.0),
            "image_url": image_url,
            "scanned_at": iso_now(),
            "stressPrediction": prediction["stress_prediction"],
            "stressConfidence": prediction["stress_confidence"]
        }

        # Save to database only if user_id is provided
        if user_id:
            try:
                entry = response_data.copy()
                entry["user_id"] = user_id
                # Remove prediction fields (not in DB schema)
                entry.pop("stressPrediction", None)
                entry.pop("stressConfidence", None)
                
                print(f"[Scan] Attempting to insert into database...")
                db_result = supabase_client.table("stress_scan").insert(entry).execute()
                print(f"[Scan] ✅ Database insert successful! ID: {scan_id}")
            except Exception as db_error:
                print(f"[Scan] Database save failed (non-critical): {db_error}")

        return {
            "success": True,
            "data": response_data
        }

    except Exception as e:
        print(f"[Scan Error] {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": "Scan failed",
            "error": str(e)
        }

# -------------------------------------------------------------------------
# ✅ CHATBOT (with graceful fallback)
# -------------------------------------------------------------------------
@app.post("/chat")
async def chat(request: Request):
    try:
        body = await request.json()
        msg = body.get("message", "").strip()

        if not msg:
            return {"success": False, "message": "Empty message"}

        if not OPENROUTER_API_KEY:
            return {"success": True, "message": "AI unavailable. Try later."}

        payload = {
            "model": "meta-llama/llama-3.1-8b-instruct",
            "messages": [
                {"role": "system", "content": "You are a wellness AI assistant."},
                {"role": "user", "content": msg}
            ]
        }

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=15) as client:
            res = await client.post(OPENROUTER_API_URL, headers=headers, json=payload)

        data = res.json()
        reply = data["choices"][0]["message"]["content"]
        return {"success": True, "message": reply}

    except Exception as e:
        print("[Chat Error]", e)
        return {"success": True, "message": "Offline fallback response."}

# -------------------------------------------------------------------------
# ✅ DASHBOARD API ENDPOINTS
# -------------------------------------------------------------------------

@app.get("/api/scans")
async def get_scans(limit: int = 5):
    """Get latest stress scans (no auth required)"""
    try:
        # Try Supabase first
        try:
            response = supabase_client.table("stress_scan") \
                .select("*") \
                .order("scanned_at", desc=True) \
                .limit(limit) \
                .execute()
            scans_data = response.data if hasattr(response, 'data') else []
        except Exception as db_error:
            # Fall back to offline storage if network error
            if is_network_error(db_error):
                print("⚠️ Using offline storage for scans")
                scans_data = offline_storage.get_scans(limit)
            else:
                raise
        
        # Ensure we have data
        if not scans_data:
            return {"success": True, "data": []}
        
        # Format the response and RE-CALCULATE prediction since it's not stored
        scans = []
        for scan in scans_data:
            try:
                # Re-construct feature dict for prediction
                features = {
                    "emotion": scan.get("emotion"),
                    "emotion_confidence": scan.get("emotion_confidence"),
                    "mouth_open": scan.get("mouth_open"),
                    "eyebrow_raise": scan.get("eyebrow_raise"),
                    "jaw_clench_score": scan.get("jaw_clench_score"),
                    "posture_quality": scan.get("posture_quality"),
                    "slouch_score": scan.get("slouch_score"),
                    "head_tilt_angle": scan.get("head_tilt_angle"),
                    "shoulder_alignment_diff": scan.get("shoulder_alignment_diff"),
                    "spine_curve_ratio": scan.get("spine_curve_ratio"),
                    "pose_confidence": scan.get("pose_confidence")
                }
                
                # Run prediction on stored features
                prediction = model_manager.predict_stress(features)
                
                # Convert posture_quality string to numeric value
                posture_str = scan.get("posture_quality", "unknown")
                if posture_str == "good":
                    posture_value = 100.0
                elif posture_str == "fair":
                    posture_value = 60.0
                else:
                    posture_value = 30.0
                
                scans.append({
                    "id": scan.get("id", ""),
                    "emotion": scan.get("emotion", "neutral"),
                    "emotionConfidence": float(scan.get("emotion_confidence", 0.5)),
                    "jawTension": float(scan.get("jaw_clench_score", 0.0)) * 100,
                    "postureQuality": posture_value,
                    "overallStress": 20.0 if prediction["stress_prediction"] == "low" else 50.0 if prediction["stress_prediction"] == "medium" else 80.0,
                    "stressPrediction": prediction["stress_prediction"],
                    "stressConfidence": prediction["stress_confidence"],
                    "timestamp": scan.get("scanned_at", ""),
                    "imageUrl": scan.get("image_url")
                })
            except Exception as e:
                print(f"Error formatting scan {scan.get('id')}: {str(e)}")
                continue
        
        return {
            "success": True,
            "data": scans
        }
        
    except Exception as e:
        print(f"[Scans Error] {str(e)}")
        import traceback
        traceback.print_exc()
        # Return empty data instead of raising exception
        return {"success": True, "data": []}


@app.get("/api/habits")
async def get_habits(limit: int = 5):
    """Get latest habit entries (no auth required)"""
    try:
        # Try Supabase first
        try:
            habits = supabase_client.table("habits") \
                .select("*") \
                .order("created_at", desc=True) \
                .limit(limit) \
                .execute()
            habits_data = habits.data
        except Exception as db_error:
            # Fall back to offline storage if network error
            if is_network_error(db_error):
                print("⚠️ Using offline storage for habits")
                habits_data = offline_storage.get_habits(limit)
            else:
                raise
        
        # Calculate average sleep
        total_sleep = sum(h.get("sleep_hours", 0) for h in habits_data) if habits_data else 0
        avg_sleep = total_sleep / len(habits_data) if habits_data else 0
        
        return {
            "success": True,
            "data": [{
                "id": habit["id"],
                "sleepHours": habit.get("sleep_hours"),
                "exerciseMinutes": habit.get("exercise"), # Schema says 'exercise'
                "waterIntake": habit.get("water_intake"),
                "socialInteraction": habit.get("social_interaction"),
                "timestamp": habit["created_at"],
                "totalHabits": len(habits_data),
                "avgSleep": avg_sleep
            } for habit in habits_data]
        }
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(f"[Habits Error] {str(e)}")
        # Return empty data instead of error
        return {"success": True, "data": []}


@app.get("/api/latest-scan")
async def get_latest_scan():
    """Get the most recent stress scan (no auth required)"""
    try:
        
        # Get latest scan
        scan = supabase_client.table("stress_scan") \
            .select("*") \
            .order("scanned_at", desc=True) \
            .limit(1) \
            .execute()
        
        if not scan.data:
            return {
                "success": True,
                "data": None
            }
        
        scan_data = scan.data[0]
        
        # Re-calculate prediction
        features = {
            "emotion": scan_data.get("emotion"),
            "emotion_confidence": scan_data.get("emotion_confidence"),
            "mouth_open": scan_data.get("mouth_open"),
            "eyebrow_raise": scan_data.get("eyebrow_raise"),
            "jaw_clench_score": scan_data.get("jaw_clench_score"),
            "posture_quality": scan_data.get("posture_quality"),
            "slouch_score": scan_data.get("slouch_score"),
            "head_tilt_angle": scan_data.get("head_tilt_angle"),
            "shoulder_alignment_diff": scan_data.get("shoulder_alignment_diff"),
            "spine_curve_ratio": scan_data.get("spine_curve_ratio"),
            "pose_confidence": scan_data.get("pose_confidence")
        }
        
        prediction = model_manager.predict_stress(features)
        
        return {
            "success": True,
            "data": {
            "id": scan_data["id"],
                "emotion": scan_data["emotion"],
                "emotionConfidence": scan_data["emotion_confidence"],
                "jawTension": scan_data["jaw_clench_score"] * 100,
                "postureQuality": 100.0 if scan_data.get("posture_quality") == "good" else 30.0,
                "stressPrediction": prediction["stress_prediction"],
                "stressConfidence": prediction["stress_confidence"],
                "overallStress": 20.0 if prediction["stress_prediction"] == "low" else 50.0 if prediction["stress_prediction"] == "medium" else 80.0,
                "timestamp": scan_data["scanned_at"],
                "imageUrl": scan_data.get("image_url")
            }
        }
    except Exception as e:
        print(f"[Latest Scan Error] {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch latest scan")

# -------------------------------------------------------------------------
# ✅ MAIN
# -------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)