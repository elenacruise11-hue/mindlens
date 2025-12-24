from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime


# ==============================
# ✅ AUTH MODELS
# ==============================

class UserSignup(BaseModel):
    full_name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class OTPVerification(BaseModel):
    email: EmailStr
    otp: str


class UserResponse(BaseModel):
    id: str
    full_name: str
    email: str
    is_verified: bool
    created_at: Optional[datetime] = None


class AuthResponse(BaseModel):
    success: bool
    message: str
    user: Optional[Dict[str, Any]] = None       # ✅ Accept raw DB JSON
    access_token: Optional[str] = None


# ==============================
# ✅ HABIT MODELS
# ==============================

class HabitSubmission(BaseModel):
    user_id: str
    age: int
    sleep_hours: float
    work_hours: float
    screen_time: float
    water_intake: float
    exercise: bool
    meals_per_day: int
    social_interaction: str
    caffeine_intake: bool


class HabitResponse(BaseModel):
    success: bool
    message: str
    habit_id: Optional[str] = None


# ==============================
# ✅ STRESS SCANNER MODELS
# ==============================

class StressScanResult(BaseModel):
    user_id: str
    emotion: Optional[str] = None
    emotion_confidence: Optional[float] = None
    mouth_open: Optional[float] = None
    eyebrow_raise: Optional[float] = None
    jaw_clench_score: Optional[float] = None
    posture_quality: Optional[str] = None
    slouch_score: Optional[float] = None
    head_tilt_angle: Optional[float] = None
    shoulder_alignment_diff: Optional[float] = None
    spine_curve_ratio: Optional[float] = None
    pose_confidence: Optional[float] = None
    image_url: Optional[str] = None
    scanned_at: Optional[datetime] = None
