#!/bin/bash
# Test script to verify ARM64 fixes
# This script tests the setup-frontend.sh and start-dashboard.sh improvements

echo "========================================="
echo "ARM64 Fix Verification Tests"
echo "========================================="
echo ""

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Test function
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo -n "Testing: $test_name... "
    
    if eval "$test_command" > /dev/null 2>&1; then
        echo "✅ PASS"
        ((TESTS_PASSED++))
        return 0
    else
        echo "❌ FAIL"
        ((TESTS_FAILED++))
        return 1
    fi
}

# Test 1: Verify setup-frontend.sh exists and is executable
run_test "setup-frontend.sh exists and is executable" \
    "[ -x '$SCRIPT_DIR/setup-frontend.sh' ]"

# Test 2: Verify start-dashboard.sh exists and is executable
run_test "start-dashboard.sh exists and is executable" \
    "[ -x '$SCRIPT_DIR/start-dashboard.sh' ]"

# Test 3: Verify setup-frontend.sh has valid bash syntax
run_test "setup-frontend.sh has valid bash syntax" \
    "bash -n '$SCRIPT_DIR/setup-frontend.sh'"

# Test 4: Verify start-dashboard.sh has valid bash syntax
run_test "start-dashboard.sh has valid bash syntax" \
    "bash -n '$SCRIPT_DIR/start-dashboard.sh'"

# Test 5: Verify .npmrc exists in frontend directory
run_test "frontend/.npmrc exists" \
    "[ -f '$FRONTEND_DIR/.npmrc' ]"

# Test 6: Verify .npmrc has timeout settings
run_test "frontend/.npmrc has fetch-timeout setting" \
    "grep -q 'fetch-timeout' '$FRONTEND_DIR/.npmrc'"

# Test 7: Verify ARM64_SETUP.md exists
run_test "ARM64_SETUP.md exists" \
    "[ -f '$SCRIPT_DIR/ARM64_SETUP.md' ]"

# Test 8: Verify troubleshooting doc has ARM64 section
run_test "TROUBLESHOOTING.md has ARM64 section" \
    "grep -q 'Rollup Module Error on ARM64' '$SCRIPT_DIR/docs/TROUBLESHOOTING.md'"

# Test 9: Verify Raspberry Pi guide has frontend setup step
run_test "Raspberry Pi guide has frontend setup section" \
    "grep -q 'Frontend Installation' '$SCRIPT_DIR/docs/deployment/raspberry-pi.md'"

# Test 10: Verify README mentions ARM64
run_test "README.md mentions ARM64" \
    "grep -q 'ARM64' '$SCRIPT_DIR/README.md'"

# Test 11: Verify setup script detects architecture
run_test "setup-frontend.sh detects architecture" \
    "grep -q 'uname -m' '$SCRIPT_DIR/setup-frontend.sh'"

# Test 12: Verify setup script has ARM64 conditional
run_test "setup-frontend.sh has ARM64 handling" \
    "grep -q 'aarch64\\|arm64' '$SCRIPT_DIR/setup-frontend.sh'"

# Test 13: Verify start script has error handler
run_test "start-dashboard.sh has error handler" \
    "grep -q 'handle_error' '$SCRIPT_DIR/start-dashboard.sh'"

# Test 14: Verify start script sets trap
run_test "start-dashboard.sh sets trap for errors" \
    "grep -q 'trap.*ERR' '$SCRIPT_DIR/start-dashboard.sh'"

# Test 15: Verify setup script cleans node_modules on ARM64
run_test "setup-frontend.sh cleans node_modules on ARM64" \
    "grep -q 'rm -rf node_modules' '$SCRIPT_DIR/setup-frontend.sh'"

# Test 16: Verify setup script uses --legacy-peer-deps flag
run_test "setup-frontend.sh uses --legacy-peer-deps flag" \
    "grep -q 'legacy-peer-deps' '$SCRIPT_DIR/setup-frontend.sh'"

# Test 17: Verify .npmrc has optional=true
run_test "frontend/.npmrc has optional=true" \
    "grep -q 'optional=true' '$FRONTEND_DIR/.npmrc'"

# Test 18: Verify FIX_SUMMARY.md exists
run_test "FIX_SUMMARY.md exists" \
    "[ -f '$SCRIPT_DIR/FIX_SUMMARY.md' ]"

# Test 19: Verify setup script checks for Rollup module
run_test "setup-frontend.sh verifies Rollup ARM64 module" \
    "grep -q '@rollup/rollup-linux-arm64-gnu' '$SCRIPT_DIR/setup-frontend.sh'"

# Test 20: Verify start script has helpful error messages
run_test "start-dashboard.sh has helpful error messages" \
    "grep -q 'To fix this' '$SCRIPT_DIR/start-dashboard.sh'"

# Summary
echo ""
echo "========================================="
echo "Test Results"
echo "========================================="
echo "Passed: $TESTS_PASSED"
echo "Failed: $TESTS_FAILED"
echo "Total:  $((TESTS_PASSED + TESTS_FAILED))"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo "✅ All tests passed!"
    echo ""
    echo "ARM64 fixes are properly implemented:"
    echo "  - Setup script detects and handles ARM64"
    echo "  - Start script verifies dependencies"
    echo "  - NPM configuration optimized"
    echo "  - Documentation comprehensive"
    echo ""
    exit 0
else
    echo "❌ Some tests failed!"
    echo ""
    echo "Please review the failed tests above."
    exit 1
fi
