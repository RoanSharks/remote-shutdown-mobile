import requests
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Current tunnel URL from your system
TUNNEL_URL = "https://bias-shoot-then-stickers.trycloudflare.com"
SHUTDOWN_URL = f"{TUNNEL_URL}/shutdown"
TOKEN = "admin-shutdown-2024-token-secure"

def test_connection():
    """Test basic connection to the tunnel"""
    print("="*50)
    print("TESTING CONTROLLER CONNECTION")
    print("="*50)
    
    try:
        print(f"1. Testing root URL: {TUNNEL_URL}")
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(TUNNEL_URL, headers=headers, verify=False, timeout=10)
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        
        if response.status_code == 200:
            print("   ✅ Root connection successful!")
        else:
            print("   ❌ Root connection failed!")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "-"*50)
    
    try:
        print(f"2. Testing shutdown endpoint: {SHUTDOWN_URL}")
        headers = {
            "Authorization": f"Bearer {TOKEN}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json"
        }
        
        print(f"   Headers: {headers}")
        response = requests.post(SHUTDOWN_URL, headers=headers, verify=False, timeout=10)
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("   ✅ Shutdown endpoint works! (BUT DON'T ACTUALLY SHUTDOWN)")
        elif response.status_code == 401:
            print("   ❌ Unauthorized - token mismatch")
        elif response.status_code == 404:
            print("   ❌ Endpoint not found - Flask may not be running")
        else:
            print(f"   ❌ Unexpected status code: {response.status_code}")
            
    except requests.exceptions.ConnectionError as e:
        print(f"   ❌ Connection error: {e}")
        print("   💡 Check if tunnel is still running")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("="*50)

if __name__ == "__main__":
    test_connection()