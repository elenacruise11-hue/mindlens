from typing import Dict, Any


def prepare_features(form_dict: Dict[str, Any]) -> Dict[str, int]:
    sleep_hours = int(form_dict.get("sleep_hours", 0) or 0)
    water_intake = int(form_dict.get("water_intake", 0) or 0)
    screen_time = int(form_dict.get("screen_time", 0) or 0)
    exercise_bool = bool(form_dict.get("exercise", False))
    exercise = 1 if exercise_bool else 0
    social_interaction = int(form_dict.get("social_interaction", 0) or 0)
    meals = int(form_dict.get("meals", 0) or 0)

    return {
        "sleep_hours": sleep_hours,
        "water_intake": water_intake,
        "screen_time": screen_time,
        "exercise": exercise,
        "social_interaction": social_interaction,
        "meals": meals,
    }


def predict(features: Dict[str, int]) -> Dict[str, Any]:
    # Placeholder – to be replaced by real model
    return {"stress_percent": 0, "level": "Low (placeholder)"}


