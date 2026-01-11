import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

def test_chat():
    print("💬 Testing Real Chat API...")
    try:
        payload = {"query": "Who is Thanos?", "user_id": "test_user"}
        res = requests.post(f"{BASE_URL}/chat", json=payload)
        if res.status_code == 200:
            data = res.json()
            response = data.get("response", "")
            print(f"   Response Length: {len(response)}")
            if "Add FIREWORKS_API_KEY" in response:
                print("   ❌ FAIL: Still in Mock Mode.")
            else:
                print(f"   ✅ SUCCESS: Real AI Response received! ('{response[:50]}...')")
        else:
            print(f"   ❌ API Error: {res.status_code}")
    except Exception as e:
        print(f"   ⚠️ Connection Error: {e}")

def test_sync_theme():
    print("\n🎭 Testing Scene Theming...")
    try:
        # Timestamp ~200s (Start of movie has action/distress)
        payload = {"timestamp_seconds": 200} 
        res = requests.post(f"{BASE_URL}/sync", json=payload)
        if res.status_code == 200:
            data = res.json()
            print(f"   DEBUG: Full Response: {data}")
            theme = data.get("theme", "unknown")
            print(f"   Timestamp 200s Theme: {theme.upper()}")
            if theme in ["action", "suspense", "emotional", "neutral"]:
                 print("   ✅ SUCCESS: Theme detected.")
            else:
                 print("   ⚠️ WARNING: Unixpected theme value.")
        else:
            print(f"   ❌ API Error: {res.status_code}")
    except Exception as e:
        print(f"   ⚠️ Connection Error: {e}")

if __name__ == "__main__":
    test_chat()
    test_sync_theme()
