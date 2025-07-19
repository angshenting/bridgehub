#!/bin/bash

# Bridge Platform Integration Testing Script
set -e

echo "🧪 Bridge Platform Integration Testing"
echo "====================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test results
TESTS_PASSED=0
TESTS_FAILED=0

run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo -e "\n🔍 Testing: $test_name"
    if eval "$test_command"; then
        echo -e "${GREEN}✅ PASSED${NC}: $test_name"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ FAILED${NC}: $test_name"
        ((TESTS_FAILED++))
    fi
}

# Check prerequisites
echo "🔧 Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is required but not installed${NC}"
    exit 1
fi

if ! command -v pnpm &> /dev/null; then
    echo -e "${RED}❌ pnpm is required but not installed${NC}"
    exit 1
fi

if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"

# Start services
echo -e "\n🚀 Starting services..."
docker-compose -f docker-compose.dev.yml up -d

# Wait for database
echo "⏳ Waiting for database..."
timeout=60
counter=0
until docker-compose -f docker-compose.dev.yml exec -T postgres pg_isready -U bridge_user -d bridge_platform_dev; do
    if [ $counter -eq $timeout ]; then
        echo -e "${RED}❌ Database failed to start${NC}"
        exit 1
    fi
    sleep 1
    ((counter++))
done

echo -e "${GREEN}✅ Database is ready${NC}"

# Test database connection
run_test "Database Connection" "
    docker-compose -f docker-compose.dev.yml exec -T postgres psql -U bridge_user -d bridge_platform_dev -c 'SELECT COUNT(*) FROM organizations;' > /dev/null
"

# Test Redis connection
run_test "Redis Connection" "
    docker-compose -f docker-compose.dev.yml exec -T redis redis-cli ping | grep -q PONG
"

# Seed database
echo -e "\n🌱 Seeding database..."
python scripts/seed-database.py

# Start API in background
echo -e "\n🚀 Starting API server..."
cd apps/api
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
API_PID=$!
cd ../..

# Wait for API to start
echo "⏳ Waiting for API..."
timeout=30
counter=0
until curl -s http://localhost:8000/health > /dev/null; do
    if [ $counter -eq $timeout ]; then
        echo -e "${RED}❌ API failed to start${NC}"
        kill $API_PID 2>/dev/null || true
        exit 1
    fi
    sleep 1
    ((counter++))
done

echo -e "${GREEN}✅ API is running${NC}"

# Run API tests
run_test "API Health Check" "
    curl -s http://localhost:8000/health | grep -q 'healthy'
"

run_test "API Documentation" "
    curl -s http://localhost:8000/docs > /dev/null
"

# Run comprehensive API tests
echo -e "\n🧪 Running API endpoint tests..."
if python scripts/test-api.py; then
    echo -e "${GREEN}✅ API tests passed${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}❌ API tests failed${NC}"
    ((TESTS_FAILED++))
fi

# Test frontend build
echo -e "\n🎨 Testing frontend build..."
cd apps/web

run_test "Frontend Dependencies" "pnpm install --frozen-lockfile"
run_test "Frontend TypeScript Check" "pnpm type-check"
run_test "Frontend Linting" "pnpm lint --max-warnings=0"
run_test "Frontend Build" "pnpm build"

cd ../..

# Test data integrity
echo -e "\n📊 Testing data integrity..."

run_test "Sample Players Exist" "
    curl -s http://localhost:8000/api/v1/players | jq -e '.length > 10' > /dev/null
"

run_test "Sample Events Exist" "
    curl -s http://localhost:8000/api/v1/events | jq -e '.length > 0' > /dev/null
"

run_test "Leaderboard Works" "
    curl -s http://localhost:8000/api/v1/results/leaderboard | jq -e '.leaderboard | length > 0' > /dev/null
"

run_test "Player Masterpoints Calculation" "
    curl -s http://localhost:8000/api/v1/players/1/masterpoints | jq -e '.total_points > 0' > /dev/null
"

# Performance tests
echo -e "\n⚡ Running performance tests..."

run_test "API Response Time < 500ms" "
    response_time=\$(curl -o /dev/null -s -w '%{time_total}' http://localhost:8000/api/v1/players)
    (( \$(echo \"\$response_time < 0.5\" | bc -l) ))
"

run_test "Database Query Performance" "
    time_result=\$(docker-compose -f docker-compose.dev.yml exec -T postgres psql -U bridge_user -d bridge_platform_dev -c \"
        \\timing on
        SELECT COUNT(*) FROM players;
    \" 2>&1 | grep 'Time:' | awk '{print \$2}' | sed 's/ms//')
    (( \$(echo \"\$time_result < 100\" | bc -l) ))
"

# Cleanup
echo -e "\n🧹 Cleaning up..."
kill $API_PID 2>/dev/null || true
sleep 2

# Summary
echo -e "\n📋 Test Summary"
echo "==============="
echo -e "Tests passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests failed: ${RED}$TESTS_FAILED${NC}"
echo -e "Total tests: $((TESTS_PASSED + TESTS_FAILED))"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All tests passed! The Bridge Platform is ready for deployment.${NC}"
    echo -e "\n📝 Next steps:"
    echo "   1. Review the test results above"
    echo "   2. Test the frontend manually at http://localhost:3000"
    echo "   3. Deploy to AWS when ready"
    exit 0
else
    echo -e "\n${RED}❌ Some tests failed. Please fix the issues before deployment.${NC}"
    exit 1
fi