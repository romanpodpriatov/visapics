#!/bin/bash

# Health Check Script for VisaPics
set -e

echo "🏥 Performing health checks..."

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Function to print test results
test_result() {
    local test_name=$1
    local result=$2
    local details=$3
    
    if [ "$result" = "PASS" ]; then
        echo -e "  ✅ ${GREEN}$test_name${NC}: $details"
    elif [ "$result" = "WARN" ]; then
        echo -e "  ⚠️  ${YELLOW}$test_name${NC}: $details"
    else
        echo -e "  ❌ ${RED}$test_name${NC}: $details"
    fi
}

# Test counters
tests_passed=0
tests_failed=0
tests_warned=0

# Test function
run_test() {
    local test_name=$1
    local test_command=$2
    local expected_result=$3
    
    if eval "$test_command" > /dev/null 2>&1; then
        if [ "$expected_result" = "success" ]; then
            test_result "$test_name" "PASS" "OK"
            ((tests_passed++))
        else
            test_result "$test_name" "FAIL" "Unexpected success"
            ((tests_failed++))
        fi
    else
        if [ "$expected_result" = "success" ]; then
            test_result "$test_name" "FAIL" "Failed"
            ((tests_failed++))
        else
            test_result "$test_name" "PASS" "Expected failure"
            ((tests_passed++))
        fi
    fi
}

echo "🔍 System Health Checks:"

# 1. Docker Services
echo ""
echo "🐳 Docker Services:"
if docker-compose ps | grep -q "Up"; then
    test_result "Docker Compose" "PASS" "Services are running"
    ((tests_passed++))
else
    test_result "Docker Compose" "FAIL" "Services not running"
    ((tests_failed++))
fi

# Check individual services
for service in visapics nginx; do
    if docker-compose ps $service | grep -q "Up"; then
        test_result "$service service" "PASS" "Running"
        ((tests_passed++))
    else
        test_result "$service service" "FAIL" "Not running"
        ((tests_failed++))
    fi
done

# 2. Network Connectivity
echo ""
echo "🌐 Network Connectivity:"

# Local health endpoint
if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
    test_result "Local App Health" "PASS" "Responding on port 8000"
    ((tests_passed++))
else
    test_result "Local App Health" "FAIL" "Not responding on port 8000"
    ((tests_failed++))
fi

# SSL endpoint
if curl -f -s -k https://localhost/health > /dev/null 2>&1; then
    test_result "HTTPS Health" "PASS" "SSL endpoint responding"
    ((tests_passed++))
else
    test_result "HTTPS Health" "FAIL" "SSL endpoint not responding"
    ((tests_failed++))
fi

# External domain check
if curl -f -s https://visapics.org/health > /dev/null 2>&1; then
    test_result "External Domain" "PASS" "visapics.org accessible"
    ((tests_passed++))
else
    test_result "External Domain" "WARN" "visapics.org not accessible (DNS/Cloudflare issue?)"
    ((tests_warned++))
fi

# 3. File System
echo ""
echo "📁 File System:"

# Required directories
for dir in uploads processed previews gfpgan/weights models ssl; do
    if [ -d "$dir" ]; then
        test_result "$dir directory" "PASS" "Exists"
        ((tests_passed++))
    else
        test_result "$dir directory" "FAIL" "Missing"
        ((tests_failed++))
    fi
done

# SSL certificates
if [ -f "ssl/cert.pem" ] && [ -f "ssl/key.pem" ]; then
    # Check certificate validity
    if openssl x509 -in ssl/cert.pem -checkend 86400 > /dev/null 2>&1; then
        test_result "SSL Certificates" "PASS" "Valid and not expiring in 24h"
        ((tests_passed++))
    else
        test_result "SSL Certificates" "WARN" "Expiring within 24 hours"
        ((tests_warned++))
    fi
else
    test_result "SSL Certificates" "FAIL" "Missing"
    ((tests_failed++))
fi

# Environment file
if [ -f ".env" ]; then
    if grep -q "your.*here" .env; then
        test_result "Environment Config" "WARN" "Contains placeholder values"
        ((tests_warned++))
    else
        test_result "Environment Config" "PASS" "Configured"
        ((tests_passed++))
    fi
else
    test_result "Environment Config" "FAIL" "Missing .env file"
    ((tests_failed++))
fi

# 4. AI Models
echo ""
echo "🤖 AI Models:"

models=(
    "gfpgan/weights/GFPGANv1.4.pth:300"
    "gfpgan/weights/detection_Resnet50_Final.pth:100"
    "gfpgan/weights/parsing_parsenet.pth:80"
    "models/BiRefNet-portrait-epoch_150.onnx:50"
)

for model_info in "${models[@]}"; do
    model_path=$(echo $model_info | cut -d':' -f1)
    min_size_mb=$(echo $model_info | cut -d':' -f2)
    model_name=$(basename $model_path)
    
    if [ -f "$model_path" ]; then
        size_mb=$(du -m "$model_path" | cut -f1)
        if [ "$size_mb" -ge "$min_size_mb" ]; then
            test_result "$model_name" "PASS" "${size_mb}MB"
            ((tests_passed++))
        else
            test_result "$model_name" "WARN" "Too small (${size_mb}MB < ${min_size_mb}MB)"
            ((tests_warned++))
        fi
    else
        test_result "$model_name" "FAIL" "Missing"
        ((tests_failed++))
    fi
done

# 5. Application Endpoints
echo ""
echo "🔗 Application Endpoints:"

endpoints=(
    "/"
    "/health"
    "/api/pricing"
)

for endpoint in "${endpoints[@]}"; do
    if curl -f -s "http://localhost:8000$endpoint" > /dev/null 2>&1; then
        test_result "Endpoint $endpoint" "PASS" "Responding"
        ((tests_passed++))
    else
        test_result "Endpoint $endpoint" "FAIL" "Not responding"
        ((tests_failed++))
    fi
done

# 6. Resource Usage
echo ""
echo "💾 Resource Usage:"

# Disk space
disk_usage=$(df -h . | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$disk_usage" -lt 80 ]; then
    test_result "Disk Space" "PASS" "${disk_usage}% used"
    ((tests_passed++))
elif [ "$disk_usage" -lt 90 ]; then
    test_result "Disk Space" "WARN" "${disk_usage}% used"
    ((tests_warned++))
else
    test_result "Disk Space" "FAIL" "${disk_usage}% used (critical)"
    ((tests_failed++))
fi

# Memory usage (if available)
if command -v free > /dev/null 2>&1; then
    mem_usage=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
    if [ "$mem_usage" -lt 80 ]; then
        test_result "Memory Usage" "PASS" "${mem_usage}% used"
        ((tests_passed++))
    elif [ "$mem_usage" -lt 90 ]; then
        test_result "Memory Usage" "WARN" "${mem_usage}% used"
        ((tests_warned++))
    else
        test_result "Memory Usage" "FAIL" "${mem_usage}% used (critical)"
        ((tests_failed++))
    fi
fi

# Summary
echo ""
echo "📊 Health Check Summary:"
echo "  ✅ Passed: $tests_passed"
echo "  ⚠️  Warnings: $tests_warned"
echo "  ❌ Failed: $tests_failed"

total_tests=$((tests_passed + tests_warned + tests_failed))
echo "  📈 Success Rate: $(( (tests_passed * 100) / total_tests ))%"

# Exit with appropriate code
if [ $tests_failed -eq 0 ]; then
    if [ $tests_warned -eq 0 ]; then
        echo "🎉 All health checks passed!"
        exit 0
    else
        echo "⚠️  Health checks passed with warnings"
        exit 0
    fi
else
    echo "❌ Health checks failed"
    exit 1
fi