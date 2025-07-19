# SCBA Database Migration Plan

## Current MySQL Database Analysis

### Existing Tables Overview
Your current MySQL database contains 10 tables with 69 total columns:

1. **awards** (5 columns) - Masterpoint awards
2. **events** (6 columns) - Tournament events
3. **kv** (2 columns) - Key-value store
4. **members** (13 columns) - Member information
5. **members_backup2** (13 columns) - Member backup data
6. **nameindices** (3 columns) - Name search indices
7. **rating_mp** (9 columns) - Rating calculations with mu/sigma
8. **score_imp** (6 columns) - IMP scoring results
9. **score_rank_mp** (5 columns) - Matchpoint scoring results
10. **subscriptions** (7 columns) - Membership subscriptions

### Current Schema Details

#### Core Tables

**members** (Primary member data)
```sql
- id: int NOT NULL [PRI] auto_increment
- bmid: int NULL [UNI] DEFAULT NULL  -- Bridgemate ID?
- number: int NOT NULL [UNI]         -- Member number
- lastname: varchar NOT NULL
- firstname: varchar NOT NULL
- address: text NOT NULL
- mobile: varchar NOT NULL
- homecontact: varchar NOT NULL
- email: varchar NOT NULL
- gender: char NOT NULL
- birthdate: date NOT NULL
- joindate: date NOT NULL
- lastupdate: timestamp NOT NULL DEFAULT current_timestamp()
```

**events** (Tournament events)
```sql
- id: int NOT NULL [PRI] auto_increment
- code: varchar NULL [MUL] DEFAULT NULL  -- Event code
- date: date NOT NULL [MUL]
- name: varchar NOT NULL
- tables: int NULL DEFAULT NULL          -- Number of tables
- status: enum NULL DEFAULT NULL         -- Event status/level
```

**awards** (Masterpoint awards)
```sql
- id: int NOT NULL [PRI] auto_increment
- event: int NOT NULL [MUL]  -- Foreign key to events
- member: int NOT NULL [MUL] -- Foreign key to members
- lp: int NOT NULL           -- Local points
- nlp: int NOT NULL          -- National points
```

**rating_mp** (Rating system - OpenSkill implementation)
```sql
- id: int NOT NULL [PRI] auto_increment
- event: int NOT NULL [MUL]
- date: date NOT NULL
- member: int NOT NULL [MUL]
- mu: float NOT NULL         -- TrueSkill mu (skill estimate)
- sigma: float NOT NULL      -- TrueSkill sigma (uncertainty)
- mu_delta: float NOT NULL   -- Change in mu
- sigma_delta: float NOT NULL -- Change in sigma
- days_since_last: int NOT NULL
```

**score_imp** (IMP scoring results)
```sql
- id: int NOT NULL [PRI] auto_increment
- event: int NOT NULL [MUL]
- member: int NOT NULL [MUL]
- imp: float NOT NULL
- vp: float NOT NULL         -- Victory points
- partner: int NOT NULL [MUL] -- Partner member ID
```

**score_rank_mp** (Matchpoint scoring results)
```sql
- id: int NOT NULL [PRI] auto_increment
- event: int NOT NULL [MUL]
- member: int NOT NULL [MUL]
- rank: int NOT NULL
- score: float NOT NULL
```

**subscriptions** (Membership subscriptions)
```sql
- id: int NOT NULL [PRI] auto_increment
- member: int NOT NULL [MUL]
- type: enum NOT NULL        -- Subscription type
- expiry: date NOT NULL [MUL]
- fee: int NULL DEFAULT NULL
- paymentdate: date NULL DEFAULT NULL
- receipt: varchar NULL DEFAULT NULL
```

## Migration to PostgreSQL Schema

### Enhanced Schema Design

#### 1. Organizations & Hierarchy
```sql
-- New table for multi-level organization support
CREATE TABLE organizations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL, -- 'club', 'region', 'national', 'international'
    parent_id INTEGER REFERENCES organizations(id),
    country VARCHAR(3),
    settings JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. Enhanced Members Table
```sql
-- Migrate and enhance existing members table
CREATE TABLE players (
    id SERIAL PRIMARY KEY,
    legacy_id INTEGER, -- Original MySQL ID for migration
    bmid INTEGER UNIQUE, -- Bridgemate ID
    number INTEGER NOT NULL UNIQUE, -- Member number
    wbf_id VARCHAR(20), -- WBF player ID
    national_id VARCHAR(20), -- National federation ID
    organization_id INTEGER REFERENCES organizations(id),
    lastname VARCHAR(255) NOT NULL,
    firstname VARCHAR(255) NOT NULL,
    address TEXT,
    mobile VARCHAR(50),
    homecontact VARCHAR(50),
    email VARCHAR(255),
    gender CHAR(1),
    birthdate DATE,
    joindate DATE,
    status VARCHAR(20) DEFAULT 'active',
    settings JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 3. Enhanced Events System
```sql
-- Multi-level event hierarchy
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organizations(id),
    parent_event_id INTEGER REFERENCES events(id),
    code VARCHAR(50),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL, -- 'pairs', 'teams', 'swiss', 'knockout'
    start_date DATE NOT NULL,
    end_date DATE,
    status VARCHAR(20) DEFAULT 'planned',
    settings JSONB, -- Format-specific settings
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sessions within events
CREATE TABLE sessions (
    id SERIAL PRIMARY KEY,
    event_id INTEGER REFERENCES events(id),
    session_number INTEGER NOT NULL,
    date DATE NOT NULL,
    start_time TIME,
    status VARCHAR(20) DEFAULT 'planned',
    boards_played INTEGER,
    movement_type VARCHAR(50),
    settings JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 4. Enhanced Results System
```sql
-- Unified results table
CREATE TABLE results (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES sessions(id),
    event_id INTEGER REFERENCES events(id),
    player_id INTEGER REFERENCES players(id),
    partner_id INTEGER REFERENCES players(id),
    pair_number INTEGER,
    position INTEGER,
    score DECIMAL(10,2),
    percentage DECIMAL(5,2),
    imp_score DECIMAL(8,2),
    vp_score DECIMAL(6,2),
    masterpoints_awarded DECIMAL(6,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 5. Enhanced Rating System
```sql
-- Migrate existing rating_mp table
CREATE TABLE ratings (
    id SERIAL PRIMARY KEY,
    player_id INTEGER REFERENCES players(id),
    rating_type VARCHAR(20) NOT NULL, -- 'openskill', 'elo', 'ngs'
    event_id INTEGER REFERENCES events(id),
    date DATE NOT NULL,
    mu DECIMAL(8,4) NOT NULL,
    sigma DECIMAL(8,4) NOT NULL,
    mu_delta DECIMAL(8,4),
    sigma_delta DECIMAL(8,4),
    days_since_last INTEGER,
    confidence_interval DECIMAL(8,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 6. Enhanced Masterpoints System
```sql
-- Migrate existing awards table
CREATE TABLE masterpoints (
    id SERIAL PRIMARY KEY,
    player_id INTEGER REFERENCES players(id),
    event_id INTEGER REFERENCES events(id),
    organization_id INTEGER REFERENCES organizations(id),
    award_type VARCHAR(50) NOT NULL, -- 'local', 'national', 'regional', 'international'
    points DECIMAL(6,2) NOT NULL,
    level VARCHAR(50), -- Current masterpoint level
    awarded_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 7. Bridge-Specific Tables
```sql
-- Hand records and analysis
CREATE TABLE hands (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES sessions(id),
    board_number INTEGER NOT NULL,
    dealer VARCHAR(5) NOT NULL,
    vulnerability VARCHAR(10) NOT NULL,
    pbn_data TEXT, -- Portable Bridge Notation
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Detailed contract and play results
CREATE TABLE contracts (
    id SERIAL PRIMARY KEY,
    result_id INTEGER REFERENCES results(id),
    hand_id INTEGER REFERENCES hands(id),
    level INTEGER NOT NULL,
    suit VARCHAR(10) NOT NULL,
    doubled VARCHAR(10),
    declarer VARCHAR(5) NOT NULL,
    tricks INTEGER NOT NULL,
    score INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Migration Strategy

### Phase 1: Data Preparation
1. **Create PostgreSQL database** with new schema
2. **Backup existing MySQL data**
3. **Data cleaning**: Fix any inconsistencies in member names, emails
4. **Create organization hierarchy**: Start with SCBA as root organization

### Phase 2: Core Data Migration
1. **Migrate members table**:
   ```sql
   INSERT INTO players (legacy_id, bmid, number, lastname, firstname, address, mobile, homecontact, email, gender, birthdate, joindate, organization_id)
   SELECT id, bmid, number, lastname, firstname, address, mobile, homecontact, email, gender, birthdate, joindate, 1
   FROM mysql_members;
   ```

2. **Migrate events table**:
   ```sql
   INSERT INTO events (code, name, start_date, organization_id, settings)
   SELECT code, name, date, 1, JSON_BUILD_OBJECT('tables', tables, 'status', status)
   FROM mysql_events;
   ```

3. **Migrate awards to masterpoints**:
   ```sql
   INSERT INTO masterpoints (player_id, event_id, award_type, points, awarded_date)
   SELECT 
     p.id, e.id, 
     CASE WHEN a.nlp > 0 THEN 'national' ELSE 'local' END,
     (a.lp + a.nlp), e.start_date
   FROM mysql_awards a
   JOIN players p ON p.legacy_id = a.member
   JOIN events e ON e.id = a.event;
   ```

4. **Migrate ratings**:
   ```sql
   INSERT INTO ratings (player_id, rating_type, event_id, date, mu, sigma, mu_delta, sigma_delta, days_since_last)
   SELECT p.id, 'openskill', e.id, r.date, r.mu, r.sigma, r.mu_delta, r.sigma_delta, r.days_since_last
   FROM mysql_rating_mp r
   JOIN players p ON p.legacy_id = r.member
   JOIN events e ON e.id = r.event;
   ```

### Phase 3: Results Migration
1. **Migrate score_rank_mp to results**:
   ```sql
   INSERT INTO results (player_id, event_id, position, score, percentage)
   SELECT p.id, s.event, s.rank, s.score, (s.score * 100.0 / MAX(s.score) OVER (PARTITION BY s.event))
   FROM mysql_score_rank_mp s
   JOIN players p ON p.legacy_id = s.member;
   ```

2. **Migrate score_imp to results**:
   ```sql
   INSERT INTO results (player_id, event_id, partner_id, imp_score, vp_score)
   SELECT p.id, s.event, partner.id, s.imp, s.vp
   FROM mysql_score_imp s
   JOIN players p ON p.legacy_id = s.member
   JOIN players partner ON partner.legacy_id = s.partner;
   ```

### Phase 4: Validation & Testing
1. **Data integrity checks**:
   - Verify all foreign key relationships
   - Check for missing data
   - Validate point calculations
   - Test rating calculations

2. **Performance optimization**:
   - Create appropriate indexes
   - Optimize queries for common operations
   - Set up database monitoring

### Phase 5: Cutover
1. **Run new and old systems in parallel**
2. **Train users on new interface**
3. **Gradual migration of live events**
4. **Monitor performance and fix issues**

## Key Improvements in New Schema

### 1. Scalability
- **Multi-organization support**: Can handle club, regional, national events
- **Event hierarchy**: Tournaments can contain multiple sessions
- **Flexible settings**: JSONB fields for format-specific data

### 2. Data Integrity
- **Proper foreign keys**: Better referential integrity
- **Standardized enums**: Consistent data values
- **Audit trails**: Created/updated timestamps

### 3. Bridge-Specific Features
- **Hand records**: PBN format support
- **Multiple scoring systems**: MP, IMP, VP in single table
- **Rating flexibility**: Support for multiple rating systems
- **Partnership tracking**: Proper partner relationships

### 4. Performance
- **Indexes**: Strategic indexing for common queries
- **Partitioning**: Large tables can be partitioned by date
- **Materialized views**: Pre-computed statistics

## Migration Timeline

- **Week 1-2**: Schema design and testing
- **Week 3**: Data migration scripts development
- **Week 4**: Migration testing with sample data
- **Week 5**: Full migration and validation
- **Week 6**: Parallel running and testing
- **Week 7**: Cutover and monitoring

## Rollback Plan

1. **Keep MySQL database**: Maintain for 6 months as backup
2. **Export capabilities**: Ability to export back to MySQL format
3. **Point-in-time recovery**: Regular PostgreSQL backups
4. **Incremental sync**: Tools to sync changes back to MySQL if needed

This migration plan preserves all your existing data while dramatically improving the system's capabilities for your new bridge platform.