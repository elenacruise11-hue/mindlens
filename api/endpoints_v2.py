""
API Endpoints v2
Updated endpoints with database integration
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

from . import utils
from ..model_manager import model_manager
from ..database import supabase_client

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/stress-scan", response_model=Dict[str, Any])
async def process_stress_scan(
    scan_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(utils.get_current_user)
):
    """
    Process a stress scan with facial and posture analysis.
    
    Request body should include:
    - face_metrics: Dict containing facial expression metrics
    - posture_metrics: Dict containing posture analysis metrics
    - image_url: Optional URL to the scanned image
    """
    try:
        # Validate input data
        utils.validate_stress_scan_data(scan_data)
        
        # Get predictions from model
        prediction = model_manager.predict_stress_scan(
            face_metrics=scan_data["face_metrics"],
            posture_metrics=scan_data["posture_metrics"]
        )
        
        if "error" in prediction:
            raise utils.APIError(
                message="Failed to process stress scan",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error": prediction["error"]}
            )
        
        # Prepare data for storage
        scan_record = {
            **prediction,
            "raw_metrics": {
                "face_metrics": scan_data["face_metrics"],
                "posture_metrics": scan_data["posture_metrics"]
            },
            "image_url": scan_data.get("image_url")
        }
        
        # Save to database
        saved_scan = await supabase_client.save_stress_scan(
            user_id=current_user["id"],
            scan_data=scan_record
        )
        
        if not saved_scan:
            raise utils.APIError(
                message="Failed to save stress scan",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Format response
        response = {
            "status": "success",
            "data": utils.format_stress_scan_response(saved_scan),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return response
        
    except utils.APIError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=utils.format_error_response(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in process_stress_scan: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=utils.format_error_response(e)
        )

@router.post("/health-metrics", response_model=Dict[str, Any])
async def process_health_metrics(
    metrics_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(utils.get_current_user)
):
    """
    Process and store health metrics.
    
    Request body should include health metrics like:
    - blood_pressure: {systolic: int, diastolic: int}
    - heart_rate: int
    - cholesterol: int
    - glucose: int
    - insulin: float
    - stress_level: float
    - mental_health_score: int
    """
    try:
        # Validate input data
        utils.validate_health_metrics(metrics_data)
        
        # Get predictions from model (if needed)
        # For now, we'll just use the provided metrics
        
        # Save to database
        saved_metrics = await supabase_client.save_health_metrics(
            user_id=current_user["id"],
            metrics=metrics_data
        )
        
        if not saved_metrics:
            raise utils.APIError(
                message="Failed to save health metrics",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Format response
        response = {
            "status": "success",
            "data": utils.format_health_metrics_response(saved_metrics),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return response
        
    except utils.APIError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=utils.format_error_response(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in process_health_metrics: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=utils.format_error_response(e)
        )

@router.get("/dashboard/summary", response_model=Dict[str, Any])
async def get_dashboard_summary(
    current_user: Dict[str, Any] = Depends(utils.get_current_user)
):
    """
    Get a summary of the user's health and stress data for the dashboard.
    """
    try:
        # Get recent data from database
        recent_scans = await supabase_client.get_recent_stress_scans(
            user_id=current_user["id"],
            limit=5
        )
        
        recent_metrics = await supabase_client.get_recent_health_metrics(
            user_id=current_user["id"],
            limit=1
        )
        
        # Get user preferences
        preferences = await supabase_client.get_user_preferences(
            user_id=current_user["id"]
        )
        
        # Calculate trends
        stress_trend = utils.calculate_stress_trend(
            [scan["overall_stress"] for scan in recent_scans if "overall_stress" in scan]
        )
        
        # Generate recommendations
        latest_scan = recent_scans[0] if recent_scans else {}
        latest_metrics = recent_metrics[0] if recent_metrics else {}
        
        recommendations = model_manager.generate_recommendations(
            stress_metrics=latest_scan,
            health_metrics=latest_metrics
        )
        
        # Format response
        response = {
            "status": "success",
            "data": {
                "user": {
                    "id": current_user["id"],
                    "email": current_user["email"]
                },
                "stress": {
                    "recent_scans": [utils.format_stress_scan_response(scan) for scan in recent_scans],
                    "trend": stress_trend
                },
                "health": {
                    "latest_metrics": utils.format_health_metrics_response(latest_metrics) if latest_metrics else {},
                    "trend": "stable"  # Could be calculated from historical data
                },
                "recommendations": recommendations,
                "preferences": preferences
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Error in get_dashboard_summary: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=utils.format_error_response(e)
        )

@router.get("/stress/history", response_model=Dict[str, Any])
async def get_stress_history(
    days: int = 30,
    current_user: Dict[str, Any] = Depends(utils.get_current_user)
):
    """
    Get historical stress data for the specified time period.
    """
    try:
        # Validate input
        if not 1 <= days <= 365:
            raise utils.APIError(
                message="Days parameter must be between 1 and 365",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Get historical data
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # This would be implemented in the database client
        # For now, we'll use the recent scans endpoint
        scans = await supabase_client.get_recent_stress_scans(
            user_id=current_user["id"],
            limit=100  # Adjust based on needs
        )
        
        # Filter by date range
        filtered_scans = [
            scan for scan in scans 
            if datetime.fromisoformat(scan["scanned_at"]) >= start_date
        ]
        
        # Format response
        response = {
            "status": "success",
            "data": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "scans": [utils.format_stress_scan_response(scan) for scan in filtered_scans]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return response
        
    except utils.APIError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=utils.format_error_response(e)
        )
    except Exception as e:
        logger.error(f"Error in get_stress_history: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=utils.format_error_response(e)
        )
