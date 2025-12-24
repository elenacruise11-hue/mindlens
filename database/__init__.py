# database/__init__.py

from .client import DatabaseClient
from config import settings

# ✅ Create a singleton instance of DatabaseClient using values from config.py
db = DatabaseClient(settings.SUPABASE_URL, settings.SUPABASE_KEY)

# ✅ Expose the Supabase client object for direct queries if needed
supabase_client = db.get_client()
