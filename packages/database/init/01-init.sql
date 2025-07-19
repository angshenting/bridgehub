-- Database initialization script
-- This runs automatically when the Docker container starts

-- Create the database if it doesn't exist
-- (This is handled by the POSTGRES_DB environment variable)

-- Connect to the database
\c bridge_platform_dev;

-- Run the schema
\i /docker-entrypoint-initdb.d/schema.sql