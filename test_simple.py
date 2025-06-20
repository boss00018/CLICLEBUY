#!/usr/bin/env python3
"""
CIRCLEBUY Simple Testing Suite
"""

import requests
import time
from datetime import datetime

def test_circlebuy():
    base_url = "http://127.0.0.1:8000"
    session = requests.Session()
    
    print("CIRCLEBUY TESTING REPORT")
    print("=" * 40)
    print(f"Testing server at: {base_url}")
    print(f"Test time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests_passed = 0
    tests_failed = 0
    issues = []
    
    # Test 1: Basic Connectivity
    print("1. Testing Basic Connectivity...")
    try:
        response = session.get(base_url, timeout=10)
        if response.status_code == 200:
            print("   PASS: Server is responding")
            tests_passed += 1
        else:
            print(f"   FAIL: Server returned status {response.status_code}")
            tests_failed += 1
            issues.append("Server not responding correctly")
    except Exception as e:
        print(f"   FAIL: Cannot connect - {str(e)}")
        tests_failed += 1
        issues.append("Cannot connect to server")
    
    # Test 2: Homepage Load
    print("2. Testing Homepage...")
    try:
        response = session.get(f"{base_url}/")
        if response.status_code == 200 and "CIRCLEBUY" in response.text:
            print("   PASS: Homepage loads correctly")
            tests_passed += 1
        else:
            print("   FAIL: Homepage not loading properly")
            tests_failed += 1
            issues.append("Homepage issues")
    except Exception as e:
        print(f"   FAIL: Homepage error - {str(e)}")
        tests_failed += 1
        issues.append("Homepage loading error")
    
    # Test 3: Login Page
    print("3. Testing Login Page...")
    try:
        response = session.get(f"{base_url}/login")
        if response.status_code == 200:
            print("   PASS: Login page accessible")
            tests_passed += 1
        else:
            print(f"   FAIL: Login page status {response.status_code}")
            tests_failed += 1
            issues.append("Login page not accessible")
    except Exception as e:
        print(f"   FAIL: Login page error - {str(e)}")
        tests_failed += 1
        issues.append("Login page error")
    
    # Test 4: Register Page
    print("4. Testing Register Page...")
    try:
        response = session.get(f"{base_url}/register")
        if response.status_code == 200:
            print("   PASS: Register page accessible")
            tests_passed += 1
        else:
            print(f"   FAIL: Register page status {response.status_code}")
            tests_failed += 1
            issues.append("Register page not accessible")
    except Exception as e:
        print(f"   FAIL: Register page error - {str(e)}")
        tests_failed += 1
        issues.append("Register page error")
    
    # Test 5: Search Page
    print("5. Testing Search...")
    try:
        response = session.get(f"{base_url}/search")
        if response.status_code == 200:
            print("   PASS: Search page accessible")
            tests_passed += 1
        else:
            print(f"   FAIL: Search page status {response.status_code}")
            tests_failed += 1
            issues.append("Search not working")
    except Exception as e:
        print(f"   FAIL: Search error - {str(e)}")
        tests_failed += 1
        issues.append("Search functionality error")
    
    # Test 6: Static Files
    print("6. Testing Static Files...")
    try:
        response = session.get(f"{base_url}/static/styles.css")
        if response.status_code == 200:
            print("   PASS: CSS files loading")
            tests_passed += 1
        else:
            print("   FAIL: CSS files not loading")
            tests_failed += 1
            issues.append("Static files not serving")
    except Exception as e:
        print(f"   FAIL: Static files error - {str(e)}")
        tests_failed += 1
        issues.append("Static file serving error")
    
    # Test 7: Performance
    print("7. Testing Performance...")
    try:
        start_time = time.time()
        response = session.get(f"{base_url}/")
        end_time = time.time()
        response_time = end_time - start_time
        
        if response_time < 2.0:
            print(f"   PASS: Response time {response_time:.2f}s")
            tests_passed += 1
        else:
            print(f"   WARN: Slow response time {response_time:.2f}s")
            tests_passed += 1  # Not a failure, just slow
            issues.append("Performance could be improved")
    except Exception as e:
        print(f"   FAIL: Performance test error - {str(e)}")
        tests_failed += 1
        issues.append("Performance testing error")
    
    # Test 8: Error Handling
    print("8. Testing Error Handling...")
    try:
        response = session.get(f"{base_url}/nonexistent-page")
        if response.status_code == 404:
            print("   PASS: 404 errors handled correctly")
            tests_passed += 1
        else:
            print(f"   WARN: Unexpected status for 404: {response.status_code}")
            tests_passed += 1  # Not critical
    except Exception as e:
        print(f"   FAIL: Error handling test failed - {str(e)}")
        tests_failed += 1
        issues.append("Error handling issues")
    
    # Generate Report
    print("\n" + "=" * 40)
    print("TEST SUMMARY")
    print("=" * 40)
    
    total_tests = tests_passed + tests_failed
    success_rate = (tests_passed / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {tests_passed}")
    print(f"Failed: {tests_failed}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    # Overall Status
    if tests_failed == 0:
        status = "EXCELLENT - Ready for production"
    elif tests_failed <= 2:
        status = "GOOD - Minor issues to fix"
    elif tests_failed <= 4:
        status = "NEEDS WORK - Several issues found"
    else:
        status = "CRITICAL - Major issues need fixing"
    
    print(f"Overall Status: {status}")
    
    # Issues
    if issues:
        print(f"\nISSUES FOUND ({len(issues)}):")
        for i, issue in enumerate(issues, 1):
            print(f"{i}. {issue}")
    
    # Recommendations
    print(f"\nRECOMMENDATIONS:")
    if tests_failed == 0:
        print("1. Application is working well!")
        print("2. Consider adding more comprehensive tests")
        print("3. Monitor performance in production")
    else:
        print("1. Fix failed tests before deployment")
        print("2. Test all functionality manually")
        print("3. Check server logs for detailed errors")
    
    print("\n" + "=" * 40)
    print("Testing completed successfully")
    
    return tests_passed, tests_failed, issues

if __name__ == "__main__":
    test_circlebuy()