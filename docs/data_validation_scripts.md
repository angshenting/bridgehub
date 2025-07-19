# Data Validation Scripts for Bridge Platform Migration

## Overview
These scripts ensure data integrity during the migration from MySQL to PostgreSQL and validate the new bridge platform's data consistency.

## Pre-Migration Validation Scripts

### 1. MySQL Data Quality Checks

```sql
-- Check for duplicate member numbers
SELECT number, COUNT(*) as count
FROM members 
GROUP BY number 
HAVING COUNT(*) > 1;

-- Check for invalid email formats
SELECT id, email, firstname, lastname
FROM members 
WHERE email IS NOT NULL 
AND email NOT REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$';

-- Check for orphaned awards (awards without corresponding members)
SELECT a.id, a.member, a.event
FROM awards a
LEFT JOIN members m ON a.member = m.id
WHERE m.id IS NULL;

-- Check for orphaned awards (awards without corresponding events)
SELECT a.id, a.member, a.event
FROM awards a
LEFT JOIN events e ON a.event = e.id
WHERE e.id IS NULL;

-- Check for invalid dates
SELECT id, firstname, lastname, birthdate, joindate
FROM members 
WHERE birthdate > CURDATE() 
OR joindate > CURDATE()
OR birthdate > joindate;

-- Check for missing required fields
SELECT id, firstname, lastname, email, mobile
FROM members 
WHERE firstname = '' OR lastname = '' OR email = '' OR mobile = '';

-- Check rating system consistency
SELECT COUNT(*) as total_ratings,
       COUNT(DISTINCT member) as unique_members,
       MIN(date) as earliest_rating,
       MAX(date) as latest_rating,
       AVG(mu) as avg_mu,
       AVG(sigma) as avg_sigma
FROM rating_mp;

-- Check for negative masterpoints
SELECT a.id, a.member, a.event, a.lp, a.nlp
FROM awards a
WHERE a.lp < 0 OR a.nlp < 0;
```

### 2. Data Consistency Validation

```sql
-- Verify event participation consistency
SELECT e.id, e.name, e.date,
       COUNT(DISTINCT a.member) as members_with_awards,
       COUNT(DISTINCT s1.member) as members_with_mp_scores,
       COUNT(DISTINCT s2.member) as members_with_imp_scores
FROM events e
LEFT JOIN awards a ON e.id = a.event
LEFT JOIN score_rank_mp s1 ON e.id = s1.event
LEFT JOIN score_imp s2 ON e.id = s2.event
GROUP BY e.id, e.name, e.date
HAVING members_with_awards != members_with_mp_scores 
   OR members_with_awards != members_with_imp_scores;

-- Check for rating updates without corresponding events
SELECT r.id, r.member, r.event, r.date
FROM rating_mp r
LEFT JOIN events e ON r.event = e.id
WHERE e.id IS NULL;

-- Validate partner relationships in IMP scoring
SELECT s.id, s.member, s.partner, s.event
FROM score_imp s
LEFT JOIN members m1 ON s.member = m1.id
LEFT JOIN members m2 ON s.partner = m2.id
WHERE m1.id IS NULL OR m2.id IS NULL;
```

## Migration Validation Scripts

### 3. PostgreSQL Migration Verification

```sql
-- Count verification: Ensure all records migrated
SELECT 
    'members' as table_name,
    (SELECT COUNT(*) FROM mysql_members) as mysql_count,
    (SELECT COUNT(*) FROM players WHERE legacy_id IS NOT NULL) as postgres_count,
    (SELECT COUNT(*) FROM mysql_members) - (SELECT COUNT(*) FROM players WHERE legacy_id IS NOT NULL) as difference;

-- Sample data verification
SELECT 
    m.id as mysql_id,
    m.number as mysql_number,
    m.firstname as mysql_firstname,
    m.lastname as mysql_lastname,
    p.id as postgres_id,
    p.number as postgres_number,
    p.firstname as postgres_firstname,
    p.lastname as postgres_lastname
FROM mysql_members m
JOIN players p ON p.legacy_id = m.id
WHERE m.id <= 10
ORDER BY m.id;

-- Foreign key integrity check
SELECT 
    COUNT(*) as total_masterpoints,
    COUNT(CASE WHEN player_id IS NOT NULL THEN 1 END) as valid_player_refs,
    COUNT(CASE WHEN event_id IS NOT NULL THEN 1 END) as valid_event_refs
FROM masterpoints;

-- Rating system migration verification
SELECT 
    COUNT(*) as total_ratings,
    AVG(mu) as avg_mu,
    AVG(sigma) as avg_sigma,
    MIN(date) as earliest_date,
    MAX(date) as latest_date
FROM ratings 
WHERE rating_type = 'openskill';
```

### 4. Business Logic Validation

```sql
-- Masterpoints calculation verification
WITH player_totals AS (
    SELECT 
        player_id,
        SUM(CASE WHEN award_type = 'local' THEN points ELSE 0 END) as local_points,
        SUM(CASE WHEN award_type = 'national' THEN points ELSE 0 END) as national_points
    FROM masterpoints
    GROUP BY player_id
),
mysql_totals AS (
    SELECT 
        member,
        SUM(lp) as mysql_lp,
        SUM(nlp) as mysql_nlp
    FROM mysql_awards
    GROUP BY member
)
SELECT 
    p.id,
    p.firstname,
    p.lastname,
    pt.local_points,
    mt.mysql_lp,
    pt.national_points,
    mt.mysql_nlp,
    ABS(pt.local_points - mt.mysql_lp) as lp_diff,
    ABS(pt.national_points - mt.mysql_nlp) as nlp_diff
FROM players p
JOIN player_totals pt ON p.id = pt.player_id
JOIN mysql_totals mt ON p.legacy_id = mt.member
WHERE ABS(pt.local_points - mt.mysql_lp) > 0.01 
   OR ABS(pt.national_points - mt.mysql_nlp) > 0.01;
```

## Post-Migration Validation Scripts

### 5. Application Logic Validation

```sql
-- Test event creation and results entry
INSERT INTO events (organization_id, name, type, start_date, status)
VALUES (1, 'Test Event', 'pairs', CURRENT_DATE, 'active');

-- Verify triggers and constraints work
INSERT INTO results (event_id, player_id, partner_id, score, percentage)
VALUES (
    (SELECT id FROM events WHERE name = 'Test Event'),
    (SELECT id FROM players ORDER BY id LIMIT 1),
    (SELECT id FROM players ORDER BY id LIMIT 1 OFFSET 1),
    65.5, 65.5
);

-- Test rating calculations
SELECT 
    p.id,
    p.firstname,
    p.lastname,
    r.mu,
    r.sigma,
    r.mu - (2 * r.sigma) as conservative_rating
FROM players p
JOIN ratings r ON p.id = r.player_id
WHERE r.rating_type = 'openskill'
ORDER BY r.mu DESC
LIMIT 10;
```

### 6. Performance Validation

```sql
-- Check query performance on large datasets
EXPLAIN ANALYZE
SELECT 
    p.firstname,
    p.lastname,
    SUM(mp.points) as total_points,
    COUNT(r.id) as events_played,
    MAX(rt.mu) as current_rating
FROM players p
LEFT JOIN masterpoints mp ON p.id = mp.player_id
LEFT JOIN results r ON p.id = r.player_id
LEFT JOIN ratings rt ON p.id = rt.player_id AND rt.rating_type = 'openskill'
GROUP BY p.id, p.firstname, p.lastname
ORDER BY total_points DESC;

-- Index usage verification
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_tup_read DESC;
```

## Python Validation Scripts

### 7. Comprehensive Data Validation Script

```python
import psycopg2
import pandas as pd
import logging
from datetime import datetime
from typing import Dict, List, Any

class BridgeDataValidator:
    def __init__(self, postgres_conn_str: str, mysql_conn_str: str):
        self.pg_conn = psycopg2.connect(postgres_conn_str)
        self.mysql_conn = mysql.connector.connect(mysql_conn_str)
        self.validation_results = {}
        
    def validate_member_migration(self) -> Dict[str, Any]:
        """Validate member data migration"""
        # Count validation
        mysql_count = self.execute_mysql("SELECT COUNT(*) FROM members")[0][0]
        pg_count = self.execute_postgres("SELECT COUNT(*) FROM players WHERE legacy_id IS NOT NULL")[0][0]
        
        # Sample data validation
        sample_query = """
        SELECT m.id, m.number, m.firstname, m.lastname, m.email,
               p.id, p.number, p.firstname, p.lastname, p.email
        FROM mysql_members m
        JOIN players p ON p.legacy_id = m.id
        LIMIT 100
        """
        
        results = {
            'mysql_count': mysql_count,
            'postgres_count': pg_count,
            'migration_success': mysql_count == pg_count,
            'sample_validation': self.validate_sample_data(sample_query)
        }
        
        return results
    
    def validate_masterpoints_calculation(self) -> Dict[str, Any]:
        """Validate masterpoints calculations"""
        query = """
        SELECT 
            p.id,
            p.firstname,
            p.lastname,
            COALESCE(SUM(CASE WHEN mp.award_type = 'local' THEN mp.points ELSE 0 END), 0) as pg_local,
            COALESCE(SUM(CASE WHEN mp.award_type = 'national' THEN mp.points ELSE 0 END), 0) as pg_national,
            COALESCE(SUM(a.lp), 0) as mysql_local,
            COALESCE(SUM(a.nlp), 0) as mysql_national
        FROM players p
        LEFT JOIN masterpoints mp ON p.id = mp.player_id
        LEFT JOIN mysql_awards a ON p.legacy_id = a.member
        GROUP BY p.id, p.firstname, p.lastname
        HAVING ABS(COALESCE(SUM(CASE WHEN mp.award_type = 'local' THEN mp.points ELSE 0 END), 0) - COALESCE(SUM(a.lp), 0)) > 0.01
           OR ABS(COALESCE(SUM(CASE WHEN mp.award_type = 'national' THEN mp.points ELSE 0 END), 0) - COALESCE(SUM(a.nlp), 0)) > 0.01
        """
        
        discrepancies = self.execute_postgres(query)
        
        return {
            'discrepancies_found': len(discrepancies),
            'discrepancies': discrepancies[:10]  # First 10 discrepancies
        }
    
    def validate_rating_system(self) -> Dict[str, Any]:
        """Validate rating system migration"""
        stats_query = """
        SELECT 
            COUNT(*) as total_ratings,
            COUNT(DISTINCT player_id) as unique_players,
            AVG(mu) as avg_mu,
            AVG(sigma) as avg_sigma,
            MIN(date) as earliest_date,
            MAX(date) as latest_date
        FROM ratings 
        WHERE rating_type = 'openskill'
        """
        
        stats = self.execute_postgres(stats_query)[0]
        
        # Check for reasonable rating values
        outliers_query = """
        SELECT player_id, mu, sigma 
        FROM ratings 
        WHERE rating_type = 'openskill'
        AND (mu < 0 OR mu > 50 OR sigma < 0 OR sigma > 10)
        """
        
        outliers = self.execute_postgres(outliers_query)
        
        return {
            'total_ratings': stats[0],
            'unique_players': stats[1],
            'avg_mu': float(stats[2]),
            'avg_sigma': float(stats[3]),
            'date_range': f"{stats[4]} to {stats[5]}",
            'outliers_found': len(outliers)
        }
    
    def validate_data_integrity(self) -> Dict[str, Any]:
        """Validate foreign key relationships and data integrity"""
        checks = {
            'orphaned_masterpoints': "SELECT COUNT(*) FROM masterpoints mp LEFT JOIN players p ON mp.player_id = p.id WHERE p.id IS NULL",
            'orphaned_results': "SELECT COUNT(*) FROM results r LEFT JOIN players p ON r.player_id = p.id WHERE p.id IS NULL",
            'orphaned_ratings': "SELECT COUNT(*) FROM ratings rt LEFT JOIN players p ON rt.player_id = p.id WHERE p.id IS NULL",
            'invalid_partnerships': "SELECT COUNT(*) FROM results r LEFT JOIN players p ON r.partner_id = p.id WHERE r.partner_id IS NOT NULL AND p.id IS NULL"
        }
        
        results = {}
        for check_name, query in checks.items():
            count = self.execute_postgres(query)[0][0]
            results[check_name] = count
            
        return results
    
    def generate_validation_report(self) -> str:
        """Generate comprehensive validation report"""
        report = f"""
# Bridge Platform Data Validation Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Migration Validation
{self.validate_member_migration()}

## Masterpoints Validation
{self.validate_masterpoints_calculation()}

## Rating System Validation
{self.validate_rating_system()}

## Data Integrity Validation
{self.validate_data_integrity()}
"""
        return report

# Usage example
if __name__ == "__main__":
    validator = BridgeDataValidator(
        postgres_conn_str="postgresql://user:pass@localhost:5432/bridge_db",
        mysql_conn_str="mysql://user:pass@localhost:3306/old_bridge_db"
    )
    
    report = validator.generate_validation_report()
    print(report)
    
    # Save report to file
    with open(f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md", "w") as f:
        f.write(report)
```

### 8. Automated Testing Suite

```python
import unittest
import psycopg2
from decimal import Decimal

class BridgePlatformTests(unittest.TestCase):
    def setUp(self):
        self.conn = psycopg2.connect("postgresql://user:pass@localhost:5432/bridge_db")
        self.cursor = self.conn.cursor()
    
    def test_member_uniqueness(self):
        """Test that member numbers are unique"""
        self.cursor.execute("SELECT number, COUNT(*) FROM players GROUP BY number HAVING COUNT(*) > 1")
        duplicates = self.cursor.fetchall()
        self.assertEqual(len(duplicates), 0, f"Found duplicate member numbers: {duplicates}")
    
    def test_masterpoints_non_negative(self):
        """Test that masterpoints are non-negative"""
        self.cursor.execute("SELECT COUNT(*) FROM masterpoints WHERE points < 0")
        negative_count = self.cursor.fetchone()[0]
        self.assertEqual(negative_count, 0, "Found negative masterpoints")
    
    def test_rating_system_consistency(self):
        """Test rating system calculations"""
        self.cursor.execute("""
            SELECT COUNT(*) FROM ratings 
            WHERE rating_type = 'openskill' 
            AND (mu < 0 OR sigma <= 0 OR sigma > 10)
        """)
        invalid_ratings = self.cursor.fetchone()[0]
        self.assertEqual(invalid_ratings, 0, "Found invalid rating values")
    
    def test_foreign_key_integrity(self):
        """Test foreign key relationships"""
        fk_tests = [
            ("masterpoints", "player_id", "players", "id"),
            ("masterpoints", "event_id", "events", "id"),
            ("results", "player_id", "players", "id"),
            ("results", "event_id", "events", "id")
        ]
        
        for table, fk_column, ref_table, ref_column in fk_tests:
            self.cursor.execute(f"""
                SELECT COUNT(*) FROM {table} t
                LEFT JOIN {ref_table} r ON t.{fk_column} = r.{ref_column}
                WHERE t.{fk_column} IS NOT NULL AND r.{ref_column} IS NULL
            """)
            orphaned_count = self.cursor.fetchone()[0]
            self.assertEqual(orphaned_count, 0, f"Found orphaned records in {table}.{fk_column}")
    
    def tearDown(self):
        self.conn.close()

if __name__ == '__main__':
    unittest.main()
```

## Validation Checklist

### Pre-Migration
- [ ] Run MySQL data quality checks
- [ ] Fix any data inconsistencies
- [ ] Backup all data
- [ ] Test migration scripts on sample data

### During Migration
- [ ] Monitor migration progress
- [ ] Validate each table as it's migrated
- [ ] Check foreign key relationships
- [ ] Verify data counts

### Post-Migration
- [ ] Run full validation suite
- [ ] Test application functionality
- [ ] Verify performance meets requirements
- [ ] Generate validation report

### Go-Live
- [ ] Run final validation
- [ ] Monitor system performance
- [ ] Have rollback plan ready
- [ ] Document any issues found

These validation scripts ensure your bridge platform migration maintains data integrity and performs correctly across all the sophisticated features in your current system.