# database/client.py

import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class DatabaseClient:
    def __init__(self, url: str | None = None, key: str | None = None):
        self.url = (url or os.getenv("SUPABASE_URL")).strip()
        self.key = (key or os.getenv("SUPABASE_KEY")).strip()

        if not self.url or not self.key:
            raise ValueError("❌ Missing SUPABASE_URL or SUPABASE_KEY in .env")

        # Works with supabase==1.0.3 (stable legacy version)
        self.client: Client = create_client(self.url, self.key)

    def get_client(self) -> Client:
        return self.client


# Global instance
supabase_client = DatabaseClient().get_client()
