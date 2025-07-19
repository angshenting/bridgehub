-- Bridge Platform Database Schema
-- PostgreSQL implementation based on migration plan

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Organizations table for multi-level hierarchy
CREATE TABLE organizations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL CHECK (type IN ('club', 'region', 'national', 'international')),
    parent_id INTEGER REFERENCES organizations(id),
    country VARCHAR(3),
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Enhanced players table (migrated from members)
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
    gender CHAR(1) CHECK (gender IN ('M', 'F')),
    birthdate DATE,
    joindate DATE,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'suspended')),
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Enhanced events system
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organizations(id),
    parent_event_id INTEGER REFERENCES events(id),
    legacy_id INTEGER, -- For migration
    code VARCHAR(50),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL CHECK (type IN ('pairs', 'teams', 'swiss', 'knockout', 'round_robin', 'bam')),
    start_date DATE NOT NULL,
    end_date DATE,
    status VARCHAR(20) DEFAULT 'planned' CHECK (status IN ('planned', 'active', 'completed', 'cancelled')),
    settings JSONB DEFAULT '{}',
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
    status VARCHAR(20) DEFAULT 'planned' CHECK (status IN ('planned', 'active', 'completed', 'cancelled')),
    boards_played INTEGER,
    movement_type VARCHAR(50),
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

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

-- Enhanced rating system
CREATE TABLE ratings (
    id SERIAL PRIMARY KEY,
    player_id INTEGER REFERENCES players(id),
    rating_type VARCHAR(20) NOT NULL CHECK (rating_type IN ('openskill', 'elo', 'ngs')),
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

-- Enhanced masterpoints system
CREATE TABLE masterpoints (
    id SERIAL PRIMARY KEY,
    player_id INTEGER REFERENCES players(id),
    event_id INTEGER REFERENCES events(id),
    organization_id INTEGER REFERENCES organizations(id),
    award_type VARCHAR(50) NOT NULL CHECK (award_type IN ('local', 'national', 'regional', 'international')),
    points DECIMAL(6,2) NOT NULL,
    level VARCHAR(50), -- Current masterpoint level
    awarded_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Hand records and analysis
CREATE TABLE hands (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES sessions(id),
    board_number INTEGER NOT NULL,
    dealer VARCHAR(5) NOT NULL CHECK (dealer IN ('N', 'S', 'E', 'W')),
    vulnerability VARCHAR(10) NOT NULL CHECK (vulnerability IN ('None', 'NS', 'EW', 'All')),
    pbn_data TEXT, -- Portable Bridge Notation
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Detailed contract and play results
CREATE TABLE contracts (
    id SERIAL PRIMARY KEY,
    result_id INTEGER REFERENCES results(id),
    hand_id INTEGER REFERENCES hands(id),
    level INTEGER NOT NULL CHECK (level BETWEEN 1 AND 7),
    suit VARCHAR(10) NOT NULL CHECK (suit IN ('C', 'D', 'H', 'S', 'NT')),
    doubled VARCHAR(10) CHECK (doubled IN ('', 'X', 'XX')),
    declarer VARCHAR(5) NOT NULL CHECK (declarer IN ('N', 'S', 'E', 'W')),
    tricks INTEGER NOT NULL CHECK (tricks BETWEEN 0 AND 13),
    score INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Import logging table
CREATE TABLE import_log (
    id SERIAL PRIMARY KEY,
    import_type VARCHAR(50) NOT NULL,
    data_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('success', 'failure', 'partial')),
    records_imported INTEGER DEFAULT 0,
    errors_count INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Subscriptions (migrated from existing table)
CREATE TABLE subscriptions (
    id SERIAL PRIMARY KEY,
    player_id INTEGER REFERENCES players(id),
    type VARCHAR(50) NOT NULL CHECK (type IN ('full', 'social', 'student', 'life')),
    expiry DATE NOT NULL,
    fee DECIMAL(8,2),
    payment_date DATE,
    receipt VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance optimization
CREATE INDEX CONCURRENTLY idx_players_number ON players(number);
CREATE INDEX CONCURRENTLY idx_players_organization ON players(organization_id);
CREATE INDEX CONCURRENTLY idx_players_status ON players(status);
CREATE INDEX CONCURRENTLY idx_players_legacy_id ON players(legacy_id);

CREATE INDEX CONCURRENTLY idx_events_organization ON events(organization_id);
CREATE INDEX CONCURRENTLY idx_events_date ON events(start_date DESC);
CREATE INDEX CONCURRENTLY idx_events_status ON events(status);

CREATE INDEX CONCURRENTLY idx_results_event ON results(event_id);
CREATE INDEX CONCURRENTLY idx_results_player ON results(player_id);
CREATE INDEX CONCURRENTLY idx_results_session ON results(session_id);
CREATE INDEX CONCURRENTLY idx_results_position ON results(position);

CREATE INDEX CONCURRENTLY idx_masterpoints_player ON masterpoints(player_id);
CREATE INDEX CONCURRENTLY idx_masterpoints_event ON masterpoints(event_id);
CREATE INDEX CONCURRENTLY idx_masterpoints_type ON masterpoints(award_type);
CREATE INDEX CONCURRENTLY idx_masterpoints_date ON masterpoints(awarded_date DESC);

CREATE INDEX CONCURRENTLY idx_ratings_player_type ON ratings(player_id, rating_type);
CREATE INDEX CONCURRENTLY idx_ratings_date ON ratings(date DESC);

CREATE INDEX CONCURRENTLY idx_sessions_event ON sessions(event_id);
CREATE INDEX CONCURRENTLY idx_sessions_date ON sessions(date DESC);

CREATE INDEX CONCURRENTLY idx_hands_session ON hands(session_id);
CREATE INDEX CONCURRENTLY idx_hands_board ON hands(board_number);

-- Triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON organizations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_players_updated_at BEFORE UPDATE ON players
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_events_updated_at BEFORE UPDATE ON events
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default organization
INSERT INTO organizations (name, type, country, settings) 
VALUES ('Singapore Contract Bridge Association', 'national', 'SGP', '{"timezone": "Asia/Singapore", "currency": "SGD"}');

-- Sample data for development
INSERT INTO players (number, firstname, lastname, email, organization_id, status, joindate) VALUES
(1001, 'John', 'Smith', 'john.smith@email.com', 1, 'active', '2020-01-15'),
(1002, 'Jane', 'Doe', 'jane.doe@email.com', 1, 'active', '2020-02-20'),
(1003, 'Bob', 'Brown', 'bob.brown@email.com', 1, 'active', '2020-03-10'),
(1004, 'Alice', 'White', 'alice.white@email.com', 1, 'active', '2020-04-05');