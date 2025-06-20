import os
import sys
import subprocess
import time

def run_command(command, description):
    """Run a command and print its output"""
    print(f"\n{'=' * 50}")
    print(f"Running {description}...")
    print(f"{'=' * 50}")
    
    start_time = time.time()
    result = subprocess.run(command, shell=True, text=True)
    end_time = time.time()
    
    print(f"\nCompleted in {end_time - start_time:.2f} seconds")
    return result.returncode == 0

def main():
    print("=" * 50)
    print("CIRCLEBUY Test Suite")
    print("=" * 50)
    
    # Make sure we're in the project directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Install test dependencies
    print("\nInstalling test dependencies...")
    subprocess.run("pip install pytest pytest-asyncio aiohttp", shell=True)
    
    # Run security checks
    security_check_success = run_command("python security_check.py", "security checks")
    
    # Run unit tests
    unit_tests_success = run_command("pytest tests/test_security.py -v", "security tests")
    
    # Run performance tests
    performance_tests_success = run_command("pytest tests/test_performance.py -v", "performance tests")
    
    # Start the application in the background for load testing
    print("\nStarting application for load testing...")
    app_process = subprocess.Popen(
        "python app.py", 
        shell=True, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE
    )
    
    # Wait for the app to start
    print("Waiting for application to start...")
    time.sleep(5)
    
    # Run load tests
    load_tests_success = run_command("python tests/test_load.py", "load tests")
    
    # Kill the application
    app_process.terminate()
    
    # Print summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    print(f"Security Checks: {'✅ Passed' if security_check_success else '❌ Failed'}")
    print(f"Security Tests: {'✅ Passed' if unit_tests_success else '❌ Failed'}")
    print(f"Performance Tests: {'✅ Passed' if performance_tests_success else '❌ Failed'}")
    print(f"Load Tests: {'✅ Passed' if load_tests_success else '❌ Failed'}")
    
    overall_success = all([
        security_check_success,
        unit_tests_success,
        performance_tests_success,
        load_tests_success
    ])
    
    print("\n" + "=" * 50)
    if overall_success:
        print("✅ All tests passed! The application is ready for deployment.")
    else:
        print("❌ Some tests failed. Please review the issues before deployment.")
    print("=" * 50)

if __name__ == "__main__":
    main()