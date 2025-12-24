"""
Offline Mode Manager - Provides local storage fallback when Supabase is unavailable
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

class OfflineStorage:
    """Simple JSON file-based storage for offline mode"""
    
    def __init__(self, data_dir="offline_data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize data files
        self.users_file = os.path.join(data_dir, "users.json")
        self.habits_file = os.path.join(data_dir, "habits.json")
        self.scans_file = os.path.join(data_dir, "stress_scans.json")
        
        # Create files if they don't exist
        for file in [self.users_file, self.habits_file, self.scans_file]:
            if not os.path.exists(file):
                with open(file, 'w') as f:
                    json.dump([], f)
    
    def _read_file(self, filepath: str) -> List[Dict]:
        """Read JSON file"""
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def _write_file(self, filepath: str, data: List[Dict]):
        """Write JSON file"""
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    # Users
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        users = self._read_file(self.users_file)
        for user in users:
            if user.get("email") == email:
                return user
        return None
    
    def create_user(self, user_data: Dict) -> bool:
        users = self._read_file(self.users_file)
        users.append(user_data)
        self._write_file(self.users_file, users)
        return True
    
    def update_user(self, email: str, updates: Dict) -> bool:
        users = self._read_file(self.users_file)
        for user in users:
            if user.get("email") == email:
                user.update(updates)
                self._write_file(self.users_file, users)
                return True
        return False
    
    # Habits
    def create_habit(self, habit_data: Dict) -> Dict:
        habits = self._read_file(self.habits_file)
        habits.append(habit_data)
        self._write_file(self.habits_file, habits)
        return habit_data
    
    def get_habits(self, limit: int = 5) -> List[Dict]:
        habits = self._read_file(self.habits_file)
        # Sort by created_at descending
        habits.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return habits[:limit]
    
    # Stress Scans
    def create_scan(self, scan_data: Dict) -> Dict:
        scans = self._read_file(self.scans_file)
        scans.append(scan_data)
        self._write_file(self.scans_file, scans)
        return scan_data
    
    def get_scans(self, limit: int = 5) -> List[Dict]:
        scans = self._read_file(self.scans_file)
        # Sort by scanned_at descending
        scans.sort(key=lambda x: x.get("scanned_at", ""), reverse=True)
        return scans[:limit]
    
    def get_latest_scan(self) -> Optional[Dict]:
        scans = self.get_scans(limit=1)
        return scans[0] if scans else None


# Global offline storage instance
offline_storage = OfflineStorage()


def is_network_error(exception: Exception) -> bool:
    """Check if an exception is a network/connection error"""
    error_msg = str(exception)
    error_type = str(type(exception).__name__)
    
    network_indicators = [
        "ConnectError", "getaddrinfo", "httpx", "ConnectionError",
        "TimeoutError", "NetworkError", "DNSError"
    ]
    
    return any(indicator in error_type or indicator in error_msg 
               for indicator in network_indicators)
