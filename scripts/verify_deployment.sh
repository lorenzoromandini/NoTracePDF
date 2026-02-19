#!/bin/bash
#
# NoTracePDF Deployment Verification Script
#
# This script verifies that the deployment meets all privacy requirements:
# - Container is running
# - tmpfs mounts are configured (RAM-backed, ephemeral)
# - No persistent volumes
# - Memory limits are set
# - Health endpoint is accessible
# - Cache headers are correct
# - Zero-trace architecture is enforced
#
# Reference: DEPLOY-01 to DEPLOY-04, ARCH-01 to ARCH-08
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Container name (can be overridden)
CONTAINER_NAME="${CONTAINER_NAME:-notracepdf}"
HEALTH_URL="${HEALTH_URL:-http://localhost:8000}"

echo "========================================"
echo "NoTracePDF Deployment Verification"
echo "========================================"
echo ""
echo "Container: $CONTAINER_NAME"
echo "Health URL: $HEALTH_URL"
echo ""

# Track overall status
PASSED=0
FAILED=0
SKIPPED=0

pass() {
    echo -e "${GREEN}✓ PASS${NC}: $1"
    ((PASSED++))
}

fail() {
    echo -e "${RED}✗ FAIL${NC}: $1"
    ((FAILED++))
}

skip() {
    echo -e "${YELLOW}⊘ SKIP${NC}: $1"
    ((SKIPPED++))
}

# ===========================================
# 1. Check container status
# ===========================================
echo "1. Checking container status..."

if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    pass "Container '$CONTAINER_NAME' is running"
else
    fail "Container '$CONTAINER_NAME' is NOT running"
    echo "   Start with: docker-compose up -d"
fi

# ===========================================
# 2. Verify tmpfs mounts
# ===========================================
echo ""
echo "2. Verifying tmpfs mounts..."

if docker exec "$CONTAINER_NAME" mount 2>/dev/null | grep -q "tmpfs on /tmp"; then
    pass "/tmp is mounted as tmpfs (RAM-backed)"
else
    fail "/tmp is NOT mounted as tmpfs"
    echo "   Add to docker-compose.yml: tmpfs: - /tmp"
fi

if docker exec "$CONTAINER_NAME" mount 2>/dev/null | grep -q "tmpfs on /app/uploads"; then
    pass "/app/uploads is mounted as tmpfs (RAM-backed)"
else
    # This may not be mounted if not in use, skip rather than fail
    skip "/app/uploads tmpfs mount (may not be mounted if unused)"
fi

# ===========================================
# 3. Verify no persistent volumes
# ===========================================
echo ""
echo "3. Verifying no persistent volumes..."

VOLUMES=$(docker inspect "$CONTAINER_NAME" --format '{{range .Mounts}}{{.Type}}:{{.Destination}} {{end}}' 2>/dev/null || echo "")

PERSISTENT_FOUND=false
for mount in $VOLUMES; do
    mount_type=$(echo "$mount" | cut -d: -f1)
    mount_dest=$(echo "$mount" | cut -d: -f2)
    
    if [ "$mount_type" != "tmpfs" ] && [ "$mount_type" != "none" ]; then
        echo -e "${RED}   Found persistent mount: $mount_type -> $mount_dest${NC}"
        PERSISTENT_FOUND=true
    fi
done

if [ "$PERSISTENT_FOUND" = false ]; then
    pass "No persistent volume mounts found"
else
    fail "Found persistent volume mounts"
    echo "   Remove volumes from docker-compose.yml"
fi

# ===========================================
# 4. Verify memory limits
# ===========================================
echo ""
echo "4. Verifying memory limits..."

MEMORY_LIMIT=$(docker inspect "$CONTAINER_NAME" --format '{{.HostConfig.Memory}}' 2>/dev/null || echo "0")

if [ "$MEMORY_LIMIT" -gt 0 ]; then
    MEMORY_MB=$((MEMORY_LIMIT / 1024 / 1024))
    pass "Memory limit set: ${MEMORY_MB}MB"
else
    fail "No memory limit set"
    echo "   Add to docker-compose.yml: deploy.resources.limits.memory"
fi

# ===========================================
# 5. Test health endpoint
# ===========================================
echo ""
echo "5. Testing health endpoint..."

HEALTH_RESPONSE=$(curl -sf "$HEALTH_URL/health" 2>/dev/null || echo "")

if [ -n "$HEALTH_RESPONSE" ]; then
    pass "Health endpoint responding"
    
    # Check response contains expected content
    if echo "$HEALTH_RESPONSE" | grep -q '"status".*"ok"'; then
        pass "Health check returns 'ok' status"
    else
        fail "Health check response unexpected: $HEALTH_RESPONSE"
    fi
else
    fail "Health endpoint not responding"
    echo "   Check if container is running and port is exposed"
fi

# ===========================================
# 6. Verify cache headers
# ===========================================
echo ""
echo "6. Verifying cache headers..."

HEADERS=$(curl -sI "$HEALTH_URL/health" 2>/dev/null || echo "")

if echo "$HEADERS" | grep -qi "cache-control:.*no-store"; then
    pass "Cache-Control: no-store header present"
else
    fail "Missing Cache-Control: no-store header"
    echo "   Add CacheHeadersMiddleware to application"
fi

if echo "$HEADERS" | grep -qi "cache-control:.*no-cache"; then
    pass "Cache-Control: no-cache header present"
else
    fail "Missing Cache-Control: no-cache header"
fi

if echo "$HEADERS" | grep -qi "pragma:.*no-cache"; then
    pass "Pragma: no-cache header present"
else
    skip "Pragma: no-cache header (optional but recommended)"
fi

if echo "$HEADERS" | grep -qi "expires:.*0"; then
    pass "Expires: 0 header present"
else
    skip "Expires: 0 header (optional but recommended)"
fi

# ===========================================
# 7. Test file cleanup (optional)
# ===========================================
echo ""
echo "7. Testing file cleanup..."

# Check if /tmp is empty (no lingering files)
TMP_FILES=$(docker exec "$CONTAINER_NAME" sh -c 'ls -A /tmp 2>/dev/null | wc -l' 2>/dev/null || echo "unknown")

if [ "$TMP_FILES" = "0" ]; then
    pass "/tmp directory is empty (no lingering files)"
elif [ "$TMP_FILES" = "unknown" ]; then
    skip "Could not check /tmp contents"
else
    skip "/tmp contains $TMP_FILES items (may include system files)"
fi

# ===========================================
# 8. Check Dockerfile configuration
# ===========================================
echo ""
echo "8. Checking Dockerfile configuration..."

DOCKERFILE_PATH="./Dockerfile"
if [ -f "$DOCKERFILE_PATH" ]; then
    if grep -qi "^VOLUME" "$DOCKERFILE_PATH"; then
        fail "Dockerfile contains VOLUME instruction"
        echo "   Remove VOLUME instruction from Dockerfile"
    else
        pass "Dockerfile has no VOLUME instruction"
    fi
    
    if grep -q "gunicorn.*--timeout" "$DOCKERFILE_PATH"; then
        pass "Gunicorn timeout configured"
    else
        skip "Gunicorn timeout not explicitly configured"
    fi
else
    skip "Dockerfile not found at $DOCKERFILE_PATH"
fi

# ===========================================
# 9. Check docker-compose configuration
# ===========================================
echo ""
echo "9. Checking docker-compose.yml configuration..."

COMPOSE_PATH="./docker-compose.yml"
if [ -f "$COMPOSE_PATH" ]; then
    if grep -q "tmpfs:" "$COMPOSE_PATH"; then
        pass "docker-compose.yml has tmpfs configuration"
    else
        fail "docker-compose.yml missing tmpfs configuration"
    fi
    
    if grep -q "memory:" "$COMPOSE_PATH"; then
        pass "docker-compose.yml has memory limit"
    else
        fail "docker-compose.yml missing memory limit"
    fi
    
    if grep -q "^.*volumes:" "$COMPOSE_PATH" && ! grep -A 10 "services:" "$COMPOSE_PATH" | grep -q "volumes:"; then
        # Check if there are service-level volumes (not top-level volume definitions)
        if grep -A 30 "notracepdf:" "$COMPOSE_PATH" | grep -q "volumes:"; then
            fail "docker-compose.yml has persistent volumes for service"
        else
            pass "docker-compose.yml has no persistent volumes for service"
        fi
    else
        pass "docker-compose.yml has no persistent volumes"
    fi
else
    skip "docker-compose.yml not found at $COMPOSE_PATH"
fi

# ===========================================
# Summary
# ===========================================
echo ""
echo "========================================"
echo "Verification Summary"
echo "========================================"
echo -e "${GREEN}Passed:  $PASSED${NC}"
echo -e "${RED}Failed:  $FAILED${NC}"
echo -e "${YELLOW}Skipped: $SKIPPED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All critical checks passed!${NC}"
    echo ""
    echo "The deployment meets NoTracePDF privacy requirements:"
    echo "  - No persistent storage (tmpfs for all temp files)"
    echo "  - Memory limits prevent resource exhaustion"
    echo "  - Cache headers prevent browser caching"
    echo "  - Container is healthy and responding"
    exit 0
else
    echo -e "${RED}✗ Some checks failed. Review the output above.${NC}"
    echo ""
    echo "Common fixes:"
    echo "  - Start container: docker-compose up -d"
    echo "  - Add tmpfs: Add 'tmpfs: - /tmp' to docker-compose.yml"
    echo "  - Set memory limit: Add 'deploy.resources.limits.memory: 1G'"
    echo "  - Remove volumes: Delete any 'volumes:' from service definition"
    exit 1
fi
