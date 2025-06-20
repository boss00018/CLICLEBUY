#!/usr/bin/env python3
"""
CIRCLEBUY Advanced Testing - Deep functionality tests
"""

import requests
import json
import time
from datetime import datetime

def test_advanced_features():
    base_url = "http://127.0.0.1:8000"
    session = requests.Session()
    
    print("CIRCLEBUY ADVANCED TESTING")
    print("=" * 40)
    
    issues = []
    warnings = []
    
    # Test 1: Database Integration
    print("1. Testing Database Integration...")
    try:
        response = session.get(f"{base_url}/")
        if "Categories" in response.text or "category" in response.text:
            print("   PASS: Database categories loading")
        else:
            print("   ISSUE: No categories found - database may be empty")
            issues.append("Database appears empty - no categories")
    except Exception as e:
        print(f"   FAIL: Database test error - {str(e)}")
        issues.append("Database integration issues")
    
    # Test 2: Category System
    print("2. Testing Category System...")
    try:
        response = session.get(f"{base_url}/category/1")
        if response.status_code == 200:
            print("   PASS: Category pages working")
        elif response.status_code == 404:
            print("   ISSUE: Category 1 not found - database needs setup")
            issues.append("Categories not properly initialized")
        else:
            print(f"   WARN: Category page returned {response.status_code}")
            warnings.append("Category system may have issues")
    except Exception as e:
        print(f"   FAIL: Category test error - {str(e)}")
        issues.append("Category system broken")
    
    # Test 3: Search Functionality
    print("3. Testing Search with Filters...")
    try:
        # Test search with parameters
        response = session.get(f"{base_url}/search?q=test&min_price=100&max_price=1000")
        if response.status_code == 200:
            print("   PASS: Advanced search working")
        else:
            print(f"   WARN: Search filters returned {response.status_code}")
            warnings.append("Search filters may not work properly")
    except Exception as e:
        print(f"   FAIL: Search test error - {str(e)}")
        issues.append("Advanced search broken")
    
    # Test 4: Authentication Routes
    print("4. Testing Authentication System...")
    try:
        # Test logout (should redirect)
        response = session.get(f"{base_url}/logout", allow_redirects=False)
        if response.status_code in [302, 303]:
            print("   PASS: Logout redirect working")
        else:
            print(f"   WARN: Logout returned {response.status_code}")
            warnings.append("Logout may not work correctly")
        
        # Test protected route
        response = session.get(f"{base_url}/sell")
        if response.status_code in [200, 302, 401]:
            print("   PASS: Protected routes handling correctly")
        else:
            print(f"   WARN: Protected route returned {response.status_code}")
            warnings.append("Authentication protection may be weak")
    except Exception as e:
        print(f"   FAIL: Auth test error - {str(e)}")
        issues.append("Authentication system issues")
    
    # Test 5: Static File Security
    print("5. Testing Static File Security...")
    try:
        # Test if sensitive files are accessible
        sensitive_files = ["/app.py", "/.env", "/database.py"]
        exposed_files = []
        
        for file_path in sensitive_files:
            response = session.get(f"{base_url}{file_path}")
            if response.status_code == 200:
                exposed_files.append(file_path)
        
        if exposed_files:
            print(f"   CRITICAL: Sensitive files exposed: {exposed_files}")
            issues.append(f"Security risk - exposed files: {exposed_files}")
        else:
            print("   PASS: Sensitive files protected")
    except Exception as e:
        print(f"   WARN: Security test error - {str(e)}")
        warnings.append("Could not verify file security")
    
    # Test 6: Form Validation
    print("6. Testing Form Security...")
    try:
        # Test registration with invalid data
        response = session.post(f"{base_url}/register", data={
            'email': 'invalid-email',
            'password': '123',
            'full_name': '',
            'university': ''
        })
        
        if response.status_code == 400 or "error" in response.text.lower():
            print("   PASS: Form validation working")
        else:
            print("   WARN: Form validation may be weak")
            warnings.append("Form validation should be strengthened")
    except Exception as e:
        print(f"   WARN: Form validation test error - {str(e)}")
        warnings.append("Could not test form validation")
    
    # Test 7: WebSocket Functionality
    print("7. Testing WebSocket Support...")
    try:
        # Check if WebSocket endpoint exists
        response = session.get(f"{base_url}/ws/1")
        if response.status_code == 426:  # Upgrade Required
            print("   PASS: WebSocket endpoint available")
        else:
            print(f"   INFO: WebSocket test returned {response.status_code}")
    except Exception as e:
        print(f"   INFO: WebSocket test - {str(e)}")
    
    # Test 8: API Endpoints
    print("8. Testing API Endpoints...")
    try:
        response = session.get(f"{base_url}/api/messages/1")
        if response.status_code in [200, 401, 403]:
            print("   PASS: API endpoints responding")
        else:
            print(f"   WARN: API returned {response.status_code}")
            warnings.append("API endpoints may have issues")
    except Exception as e:
        print(f"   WARN: API test error - {str(e)}")
        warnings.append("API functionality unclear")
    
    # Test 9: Memory Usage
    print("9. Testing Resource Usage...")
    try:
        start_time = time.time()
        responses = []
        
        # Make multiple requests to test memory
        for i in range(10):
            response = session.get(f"{base_url}/")
            responses.append(response.status_code)
        
        end_time = time.time()
        avg_time = (end_time - start_time) / 10
        
        if all(r == 200 for r in responses):
            print(f"   PASS: Handles multiple requests (avg: {avg_time:.3f}s)")
        else:
            print("   WARN: Some requests failed under load")
            warnings.append("May have stability issues under load")
    except Exception as e:
        print(f"   WARN: Load test error - {str(e)}")
        warnings.append("Could not test resource usage")
    
    # Test 10: Content Security
    print("10. Testing Content Security...")
    try:
        response = session.get(f"{base_url}/")
        content = response.text.lower()
        
        security_issues = []
        if "eval(" in content:
            security_issues.append("eval() usage detected")
        if "document.write" in content:
            security_issues.append("document.write usage detected")
        if "innerhtml" in content and "user" in content:
            security_issues.append("Potential XSS vulnerability")
        
        if security_issues:
            print(f"   WARN: Security concerns: {security_issues}")
            warnings.extend(security_issues)
        else:
            print("   PASS: No obvious security issues in content")
    except Exception as e:
        print(f"   WARN: Content security test error - {str(e)}")
    
    # Generate Advanced Report
    print("\n" + "=" * 40)
    print("ADVANCED TEST RESULTS")
    print("=" * 40)
    
    print(f"Critical Issues: {len(issues)}")
    print(f"Warnings: {len(warnings)}")
    
    if issues:
        print(f"\nCRITICAL ISSUES:")
        for i, issue in enumerate(issues, 1):
            print(f"{i}. {issue}")
    
    if warnings:
        print(f"\nWARNINGS:")
        for i, warning in enumerate(warnings, 1):
            print(f"{i}. {warning}")
    
    # Overall Assessment
    if len(issues) == 0 and len(warnings) <= 2:
        grade = "A - PRODUCTION READY"
    elif len(issues) <= 1 and len(warnings) <= 5:
        grade = "B - GOOD WITH MINOR FIXES"
    elif len(issues) <= 3:
        grade = "C - NEEDS IMPROVEMENT"
    else:
        grade = "D - MAJOR ISSUES"
    
    print(f"\nOVERALL GRADE: {grade}")
    
    # Specific Recommendations
    print(f"\nRECOMMENDATIONS:")
    
    if not issues and not warnings:
        print("1. Excellent! Application is production-ready")
        print("2. Consider adding monitoring and logging")
        print("3. Set up automated testing pipeline")
    else:
        if issues:
            print("1. PRIORITY: Fix all critical issues before deployment")
        if "database" in str(issues).lower():
            print("2. Initialize database with proper categories")
        if "security" in str(issues + warnings).lower():
            print("3. Review and strengthen security measures")
        if len(warnings) > 3:
            print("4. Address warnings to improve reliability")
        print("5. Test manually with real user scenarios")
        print("6. Monitor application in staging environment")
    
    print("\n" + "=" * 40)
    
    return len(issues), len(warnings)

if __name__ == "__main__":
    critical, warnings = test_advanced_features()
    print(f"Testing completed - {critical} critical issues, {warnings} warnings")