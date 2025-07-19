# Bridge Platform Project - CLAUDE.md

## Project Overview
This is a comprehensive bridge tournament management platform designed to replace legacy systems like Pianola and integrate with existing masterpoints and ratings systems. The platform scales from club games to international events with modern web technologies.

## Technology Stack

### Backend
- **Framework**: FastAPI (Python) or Next.js API routes (TypeScript)
- **Database**: PostgreSQL with Redis for caching
- **Authentication**: JWT-based with role-based access control
- **Real-time**: WebSockets for live scoring updates

### Frontend
- **Framework**: Next.js 14+ with TypeScript
- **Styling**: Tailwind CSS (mobile-first, responsive)
- **State Management**: Zustand or Redux Toolkit
- **Charts**: Recharts or Chart.js for statistics

### Infrastructure
- **Hosting**: Vercel (frontend) + Railway/Fly.io (backend)
- **Monitoring**: Sentry + analytics
- **CI/CD**: GitHub Actions

## Database Schema

### Core Tables
- **organizations**: Multi-level hierarchy (club, regional, national, international)
- **players**: Enhanced member data with legacy ID mapping
- **events**: Tournament events with flexible formats
- **sessions**: Individual sessions within tournaments
- **results**: Unified scoring results (MP, IMP, VP)
- **masterpoints**: Point awards by type and organization
- **ratings**: Multiple rating systems (OpenSkill, ELO, NGS)
- **hands**: PBN format hand records
- **contracts**: Detailed play results

### Migration from MySQL
The current MySQL database contains:
- **awards** (5 columns) - Masterpoint awards
- **events** (6 columns) - Tournament events
- **members** (13 columns) - Member information
- **rating_mp** (9 columns) - OpenSkill ratings with mu/sigma
- **score_imp** (6 columns) - IMP scoring results
- **score_rank_mp** (5 columns) - Matchpoint results
- **subscriptions** (7 columns) - Membership subscriptions

## Key Features

### 1. Event Management
- Multi-level events from club to international
- Flexible formats: Pairs, Teams, Swiss, Knockout, Round Robin, BAM
- Session management with real-time scoring
- Online registration and payment processing

### 2. Scoring System
- Real-time live results during play
- Multiple scoring: Matchpoints, IMPs, Butler, BAM
- PBN hand record integration
- Traveller views with analysis
- Mobile-friendly scoring interface

### 3. Player Management
- Unified player database across organizations
- Multiple masterpoint systems (WBF, ACBL, national)
- Rating calculations (OpenSkill, ELO, NGS)
- Historical performance tracking

### 4. Import/Export Capabilities
- **Pianola**: CSV member data and XML results
- **Bridgewebs**: Fixed-width text and CSV formats
- **ACBLscore**: Game files and text exports
- **Standard formats**: PBN, XML, CSV for bridge ecosystem

## Development Commands

### Database
```bash
# Run database migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"

# Reset database (development only)
psql -d bridge_db -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
```

### Backend (FastAPI)
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload --port 8000

# Run tests
pytest tests/

# Run type checking
mypy .

# Database seeding
python scripts/seed_database.py
```

### Frontend (Next.js)
```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build production
npm run build

# Run tests
npm run test

# Type checking
npm run type-check

# Linting
npm run lint
```

### Performance Testing
```bash
# Database load testing
python scripts/test_db_performance.py

# API load testing
python scripts/test_api_performance.py

# Frontend performance
npm run lighthouse
```

## Data Validation

### Pre-migration Checks
```sql
-- Check for duplicate member numbers
SELECT number, COUNT(*) as count FROM members GROUP BY number HAVING COUNT(*) > 1;

-- Validate email formats
SELECT * FROM members WHERE email NOT REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$';

-- Check orphaned awards
SELECT a.* FROM awards a LEFT JOIN members m ON a.member = m.id WHERE m.id IS NULL;
```

### Import Validation
```python
# Validate Pianola import file
from utils.pianola_importer import PianolaImporter
importer = PianolaImporter(db_connection)
validation_result = importer.validate_import_file("pianola_members.csv")
```

## Testing Strategy

### Unit Tests
- Backend API endpoints with pytest
- Frontend components with React Testing Library
- Database operations with test fixtures
- Utility functions and business logic

### Integration Tests
- End-to-end workflows with Playwright
- API integration with real database
- Payment processing scenarios
- Email delivery testing

### Performance Tests
- Load testing with Artillery or k6
- Database query optimization
- Frontend bundle optimization
- Mobile responsiveness testing

## Deployment

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/bridge_db
REDIS_URL=redis://localhost:6379

# Authentication
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256

# External Services
STRIPE_SECRET_KEY=your-stripe-key
SENDGRID_API_KEY=your-sendgrid-key
```

### Docker Development
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Security

### Authentication
- JWT tokens with refresh mechanism
- Role-based access control (RBAC)
- Rate limiting on API endpoints
- Session management with Redis

### Data Protection
- GDPR compliance for international events
- Audit trails for all changes
- Field-level encryption for sensitive data
- Secure payment processing (PCI compliance)

## Performance Targets

### Response Times
- Page load times: < 2 seconds globally
- API response times: < 100ms average
- Database queries: < 50ms for common operations
- Mobile load times: < 3 seconds

### Scalability
- Support 1000+ concurrent users during events
- 99.9% uptime during tournament periods
- Handle 10,000+ tournament participants
- Real-time updates within 5 seconds

## Common Operations

### Member Management
```python
# Import Pianola members
python scripts/import_pianola_members.py --file members.csv

# Bulk update member data
python scripts/update_members.py --organization scba
```

### Tournament Operations
```python
# Create tournament
python scripts/create_tournament.py --name "Club Championship" --type pairs

# Generate movement
python scripts/generate_movement.py --tournament-id 123 --type mitchell

# Calculate masterpoints
python scripts/calculate_masterpoints.py --event-id 456
```

### Data Export
```python
# Export results to CSV
python scripts/export_results.py --event-id 123 --format csv

# Generate PBN files
python scripts/export_pbn.py --session-id 789
```

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   - Check DATABASE_URL environment variable
   - Verify PostgreSQL is running
   - Check network connectivity

2. **Import Failures**
   - Validate file format before import
   - Check for data consistency
   - Review error logs for specific issues

3. **Performance Issues**
   - Monitor database query performance
   - Check Redis cache hit rates
   - Review API response times

4. **Authentication Problems**
   - Verify JWT_SECRET configuration
   - Check token expiration
   - Review user permissions

### Logging
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# View application logs
tail -f logs/bridge_platform.log

# Database query logging
# Add to PostgreSQL config: log_statement = 'all'
```

## Project Structure
```
bridge-platform/
├── apps/
│   ├── web/                 # Next.js frontend
│   ├── api/                 # FastAPI backend
│   └── mobile/              # Future mobile app
├── packages/
│   ├── database/            # Database schemas & migrations
│   ├── shared/              # Shared types & utilities
│   └── ui/                  # Shared UI components
├── docs/                    # Documentation
├── scripts/                 # Build & deployment scripts
├── tests/                   # Test suites
└── docker-compose.yml       # Local development setup
```

## Bridge-Specific Features

### Scoring Systems
- **Matchpoints**: Percentage-based scoring
- **IMPs**: International Match Points
- **Butler**: Aggregate scoring method
- **BAM**: Board-a-Match scoring

### Tournament Formats
- **Pairs**: Individual pair competition
- **Teams**: Team-based events
- **Swiss**: Swiss system tournaments
- **Knockout**: Elimination format
- **Round Robin**: All-play-all format

### Integration Support
- **BridgeMate**: Wireless scoring devices
- **ACBLscore**: ACBL tournament software
- **PBN**: Portable Bridge Notation
- **LIN**: Tournament record files

## Contact & Support

For technical issues or questions about this bridge platform:
- Check the documentation in the `/docs` folder
- Review the validation and import utilities
- Consult the performance benchmarking results
- Follow the development roadmap for implementation phases

This platform represents a modern, scalable solution for bridge tournament management that addresses the limitations of legacy systems while providing enhanced features for the digital age of bridge.