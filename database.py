"""
database.py - Supabase database wrapper for MindLens AI
"""

import logging
import os
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from supabase import create_client, Client

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ---------------------------------------------------------
# ✅ Load Supabase client
# ---------------------------------------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "").strip()

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error("❌ Missing SUPABASE_URL or SUPABASE_KEY!")
    supabase: Client = None
else:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    logger.info("✅ Supabase client initialized")


# ---------------------------------------------------------
# ✅ Database wrapper
# ---------------------------------------------------------
class DatabaseClient:
    def __init__(self):
        self.db = supabase
        if self.db:
            logger.info("✅ DatabaseClient connected to Supabase")
        else:
            logger.error("❌ DatabaseClient failed to connect")

    # ---------------------- USERS ----------------------
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        try:
            res = self.db.table("users").select("*").eq("email", email).execute()
            return res.data[0] if res.data else None
        except Exception as e:
            logger.error(f"[DB] get_user_by_email: {e}")
            return None

    def create_user(self, full_name: str, email: str, password_hash: str) -> bool:
        try:
            data = {
                "full_name": full_name,
                "email": email,
                "password_hash": password_hash,
                "is_verified": False,
                "created_at": datetime.utcnow().isoformat(),
            }
            res = self.db.table("users").insert(data).execute()
            return bool(res.data)
        except Exception as e:
            logger.error(f"[DB] create_user: {e}")
            return False

    def verify_user(self, email: str) -> bool:
        try:
            self.db.table("users").update({"is_verified": True}).eq("email", email).execute()
            return True
        except Exception as e:
            logger.error(f"[DB] verify_user: {e}")
            return False

    # ---------------------- OTP ----------------------
    def store_otp(self, email: str, otp: str) -> bool:
        try:
            expires_at = datetime.utcnow() + timedelta(minutes=10)

            self.db.table("otp").insert({
                "email": email,
                "otp": otp,
                "expires_at": expires_at.isoformat(),
                "created_at": datetime.utcnow().isoformat(),
            }).execute()

            return True
        except Exception as e:
            logger.error(f"[DB] store_otp: {e}")
            return False

    def verify_otp(self, email: str, otp: str) -> bool:
        try:
            result = (
                self.db.table("otp")
                .select("*")
                .eq("email", email)
                .eq("otp", otp)
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )

            if not result.data:
                return False

            record = result.data[0]
            expires = datetime.fromisoformat(record["expires_at"])

            return datetime.utcnow() <= expires

        except Exception as e:
            logger.error(f"[DB] verify_otp: {e}")
            return False

    # ---------------------- HABITS ----------------------
    def create_habit_entry(self, habit_data: Dict[str, Any]):
        try:
            res = self.db.table("habits").insert(habit_data).execute()
            return res.data[0] if res.data else None
        except Exception as e:
            logger.error(f"[DB] create_habit_entry: {e}")
            return None

    # ---------------------- STRESS SCAN ----------------------
    def create_stress_scan(self, scan_data: Dict[str, Any]):
        try:
            res = self.db.table("stress_scan").insert(scan_data).execute()
            return res.data[0] if res.data else None
        except Exception as e:
            logger.error(f"[DB] create_stress_scan: {e}")
            return None


# ---------------------------------------------------------
# ✅ Single instance export
# ---------------------------------------------------------
db = DatabaseClient()
supabase_client = supabase   # so legacy calls still work
