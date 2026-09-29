"""
Master Test Runner
Runs all 6 tests in sequence
"""

import sys
import os
import subprocess

def run_test(test_file):
    """Run a single test file and return success status"""
    print(f"\n{'='*70}")
    print(f"Running: {test_file}")
    print(f"{'='*70}\n")
    
    result = subprocess.run(
        [sys.executable, test_file],
        cwd=os.path.dirname(__file__),
        capture_output=False
    )
    
    return result.returncode == 0

def main():
    """Run all tests in sequence"""
    test_dir = os.path.dirname(__file__)
    
    # List of test files in order
    tests = [
        'test_1_full_encryption.py',
        'test_2_decryption.py',
        'test_3_capacity_limit.py',
        'test_4_wrong_stego_key.py',
        'test_5_image_analysis.py',
        'test_6_jpeg_compression.py'
    ]
    
    results = {}
    
    print("\n" + "="*70)
    print("STEGOCIPHER - MASTER TEST RUNNER")
    print("="*70)
    print(f"\nRunning {len(tests)} tests in sequence...")
    print(f"Test directory: {test_dir}\n")
    
    for test in tests:
        test_path = os.path.join(test_dir, test)
        if not os.path.exists(test_path):
            print(f"\n[!] ERROR: Test file not found: {test_path}")
            results[test] = False
            continue
        
        success = run_test(test_path)
        results[test] = success
        
        if success:
            print(f"\n[✓] {test} PASSED")
        else:
            print(f"\n[✗] {test} FAILED")
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test, success in results.items():
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"{status:12} - {test}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
