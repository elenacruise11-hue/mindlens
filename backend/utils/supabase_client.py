import os
from typing import Any, Dict

from supabase import create_client, Client


_SUPABASE_URL = os.getenv("SUPABASE_URL", "")
_SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY", "")

_client: Client | None = None


def get_client() -> Client:
    global _client
    if _client is None:
        if not _SUPABASE_URL or not _SUPABASE_KEY:
            raise RuntimeError("Supabase credentials not configured. Set SUPABASE_URL and SUPABASE_ANON_KEY env vars.")
        _client = create_client(_SUPABASE_URL, _SUPABASE_KEY)
    return _client


async def save_form_data(user_id: str, form_dict: Dict[str, Any]) -> Dict[str, Any]:
    try:
        client = get_client()
        # Remove any accidental extra fields
        payload = {
            "user_id": user_id,
            "timestamp": form_dict.get("timestamp"),
            "sleep_hours": form_dict.get("sleep_hours"),
            "water_intake": form_dict.get("water_intake"),
            "screen_time": form_dict.get("screen_time"),
            "exercise": form_dict.get("exercise"),
            "social_interaction": form_dict.get("social_interaction"),
            "meals": form_dict.get("meals"),
        }

        data, error = client.table("habit_forms").insert(payload).execute()
        if error is not None and getattr(error, "message", None):
            return {"ok": False, "error": error.message}
        return {"ok": True, "data": data}
    except Exception as e:
        return {"ok": False, "error": str(e)}


