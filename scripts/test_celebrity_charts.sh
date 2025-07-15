#!/bin/bash
# Script to run celebrity chart integration tests

set -e

echo "🌟 Running Celebrity Chart Integration Tests 🌟"
echo "============================================"

# Check if test services are running
if ! docker-compose -f docker-compose.test.yml ps | grep -q "test-db.*Up"; then
    echo "Starting test database and Redis services..."
    docker-compose -f docker-compose.test.yml up -d test-db test-redis
    
    # Wait for services to be ready
    echo "Waiting for services to be ready..."
    sleep 10
fi

# Set test environment variables
export DATABASE_URL="postgresql+asyncpg://josi:josi@localhost:5433/josi_test"
export REDIS_URL="redis://localhost:6380/1"
export ENVIRONMENT="test"
export AUTO_DB_MIGRATION="true"
export SECRET_KEY="test-secret-key"
export EPHEMERIS_PATH="/usr/share/swisseph"
export RATE_LIMIT_ENABLED="false"

# Run database migrations
echo "Running database migrations..."
poetry run alembic upgrade head

# Run the celebrity chart tests
echo "Running celebrity chart integration tests..."
poetry run pytest tests/integration/test_celebrity_charts.py -v -s

# Run summary test
echo ""
echo "Generating test summary..."
poetry run pytest tests/integration/test_celebrity_charts.py::test_celebrity_chart_summary -v -s

echo ""
echo "✅ Celebrity chart tests completed!"