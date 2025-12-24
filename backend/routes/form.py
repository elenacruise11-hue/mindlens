from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, conint
from typing import Any, Dict
from datetime import datetime, timezone

from utils.supabase_client import save_form_data
from utils.ml_utils import prepare_features, predict


router = APIRouter()


class HabitForm(BaseModel):
    user_id: str = Field(..., description="User identifier")
    sleep_hours: conint(ge=0, le=24)  # type: ignore
    water_intake: conint(ge=0, le=50)  # glasses
    screen_time: conint(ge=0, le=24)  # hours
    exercise: bool
    social_interaction: conint(ge=0, le=5)
    meals: conint(ge=0, le=12)


@router.post("/submit")
async def submit_form(payload: HabitForm) -> Dict[str, Any]:
    try:
        form_dict = payload.model_dict() if hasattr(payload, "model_dict") else payload.model_dump()
        timestamp = datetime.now(timezone.utc).isoformat()

        db_payload = {
            "user_id": form_dict["user_id"],
            "timestamp": timestamp,
            "sleep_hours": form_dict["sleep_hours"],
            "water_intake": form_dict["water_intake"],
            "screen_time": form_dict["screen_time"],
            "exercise": form_dict["exercise"],
            "social_interaction": form_dict["social_interaction"],
            "meals": form_dict["meals"],
        }

        saved = await save_form_data(form_dict["user_id"], db_payload)
        if not saved["ok"]:
            return {"status": "error", "message": saved.get("error", "Failed to save")}

        features = prepare_features(form_dict)
        _ = predict(features)  # placeholder for future use

        return {
            "status": "saved",
            "data": db_payload,
            "features": features,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


