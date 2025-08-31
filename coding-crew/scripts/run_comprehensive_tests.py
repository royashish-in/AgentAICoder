#!/usr/bin/env python3
"""Run comprehensive tests for web interface and approval workflow."""

import subprocess
import sys
import os
import time
import requests
from pathlib import Path

def run_unit_tests():
    """Run unit tests."""
    print("🧪 Running unit tests...")
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/test_web_interface.py",
        "tests/test_approval_client.py",
        "-v"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    return result.returncode == 0

def run_integration_tests():
    """Run integration tests."""
    print("🔗 Running integration tests...")
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/integration/test_approval_workflow.py",
        "-v"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    return result.returncode == 0

def test_web_interface_live():
    """Test live web interface if running."""
    print("🌐 Testing live web interface...")
    
    try:
        response = requests.get("http://localhost:8000/api/analyses", timeout=5)
        if response.status_code == 200:
            print("✅ Web interface is running and responsive")
            
            # Test submission
            test_data = {
                "id": "live-test-001",
                "title": "Live Test Analysis",
                "content": "Test content for live testing",
                "diagrams": [],
                "timestamp": "2024-01-01T00:00:00",
                "status": "pending"
            }
            
            submit_response = requests.post("http://localhost:8000/api/analyses", json=test_data)
            if submit_response.status_code == 200:
                print("✅ Analysis submission working")
                return True
            else:
                print(f"❌ Analysis submission failed: {submit_response.status_code}")
                return False
        else:
            print(f"❌ Web interface returned status: {response.status_code}")
            return False
            
    except requests.ConnectionError:
        print("⚠️  Web interface not running (this is optional)")
        print("   Start with: python scripts/start_web_interface.py")
        return True  # Not a failure, just not running
    except Exception as e:
        print(f"❌ Web interface test failed: {e}")
        return False

def run_coverage_report():
    """Generate coverage report."""
    print("📊 Generating coverage report...")
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "--cov=core",
        "--cov=web",
        "--cov-report=term-missing",
        "--cov-report=html",
        "tests/",
        "-q"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    return result.returncode == 0

def main():
    """Run all comprehensive tests."""
    print("🚀 Starting Comprehensive Test Suite")
    print("=" * 50)
    
    results = []
    
    # Run unit tests
    results.append(("Unit Tests", run_unit_tests()))
    
    # Run integration tests  
    results.append(("Integration Tests", run_integration_tests()))
    
    # Test live web interface
    results.append(("Live Web Interface", test_web_interface_live()))
    
    # Generate coverage report
    results.append(("Coverage Report", run_coverage_report()))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} test suites passed")
    
    if passed == len(results):
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())