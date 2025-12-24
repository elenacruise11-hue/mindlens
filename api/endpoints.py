"""
API Endpoints for MinLens Application
Handles stress scan and health prediction requests.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime
import logging

from ..model_manager import model_manager
from ..stress_models import StressScanRecord
from ..ml_model import HealthRiskPredictor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Mock user authentication (replace with your actual auth system)
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Mock user authentication - replace with your actual auth system."""
    # In a real app, validate the token and return the user
    return {"user_id": "test_user", "email": "user@example.com"}

class StressScanRequest(BaseModel):
    """Request model for stress scan prediction."""
    face_metrics: Dict[str, Any]
    posture_metrics: Dict[str, Any]
    image_url: Optional[str] = None

class HealthPredictionRequest(BaseModel):
    """Request model for health prediction."""
    lifestyle_data: Dict[str, Any]

@router.post("/predict/stress-scan", response_model=Dict[str, Any])
async def predict_stress_scan(
    request: StressScanRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Predict stress-related metrics from facial and posture analysis.
    
    This endpoint accepts facial metrics (jaw clench, eyebrow raise, etc.) and
    posture metrics (slouch, head tilt, etc.) and returns stress-related predictions.
    """
    try:
        # Get predictions from model manager
        result = model_manager.predict_stress_scan(
            face_metrics=request.face_metrics,
            posture_metrics=request.posture_metrics
        )
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"]
            )
        
        # Create record to save to database
        record = StressScanRecord(
            user_id=current_user["user_id"],
            scanned_at=datetime.utcnow(),
            emotion=result.get("emotion"),
            emotion_confidence=result.get("emotion_confidence"),
            mouth_open=request.face_metrics.get("mouth_open"),
            eyebrow_raise=request.face_metrics.get("eyebrow_raise"),
            jaw_clench_score=request.face_metrics.get("jaw_clench_score"),
            posture_quality=result.get("posture_quality"),
            slouch_score=request.posture_metrics.get("slouch_score"),
            head_tilt_angle=request.posture_metrics.get("head_tilt_angle"),
            shoulder_alignment_diff=request.posture_metrics.get("shoulder_alignment_diff"),
            image_url=request.image_url
        )
        
        # TODO: Save record to database
        # await save_stress_scan_record(record)
        
        return {
            "status": "success",
            "data": result,
            "record_id": str(record.id) if record.id else None
        }
        
    except Exception as e:
        logger.error(f"Error in stress scan prediction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process stress scan: {str(e)}"
        )

@router.post("/predict/health", response_model=Dict[str, Any])
async def predict_health_metrics(
    request: HealthPredictionRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Predict health metrics from lifestyle and habit data.
    
    This endpoint accepts lifestyle information (sleep, exercise, diet, etc.)
    and returns predicted health metrics.
    """
    try:
        # Get predictions from model manager
        result = model_manager.predict_health_metrics(
            lifestyle_data=request.lifestyle_data
        )
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"]
            )
        
        # TODO: Save health metrics to database
        # await save_health_metrics(current_user["user_id"], result)
        
        return {
            "status": "success",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Error in health prediction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to predict health metrics: {str(e)}"
        )

@router.get("/dashboard/summary", response_model=Dict[str, Any])
async def get_dashboard_summary(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get a summary of the user's health and stress metrics for the dashboard.
    
    Returns the most recent stress scan and health prediction results,
    along with personalized recommendations.
    """
    try:
        # TODO: Fetch recent records from database
        # recent_stress_scans = await get_recent_stress_scans(current_user["user_id"], limit=5)
        # recent_health_metrics = await get_recent_health_metrics(current_user["user_id"], limit=1)
        
        # Mock data for demonstration
        recent_stress_scans = [
            {
                "emotion": "neutral",
                "emotion_confidence": 0.85,
                "jaw_tension": 0.3,
                "posture_quality": "fair",
                "overall_stress": 4.2,
                "timestamp": "2023-11-05T12:00:00Z"
            }
        ]
        
        recent_health_metrics = {
            "blood_pressure": {"systolic": 118, "diastolic": 75, "category": "normal"},
            "heart_rate": 72,
            "cholesterol": 180,
            "glucose": 92,
            "insulin": 3.8,
            "stress_level": 4.2,
            "mental_health_score": 75,
            "timestamp": "2023-11-05T12:00:00Z"
        }
        
        # Generate recommendations
        latest_stress = recent_stress_scans[0] if recent_stress_scans else {}
        recommendations = model_manager.generate_recommendations(
            stress_metrics=latest_stress,
            health_metrics=recent_health_metrics
        )
        
        # Calculate trends (simplified)
        stress_trend = "stable"
        health_trend = "improving"
        
        return {
            "status": "success",
            "data": {
                "stress_metrics": latest_stress,
                "health_metrics": recent_health_metrics,
                "recommendations": recommendations,
                "trends": {
                    "stress": stress_trend,
                    "health": health_trend
                },
                "last_updated": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating dashboard summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate dashboard summary: {str(e)}"
        )
