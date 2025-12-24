"""
Quick Network Diagnostic Script for MindLens AI
Tests connectivity to Supabase and identifies the issue
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("🔍 MindLens AI - Network Diagnostic Tool")
print("=" * 60)

# Test 1: Check environment variables
print("\n[1/5] Checking environment variables...")
SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "").strip()

if SUPABASE_URL and SUPABASE_KEY:
    print(f"✅ SUPABASE_URL: {SUPABASE_URL}")
    print(f"✅ SUPABASE_KEY: {SUPABASE_KEY[:20]}...")
else:
    print("❌ Missing Supabase credentials in .env")
    sys.exit(1)

# Test 2: Check internet connectivity
print("\n[2/5] Testing basic internet connectivity...")
try:
    import socket
    socket.create_connection(("8.8.8.8", 53), timeout=3)
    print("✅ Internet connection is active")
except Exception as e:
    print(f"❌ No internet connection: {e}")
    print("   → Please check your network connection")
    sys.exit(1)

# Test 3: DNS Resolution
print("\n[3/5] Testing DNS resolution...")
try:
    import socket
    hostname = SUPABASE_URL.replace("https://", "").replace("http://", "")
    ip = socket.gethostbyname(hostname)
    print(f"✅ DNS resolved {hostname} → {ip}")
except Exception as e:
    print(f"❌ DNS resolution failed: {e}")
    print("   → Try changing DNS to 8.8.8.8 (Google DNS)")
    sys.exit(1)

# Test 4: HTTP Connection with requests
print("\n[4/5] Testing HTTP connection with requests library...")
try:
    import requests
    response = requests.get(SUPABASE_URL, timeout=10)
    print(f"✅ HTTP connection successful (Status: {response.status_code})")
except Exception as e:
    print(f"❌ HTTP connection failed: {e}")
    print("   → Check firewall/proxy settings")
    sys.exit(1)

# Test 5: Supabase Client Connection
print("\n[5/5] Testing Supabase client connection...")
try:
    from supabase import create_client
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    result = supabase.table("users").select("email").limit(1).execute()
    print(f"✅ Supabase connection successful!")
    print(f"   Found {len(result.data)} user(s) in database")
except Exception as e:
    print(f"❌ Supabase connection failed: {e}")
    print("   → Check Supabase credentials and project status")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED! Your connection is working.")
print("=" * 60)
print("\nIf login still fails, the issue might be:")
print("  • User credentials (wrong email/password)")
print("  • User not verified (check email for OTP)")
print("  • Database schema mismatch")
