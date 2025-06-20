import requests
import time

def test_application():
    """Simple test to verify the application is working"""
    base_url = "http://127.0.0.1:8000"
    
    print("Testing CIRCLEBUY Application")
    print("=" * 40)
    
    # Test homepage
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Homepage loads successfully")
        else:
            print(f"❌ Homepage failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Homepage test failed: {str(e)}")
    
    # Test login page
    try:
        response = requests.get(f"{base_url}/login")
        if response.status_code == 200:
            print("✅ Login page loads successfully")
        else:
            print(f"❌ Login page failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Login page test failed: {str(e)}")
    
    # Test register page
    try:
        response = requests.get(f"{base_url}/register")
        if response.status_code == 200:
            print("✅ Register page loads successfully")
        else:
            print(f"❌ Register page failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Register page test failed: {str(e)}")
    
    # Test category page
    try:
        response = requests.get(f"{base_url}/category/1")
        if response.status_code == 200:
            print("✅ Category page loads successfully")
        else:
            print(f"❌ Category page failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Category page test failed: {str(e)}")
    
    # Test search redirect
    try:
        response = requests.get(f"{base_url}/search", allow_redirects=False)
        if response.status_code in [302, 200]:
            print("✅ Search redirect works")
        else:
            print(f"❌ Search failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Search test failed: {str(e)}")
    
    print("=" * 40)
    print("Basic functionality test completed")

if __name__ == "__main__":
    test_application()