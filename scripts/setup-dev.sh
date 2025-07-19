#!/bin/bash

# Bridge Platform Local Development Setup Script
set -e

echo "🌉 Setting up Bridge Platform for local development..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if pnpm is installed
if ! command -v pnpm &> /dev/null; then
    echo "❌ pnpm is not installed. Please install pnpm first:"
    echo "   npm install -g pnpm"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from example..."
    cp .env.example .env
    echo "⚠️  Please update .env with your specific configuration"
fi

# Install dependencies
echo "📦 Installing dependencies..."
pnpm install

# Start Docker services
echo "🐳 Starting Docker services (PostgreSQL, Redis, Adminer)..."
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml up -d

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
timeout=60
counter=0
until docker-compose -f docker-compose.dev.yml exec -T postgres pg_isready -U bridge_user -d bridge_platform_dev; do
    if [ $counter -eq $timeout ]; then
        echo "❌ Database failed to start within $timeout seconds"
        exit 1
    fi
    echo "Waiting for database... ($counter/$timeout)"
    sleep 1
    counter=$((counter + 1))
done

echo "✅ Database is ready"

# Seed the database with sample data
echo "🌱 Seeding database with sample data..."
python scripts/seed-database.py

# Verify API can start
echo "🔍 Testing API startup..."
cd apps/api
python -c "
import sys
sys.path.append('.')
from app.main import app
from app.core.config import settings
print(f'✅ API configuration loaded successfully')
print(f'   Database URL: {settings.DATABASE_URL[:50]}...')
print(f'   Debug mode: {settings.DEBUG}')
"
cd ../..

echo "🎉 Local development environment is ready!"
echo ""
echo "📋 Next steps:"
echo "   1. Start the API: cd apps/api && uvicorn app.main:app --reload --port 8000"
echo "   2. Start the frontend: cd apps/web && pnpm dev"
echo "   3. Visit http://localhost:3000 for the frontend"
echo "   4. Visit http://localhost:8000/docs for API documentation"
echo "   5. Visit http://localhost:8080 for database admin (Adminer)"
echo ""
echo "🔗 Useful URLs:"
echo "   Frontend: http://localhost:3000"
echo "   API Docs: http://localhost:8000/docs"
echo "   Database Admin: http://localhost:8080"
echo "   Health Check: http://localhost:8000/health"