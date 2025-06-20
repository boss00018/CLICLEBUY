import os
import sys
import re
import subprocess
import json
from pathlib import Path

def check_dependencies():
    """Check for vulnerable dependencies"""
    print("Checking for vulnerable dependencies...")
    try:
        result = subprocess.run(
            ["pip", "list", "--format=json"], 
            capture_output=True, 
            text=True
        )
        packages = json.loads(result.stdout)
        
        # This is a simplified check - in production you'd use a proper vulnerability database
        vulnerable_packages = {
            "django": "3.0.0",  # Example vulnerable version
            "flask": "0.12.0",
            "requests": "2.18.0",
        }
        
        found_vulnerabilities = []
        for package in packages:
            name = package["name"].lower()
            version = package["version"]
            if name in vulnerable_packages and version <= vulnerable_packages[name]:
                found_vulnerabilities.append(f"{name} {version}")
        
        if found_vulnerabilities:
            print(f"⚠️ Found potentially vulnerable packages: {', '.join(found_vulnerabilities)}")
        else:
            print("✅ No known vulnerable packages found")
            
    except Exception as e:
        print(f"Error checking dependencies: {str(e)}")

def check_secret_key():
    """Check if SECRET_KEY is properly configured"""
    print("\nChecking SECRET_KEY configuration...")
    app_py = Path("app.py").read_text()
    
    if "SECRET_KEY = os.environ.get" in app_py:
        print("✅ SECRET_KEY uses environment variable (good practice)")
    elif "secrets.token_hex" in app_py:
        print("✅ SECRET_KEY uses secure random generation")
    else:
        print("⚠️ SECRET_KEY might not be securely configured")

def check_sql_injection():
    """Check for potential SQL injection vulnerabilities"""
    print("\nChecking for SQL injection vulnerabilities...")
    safe = True
    
    # Check all Python files
    for path in Path(".").glob("**/*.py"):
        content = path.read_text()
        
        # Look for raw SQL queries without parameterization
        if re.search(r"execute\([\"']SELECT.*\+.*", content) or \
           re.search(r"execute\([\"']INSERT.*\+.*", content) or \
           re.search(r"execute\([\"']UPDATE.*\+.*", content) or \
           re.search(r"execute\([\"']DELETE.*\+.*", content):
            print(f"⚠️ Potential SQL injection in {path}")
            safe = False
    
    if safe:
        print("✅ No obvious SQL injection vulnerabilities found")

def check_xss():
    """Check for potential XSS vulnerabilities"""
    print("\nChecking for XSS vulnerabilities...")
    safe = True
    
    # Check all HTML files
    for path in Path("templates").glob("**/*.html"):
        content = path.read_text()
        
        # Look for unescaped variables
        if re.search(r"{{.*\|safe.*}}", content):
            print(f"⚠️ Potential XSS vulnerability in {path} (using |safe filter)")
            safe = False
    
    if safe:
        print("✅ No obvious XSS vulnerabilities found")

def check_cors():
    """Check CORS configuration"""
    print("\nChecking CORS configuration...")
    app_py = Path("app.py").read_text()
    
    if "allow_origins=[\"*\"]" in app_py:
        print("⚠️ CORS allows all origins (*) - consider restricting in production")
    else:
        print("✅ CORS configuration looks restricted")

def check_rate_limiting():
    """Check rate limiting configuration"""
    print("\nChecking rate limiting...")
    if Path("rate_limiter.py").exists():
        print("⚠️ Rate limiting is implemented but disabled")
    else:
        print("⚠️ No rate limiting found")

def check_file_upload():
    """Check file upload security"""
    print("\nChecking file upload security...")
    app_py = Path("app.py").read_text()
    
    if "content_type.startswith(\"image/\")" in app_py:
        print("✅ File upload validates content type")
    else:
        print("⚠️ File upload might not validate content type")
        
    if "MAX_SIZE" in app_py and "file size too large" in app_py:
        print("✅ File upload has size limits")
    else:
        print("⚠️ File upload might not have size limits")

def main():
    print("=" * 50)
    print("CIRCLEBUY Security Check")
    print("=" * 50)
    
    check_dependencies()
    check_secret_key()
    check_sql_injection()
    check_xss()
    check_cors()
    check_rate_limiting()
    check_file_upload()
    
    print("\n" + "=" * 50)
    print("Security check complete")
    print("=" * 50)

if __name__ == "__main__":
    main()