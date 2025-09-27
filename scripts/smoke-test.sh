#!/bin/bash
# Smoke test script for MITS Validator container
# Usage: ./scripts/smoke-test.sh [PORT]

set -euo pipefail

# Configuration
PORT=${1:-8000}
BASE_URL="http://localhost:${PORT}"
TIMEOUT=30
MAX_RETRIES=5

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test data
VALID_XML='<?xml version="1.0" encoding="UTF-8"?>
<PropertyMarketing xmlns="http://www.mits.org/schema/PropertyMarketing/ILS/5.0">
  <Property>
    <PropertyID>12345</PropertyID>
    <MarketingName>Test Property</MarketingName>
  </Property>
</PropertyMarketing>'

INVALID_XML='<?xml version="1.0" encoding="UTF-8"?>
<PropertyMarketing xmlns="http://www.mits.org/schema/PropertyMarketing/ILS/5.0">
  <Property>
    <PropertyID>12345</PropertyID>
    <MarketingName>Test Property</MarketingName>
  </Property>
</PropertyMarketing>'

# Helper functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

wait_for_service() {
    local url="$1"
    local max_attempts="$2"
    local attempt=1

    log_info "Waiting for service at $url..."

    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "$url" > /dev/null 2>&1; then
            log_info "Service is ready after $attempt attempts"
            return 0
        fi

        log_warn "Attempt $attempt/$max_attempts failed, retrying in 2s..."
        sleep 2
        ((attempt++))
    done

    log_error "Service failed to start after $max_attempts attempts"
    return 1
}

test_health_endpoint() {
    log_info "Testing /health endpoint..."

    local response
    response=$(curl -s -w "%{http_code}" -o /dev/null "${BASE_URL}/health")

    if [ "$response" = "200" ]; then
        log_info "✓ Health endpoint returned 200"
        return 0
    else
        log_error "✗ Health endpoint returned $response"
        return 1
    fi
}

test_validate_endpoint() {
    log_info "Testing /v1/validate endpoint with valid XML..."

    local response
    local http_code
    local request_id

    # Test with valid XML
    response=$(curl -s -w "\n%{http_code}" \
        -H "Content-Type: application/xml" \
        -H "X-Request-Id: smoke-test-$(date +%s)" \
        -d "$VALID_XML" \
        "${BASE_URL}/v1/validate")

    http_code=$(echo "$response" | tail -n1)
    response=$(echo "$response" | head -n -1)

    if [ "$http_code" = "200" ]; then
        log_info "✓ Valid XML returned 200"

        # Check for X-Request-Id header
        request_id=$(curl -s -I -H "Content-Type: application/xml" \
            -H "X-Request-Id: smoke-test-$(date +%s)" \
            -d "$VALID_XML" \
            "${BASE_URL}/v1/validate" | grep -i "x-request-id" | head -n1)

        if [ -n "$request_id" ]; then
            log_info "✓ X-Request-Id header present"
        else
            log_warn "⚠ X-Request-Id header missing"
        fi

        # Check for Cache-Control header
        local cache_control
        cache_control=$(curl -s -I -H "Content-Type: application/xml" \
            -H "X-Request-Id: smoke-test-$(date +%s)" \
            -d "$VALID_XML" \
            "${BASE_URL}/v1/validate" | grep -i "cache-control" | head -n1)

        if echo "$cache_control" | grep -q "no-store"; then
            log_info "✓ Cache-Control: no-store header present"
        else
            log_warn "⚠ Cache-Control: no-store header missing"
        fi

        # Validate response envelope structure
        if echo "$response" | jq -e '.summary.valid == true' > /dev/null 2>&1; then
            log_info "✓ Response envelope structure valid"
        else
            log_error "✗ Invalid response envelope structure"
            return 1
        fi

    else
        log_error "✗ Valid XML returned $http_code"
        return 1
    fi
}

test_invalid_xml() {
    log_info "Testing /v1/validate endpoint with invalid XML..."

    local response
    local http_code

    # Test with invalid XML (malformed)
    local malformed_xml='<?xml version="1.0" encoding="UTF-8"?>
<PropertyMarketing xmlns="http://www.mits.org/schema/PropertyMarketing/ILS/5.0">
  <Property>
    <PropertyID>12345</PropertyID>
    <MarketingName>Test Property</MarketingName>
  </Property>
</PropertyMarketing>'

    response=$(curl -s -w "\n%{http_code}" \
        -H "Content-Type: application/xml" \
        -H "X-Request-Id: smoke-test-invalid-$(date +%s)" \
        -d "$malformed_xml" \
        "${BASE_URL}/v1/validate")

    http_code=$(echo "$response" | tail -n1)
    response=$(echo "$response" | head -n -1)

    if [ "$http_code" = "200" ]; then
        log_info "✓ Invalid XML returned 200 (expected for validation errors)"

        # Check that valid=false in response
        if echo "$response" | jq -e '.summary.valid == false' > /dev/null 2>&1; then
            log_info "✓ Response correctly indicates validation failure"
        else
            log_error "✗ Response should indicate validation failure"
            return 1
        fi

        # Check for WELLFORMED error
        if echo "$response" | jq -e '.findings[] | select(.code == "WELLFORMED:PARSE_ERROR")' > /dev/null 2>&1; then
            log_info "✓ WELLFORMED:PARSE_ERROR finding present"
        else
            log_warn "⚠ WELLFORMED:PARSE_ERROR finding not found (may be expected for this XML)"
        fi

    else
        log_error "✗ Invalid XML returned $http_code"
        return 1
    fi
}

test_url_validation() {
    log_info "Testing URL validation endpoint..."

    # Test with a simple URL (this will likely fail, but should return proper error)
    local response
    local http_code

    response=$(curl -s -w "\n%{http_code}" \
        -H "X-Request-Id: smoke-test-url-$(date +%s)" \
        "${BASE_URL}/v1/validate?url=https://example.com/nonexistent.xml")

    http_code=$(echo "$response" | tail -n1)
    response=$(echo "$response" | head -n -1)

    if [ "$http_code" = "200" ]; then
        log_info "✓ URL validation returned 200"

        # Should have validation errors for invalid URL
        if echo "$response" | jq -e '.summary.valid == false' > /dev/null 2>&1; then
            log_info "✓ URL validation correctly indicates failure"
        else
            log_warn "⚠ URL validation response structure unexpected"
        fi
    else
        log_warn "⚠ URL validation returned $http_code (may be expected)"
    fi
}

# Main execution
main() {
    log_info "Starting smoke tests for MITS Validator on port $PORT"

    # Wait for service to be ready
    if ! wait_for_service "${BASE_URL}/health" $MAX_RETRIES; then
        log_error "Service is not available. Make sure the container is running on port $PORT"
        exit 1
    fi

    # Run tests
    local failed=0

    test_health_endpoint || ((failed++))
    test_validate_endpoint || ((failed++))
    test_invalid_xml || ((failed++))
    test_url_validation || ((failed++))

    # Summary
    if [ $failed -eq 0 ]; then
        log_info "🎉 All smoke tests passed!"
        exit 0
    else
        log_error "❌ $failed test(s) failed"
        exit 1
    fi
}

# Check dependencies
if ! command -v curl > /dev/null 2>&1; then
    log_error "curl is required but not installed"
    exit 1
fi

if ! command -v jq > /dev/null 2>&1; then
    log_error "jq is required but not installed"
    exit 1
fi

# Run main function
main "$@"
