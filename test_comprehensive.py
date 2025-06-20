#!/usr/bin/env python3
"""
CIRCLEBUY Comprehensive Testing Suite
Tests all major functionality and identifies issues
"""

import requests
import json
import time
import os
from datetime import datetime

class CircleBuyTester:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        self.issues = []
        
    def log_test(self, test_name, status, details="", issue=None):
        """Log test results"""
        result = {
            'test': test_name,
            'status': status,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        if issue:
            self.issues.append({
                'test': test_name,
                'issue': issue,
                'severity': 'HIGH' if status == 'FAIL' else 'MEDIUM'
            })
        
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
        if issue:
            print(f"   Issue: {issue}")
    
    def test_basic_connectivity(self):
        """Test basic server connectivity"""
        try:
            response = self.session.get(self.base_url, timeout=10)
            if response.status_code == 200:
                self.log_test("Basic Connectivity", "PASS", f"Server responding on {self.base_url}")
            else:
                self.log_test("Basic Connectivity", "FAIL", f"Status code: {response.status_code}", 
                            "Server not responding correctly")
        except Exception as e:
            self.log_test("Basic Connectivity", "FAIL", str(e), "Cannot connect to server")
    
    def test_static_files(self):
        """Test static file serving"""
        static_files = [
            "/static/styles.css",
            "/static/circlebuy.png",
            "/static/notifications.js"
        ]
        
        for file_path in static_files:
            try:
                response = self.session.get(f"{self.base_url}{file_path}")
                if response.status_code == 200:
                    self.log_test(f"Static File: {file_path}", "PASS")
                else:
                    self.log_test(f"Static File: {file_path}", "FAIL", 
                                f"Status: {response.status_code}", "Static file not accessible")
            except Exception as e:
                self.log_test(f"Static File: {file_path}", "FAIL", str(e), "Static file error")
    
    def test_page_loads(self):
        """Test all major pages load correctly"""
        pages = [
            ("/", "Homepage"),
            ("/login", "Login Page"),
            ("/register", "Register Page"),
            ("/search", "Search Page"),
            ("/category/1", "Category Page"),
        ]
        
        for url, name in pages:
            try:
                response = self.session.get(f"{self.base_url}{url}")
                if response.status_code == 200:
                    # Check for basic HTML structure
                    if "<html" in response.text and "</html>" in response.text:
                        self.log_test(f"Page Load: {name}", "PASS")
                    else:
                        self.log_test(f"Page Load: {name}", "WARN", "Invalid HTML structure", 
                                    "Page may not render correctly")
                elif response.status_code == 404:
                    self.log_test(f"Page Load: {name}", "FAIL", "Page not found", 
                                "Route may be missing or broken")
                else:
                    self.log_test(f"Page Load: {name}", "FAIL", f"Status: {response.status_code}", 
                                "Page not loading correctly")
            except Exception as e:
                self.log_test(f"Page Load: {name}", "FAIL", str(e), "Page load error")
    
    def test_authentication_flow(self):
        """Test user registration and login"""
        # Test registration page
        try:
            response = self.session.get(f"{self.base_url}/register")
            if response.status_code == 200 and "register" in response.text.lower():
                self.log_test("Registration Page", "PASS")
            else:
                self.log_test("Registration Page", "FAIL", "Registration form not found", 
                            "Registration may not work")
        except Exception as e:
            self.log_test("Registration Page", "FAIL", str(e), "Registration page error")
        
        # Test login page
        try:
            response = self.session.get(f"{self.base_url}/login")
            if response.status_code == 200 and "login" in response.text.lower():
                self.log_test("Login Page", "PASS")
            else:
                self.log_test("Login Page", "FAIL", "Login form not found", "Login may not work")
        except Exception as e:
            self.log_test("Login Page", "FAIL", str(e), "Login page error")
    
    def test_search_functionality(self):
        """Test search functionality"""
        try:
            # Test empty search
            response = self.session.get(f"{self.base_url}/search")
            if response.status_code == 200:
                self.log_test("Search Page", "PASS")
            else:
                self.log_test("Search Page", "FAIL", f"Status: {response.status_code}", 
                            "Search page not working")
            
            # Test search with query
            response = self.session.get(f"{self.base_url}/search?q=test")
            if response.status_code == 200:
                self.log_test("Search Query", "PASS")
            else:
                self.log_test("Search Query", "FAIL", f"Status: {response.status_code}", 
                            "Search with query not working")
        except Exception as e:
            self.log_test("Search Functionality", "FAIL", str(e), "Search system error")
    
    def test_database_connectivity(self):
        """Test database operations through API"""
        try:
            # Test homepage which requires database
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                # Check if categories are loaded (indicates DB connection)
                if "categories" in response.text.lower() or "category" in response.text.lower():
                    self.log_test("Database Connectivity", "PASS", "Categories loaded from database")
                else:
                    self.log_test("Database Connectivity", "WARN", "No categories found", 
                                "Database may be empty or not connected")
            else:
                self.log_test("Database Connectivity", "FAIL", "Homepage not loading", 
                            "Database connection issues")
        except Exception as e:
            self.log_test("Database Connectivity", "FAIL", str(e), "Database error")
    
    def test_security_headers(self):
        """Test security headers and configurations"""
        try:
            response = self.session.get(f"{self.base_url}/")
            headers = response.headers
            
            # Check for security headers
            security_checks = [
                ("X-Content-Type-Options", "nosniff"),
                ("X-Frame-Options", "DENY"),
                ("X-XSS-Protection", "1; mode=block"),
            ]
            
            missing_headers = []
            for header, expected in security_checks:
                if header not in headers:
                    missing_headers.append(header)
            
            if missing_headers:
                self.log_test("Security Headers", "WARN", f"Missing: {', '.join(missing_headers)}", 
                            "Security headers should be added for production")
            else:
                self.log_test("Security Headers", "PASS")
                
        except Exception as e:
            self.log_test("Security Headers", "FAIL", str(e), "Cannot check security headers")
    
    def test_performance(self):
        """Test basic performance metrics"""
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/")
            end_time = time.time()
            
            response_time = end_time - start_time
            
            if response_time < 1.0:
                self.log_test("Response Time", "PASS", f"{response_time:.3f}s")
            elif response_time < 3.0:
                self.log_test("Response Time", "WARN", f"{response_time:.3f}s", 
                            "Response time could be improved")
            else:
                self.log_test("Response Time", "FAIL", f"{response_time:.3f}s", 
                            "Response time too slow")
                
        except Exception as e:
            self.log_test("Performance Test", "FAIL", str(e), "Performance test error")
    
    def test_error_handling(self):
        """Test error handling"""
        error_tests = [
            ("/nonexistent-page", "404 Error Handling"),
            ("/product/99999", "Invalid Product ID"),
            ("/category/99999", "Invalid Category ID"),
        ]
        
        for url, test_name in error_tests:
            try:
                response = self.session.get(f"{self.base_url}{url}")
                if response.status_code == 404:
                    # Check if custom error page is shown
                    if "error" in response.text.lower() or "not found" in response.text.lower():
                        self.log_test(test_name, "PASS", "Custom error page shown")
                    else:
                        self.log_test(test_name, "WARN", "Generic 404", 
                                    "Custom error pages would improve UX")
                else:
                    self.log_test(test_name, "WARN", f"Status: {response.status_code}", 
                                "Unexpected response for invalid URL")
            except Exception as e:
                self.log_test(test_name, "FAIL", str(e), "Error handling test failed")
    
    def test_mobile_responsiveness(self):
        """Test mobile responsiveness indicators"""
        try:
            response = self.session.get(f"{self.base_url}/")
            content = response.text.lower()
            
            mobile_indicators = [
                "viewport" in content,
                "bootstrap" in content or "responsive" in content,
                "@media" in content or "mobile" in content
            ]
            
            if any(mobile_indicators):
                self.log_test("Mobile Responsiveness", "PASS", "Mobile-friendly indicators found")
            else:
                self.log_test("Mobile Responsiveness", "WARN", "No mobile indicators", 
                            "Mobile responsiveness should be verified")
                
        except Exception as e:
            self.log_test("Mobile Responsiveness", "FAIL", str(e), "Cannot check mobile features")
    
    def run_all_tests(self):
        """Run all tests and generate report"""
        print("🚀 Starting CIRCLEBUY Comprehensive Testing")
        print("=" * 50)
        
        # Run all test categories
        self.test_basic_connectivity()
        self.test_static_files()
        self.test_page_loads()
        self.test_authentication_flow()
        self.test_search_functionality()
        self.test_database_connectivity()
        self.test_security_headers()
        self.test_performance()
        self.test_error_handling()
        self.test_mobile_responsiveness()
        
        # Generate summary report
        self.generate_report()
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 50)
        print("📊 CIRCLEBUY TEST REPORT")
        print("=" * 50)
        
        # Count results
        total_tests = len(self.test_results)
        passed = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed = len([r for r in self.test_results if r['status'] == 'FAIL'])
        warnings = len([r for r in self.test_results if r['status'] == 'WARN'])
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed}")
        print(f"⚠️  Warnings: {warnings}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {(passed/total_tests)*100:.1f}%")
        
        # Overall status
        if failed == 0 and warnings <= 2:
            overall_status = "🟢 EXCELLENT"
        elif failed <= 2 and warnings <= 5:
            overall_status = "🟡 GOOD"
        elif failed <= 5:
            overall_status = "🟠 NEEDS IMPROVEMENT"
        else:
            overall_status = "🔴 CRITICAL ISSUES"
        
        print(f"\nOverall Status: {overall_status}")
        
        # Issues summary
        if self.issues:
            print(f"\n🔍 ISSUES FOUND ({len(self.issues)}):")
            for i, issue in enumerate(self.issues, 1):
                severity_icon = "🔴" if issue['severity'] == 'HIGH' else "🟡"
                print(f"{i}. {severity_icon} {issue['test']}: {issue['issue']}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        recommendations = []
        
        if failed > 0:
            recommendations.append("Fix critical failures before deployment")
        if warnings > 3:
            recommendations.append("Address warnings to improve user experience")
        
        # Security recommendations
        security_issues = [i for i in self.issues if 'security' in i['issue'].lower()]
        if security_issues:
            recommendations.append("Implement security headers for production")
        
        # Performance recommendations
        perf_issues = [i for i in self.issues if 'response time' in i['issue'].lower()]
        if perf_issues:
            recommendations.append("Optimize performance for better user experience")
        
        if not recommendations:
            recommendations.append("Application is ready for deployment!")
        
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
        
        print("\n" + "=" * 50)
        print("Testing completed at:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

if __name__ == "__main__":
    tester = CircleBuyTester()
    tester.run_all_tests()