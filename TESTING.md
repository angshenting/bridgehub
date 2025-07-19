# Bridge Platform Testing Guide

## Prerequisites

Before testing, ensure you have:

- **Docker** and Docker Compose installed
- **pnpm** package manager (`npm install -g pnpm`)
- **Python 3.11+** for API testing
- **curl** and **jq** for API testing (optional but recommended)

## Quick Start Testing

### 1. Automated Setup and Testing

Run the complete test suite with one command:

```bash
# Setup environment and run all tests
./scripts/setup-dev.sh && ./scripts/test-integration.sh
```

### 2. Manual Step-by-Step Testing

If you prefer to test manually:

#### Step 1: Environment Setup
```bash
# Start Docker services
docker-compose -f docker-compose.dev.yml up -d

# Install dependencies
pnpm install

# Seed database with sample data
python scripts/seed-database.py
```

#### Step 2: Start Backend API
```bash
cd apps/api
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### Step 3: Test API Endpoints
```bash
# In another terminal
python scripts/test-api.py
```

#### Step 4: Start Frontend
```bash
cd apps/web
pnpm dev
```

#### Step 5: Manual Testing
- Visit http://localhost:3000 for the frontend
- Visit http://localhost:8000/docs for API documentation
- Visit http://localhost:8080 for database admin (Adminer)

## Testing Components

### 🔧 Infrastructure Tests

| Component | URL | Test |
|-----------|-----|------|
| PostgreSQL | localhost:5432 | `docker-compose exec postgres pg_isready` |
| Redis | localhost:6379 | `docker-compose exec redis redis-cli ping` |
| Adminer | http://localhost:8080 | Database admin interface |

### 🚀 API Tests

| Endpoint | Method | Test Purpose |
|----------|--------|--------------|
| `/health` | GET | Health check |
| `/api/v1/players` | GET | Player listing |
| `/api/v1/players/1` | GET | Individual player |
| `/api/v1/players/1/masterpoints` | GET | Masterpoints calculation |
| `/api/v1/events` | GET | Event listing |
| `/api/v1/events/recent` | GET | Recent events |
| `/api/v1/results/leaderboard` | GET | Leaderboard generation |

### 🎨 Frontend Tests

| Component | Purpose |
|-----------|---------|
| Build | `pnpm build` - Production build |
| TypeScript | `pnpm type-check` - Type safety |
| Linting | `pnpm lint` - Code quality |
| Development | `pnpm dev` - Hot reload |

### 📊 Data Tests

The seeded database includes:
- **16 sample players** with realistic bridge player data
- **5 sample events** (3 completed, 2 planned)
- **Tournament results** with scores and masterpoints
- **OpenSkill ratings** for all players
- **Subscriptions** for some players

## Test Scripts

### `setup-dev.sh`
Comprehensive development environment setup:
- Checks prerequisites
- Starts Docker services
- Seeds database
- Provides next steps

### `test-api.py`
Comprehensive API testing:
- Tests all endpoints
- Measures response times
- Validates data integrity
- Checks error handling

### `test-integration.sh`
Full integration testing:
- Infrastructure tests
- API functionality tests
- Frontend build tests
- Performance tests
- Data integrity tests

## Expected Test Results

### ✅ Successful Test Indicators

1. **API Health**: All endpoints return expected status codes
2. **Response Times**: < 500ms for most endpoints
3. **Data Integrity**: Players, events, and results are properly linked
4. **Frontend Build**: No TypeScript errors or linting issues
5. **Database Performance**: Queries execute in < 100ms

### 📈 Sample Data Verification

After seeding, you should see:
- 16+ players in the system
- 5 events (mix of completed and planned)
- Tournament results with proper scoring
- Masterpoints leaderboard working
- Recent events showing correctly

## Performance Benchmarks

| Metric | Target | Test |
|--------|--------|------|
| API Response Time | < 500ms | Average endpoint response |
| Database Queries | < 100ms | Common bridge queries |
| Frontend Build | < 2 minutes | Production build time |
| Page Load | < 2 seconds | Initial page load |

## Bridge-Specific Testing

### Tournament Data
- **Masterpoints calculation**: Verify points are correctly calculated and summed
- **Rating updates**: Check OpenSkill ratings are realistic (mu: 20-30, sigma: 2-4)
- **Results formatting**: Confirm bridge-specific data (percentages, positions)
- **Leaderboard accuracy**: Ensure ranking reflects masterpoints correctly

### API Functionality
- **Player search**: Filter by status, organization
- **Event filtering**: By date range, type, status
- **Results queries**: By event, player, time period
- **Data relationships**: Players → Events → Results → Masterpoints

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   ```bash
   # Check if PostgreSQL is running
   docker-compose -f docker-compose.dev.yml ps
   
   # Restart if needed
   docker-compose -f docker-compose.dev.yml restart postgres
   ```

2. **API Import Errors**
   ```bash
   # Ensure you're in the right directory
   cd apps/api
   pip install -r requirements.txt
   
   # Check Python path
   export PYTHONPATH=.
   ```

3. **Frontend Build Issues**
   ```bash
   # Clear cache and reinstall
   pnpm store prune
   rm -rf node_modules
   pnpm install
   ```

4. **Port Conflicts**
   - API: Port 8000
   - Frontend: Port 3000
   - Database: Port 5432
   - Redis: Port 6379
   - Adminer: Port 8080

### Performance Issues

If tests are slow:
1. Check Docker resource allocation
2. Ensure SSD storage for database
3. Increase shared memory for PostgreSQL
4. Monitor system resources during tests

## Manual Testing Checklist

### Backend ✅
- [ ] Health check responds
- [ ] API documentation loads
- [ ] All endpoints return valid JSON
- [ ] Database queries execute successfully
- [ ] Error handling works correctly

### Frontend ✅
- [ ] Homepage loads correctly
- [ ] Navigation works
- [ ] API data displays properly
- [ ] Mobile responsiveness
- [ ] Error states handled gracefully

### Bridge Features ✅
- [ ] Player masterpoints display correctly
- [ ] Event results show proper formatting
- [ ] Leaderboard ranks players accurately
- [ ] Recent events show with correct status
- [ ] Bridge-specific terminology used correctly

## AWS Deployment Readiness

After all tests pass, you're ready for AWS deployment when:

- ✅ All integration tests pass
- ✅ API responds correctly under load
- ✅ Frontend builds without errors
- ✅ Database performance is acceptable
- ✅ Bridge-specific features work correctly
- ✅ Security headers are present
- ✅ Error handling is robust

## Next Steps

1. **Manual Testing**: Test the UI manually at http://localhost:3000
2. **Load Testing**: Use scripts/test-api.py with higher concurrency
3. **Security Review**: Check authentication and authorization
4. **AWS Setup**: Configure production environment
5. **CI/CD Pipeline**: Set up automated testing

The Bridge Platform is architecturally ready for production deployment once all tests pass! 🌉