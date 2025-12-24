"""
API Utility Functions
Helper functions for API endpoints
"""
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

# Configure logging
logger = logging.getLogger(__name__)

class APIError(Exception):
    """Base class for API errors"""
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST, details: Any = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Get the current authenticated user.
    This is a placeholder - replace with your actual authentication logic.
    """
    try:
        # In a real app, validate the JWT token and get user info
        # For now, return a mock user
        return {
            "id": "user_123",  # This would come from the token
            "email": "user@example.com",
            "is_verified": True
        }
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def format_error_response(error: Exception) -> Dict[str, Any]:
    """Format an error response in a consistent way"""
    if isinstance(error, APIError):
        return {
            "status": "error",
            "message": error.message,
            "code": error.status_code,
            "details": error.details
        }
    
    logger.error(f"Unhandled error: {str(error)}", exc_info=True)
    return {
        "status": "error",
        "message": "An unexpected error occurred",
        "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "details": str(error) if str(error) else None
    }

def validate_stress_scan_data(data: Dict[str, Any]) -> None:
    """Validate stress scan input data"""
    required_fields = ["face_metrics", "posture_metrics"]
    for field in required_fields:
        if field not in data:
            raise APIError(f"Missing required field: {field}")
    
    # Add more specific validation as needed
    if not isinstance(data["face_metrics"], dict) or not isinstance(data["posture_metrics"], dict):
        raise APIError("Invalid data format: face_metrics and posture_metrics must be objects")

def validate_health_metrics(data: Dict[str, Any]) -> None:
    """Validate health metrics input data"""
    if not isinstance(data, dict):
        raise APIError("Health metrics must be an object")
    
    # Add validation for specific fields if needed
    if "blood_pressure" in data:
        bp = data["blood_pressure"]
        if not isinstance(bp, dict) or "systolic" not in bp or "diastolic" not in bp:
            raise APIError("Blood pressure must include both systolic and diastolic values")

def format_stress_scan_response(scan: Dict[str, Any]) -> Dict[str, Any]:
    """Format a stress scan record for API response"""
    return {
        "id": scan.get("id"),
        "scanned_at": scan.get("scanned_at"),
        "emotion": scan.get("emotion"),
        "emotion_confidence": scan.get("emotion_confidence"),
        "jaw_tension": scan.get("jaw_tension"),
        "posture_quality": scan.get("posture_quality"),
        "overall_stress": scan.get("overall_stress"),
        "image_url": scan.get("image_url")
    }

def format_health_metrics_response(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Format health metrics for API response"""
    return {
        "id": metrics.get("id"),
        "recorded_at": metrics.get("recorded_at"),
        "blood_pressure": {
            "systolic": metrics.get("blood_pressure_systolic"),
            "diastolic": metrics.get("blood_pressure_diastolic"),
            "category": metrics.get("blood_pressure_category")
        },
        "heart_rate": metrics.get("heart_rate"),
        "cholesterol": metrics.get("cholesterol"),
        "glucose": metrics.get("glucose"),
        "insulin": metrics.get("insulin"),
        "stress_level": metrics.get("stress_level"),
        "mental_health_score": metrics.get("mental_health_score")
    }

def calculate_stress_trend(stress_levels: List[float]) -> str:
    """Calculate stress trend based on recent stress levels"""
    if not stress_levels or len(stress_levels) < 2:
        return "stable"
    
    # Simple trend calculation (could be enhanced with more sophisticated logic)
    avg_first_half = sum(stress_levels[:len(stress_levels)//2]) / (len(stress_levels)//2)
    avg_second_half = sum(stress_levels[len(stress_levels)//2:]) / (len(stress_levels) - len(stress_levels)//2)
    
    if abs(avg_second_half - avg_first_half) < 0.5:
        return "stable"
    elif avg_second_half > avg_first_half:
        return "increasing"
    else:
        return "decreasing"
