-- PostgreSQL 16 Database Initialization Script
-- This script sets up the initial database, user, and permissions for Josi

-- Create the database user if it doesn't exist
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'josi'
   ) THEN
      CREATE ROLE josi WITH LOGIN PASSWORD 'josi';
   END IF;
END
$do$;

-- Grant necessary permissions
ALTER ROLE josi CREATEDB;

-- Create the database if it doesn't exist
SELECT 'CREATE DATABASE josi OWNER josi'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'josi')\gexec

-- Connect to the josi database
\c josi;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- For text search

-- Grant all privileges on the database to the josi user
GRANT ALL PRIVILEGES ON DATABASE josi TO josi;

-- Create schema if needed
CREATE SCHEMA IF NOT EXISTS josi AUTHORIZATION josi;

-- Set default search path
ALTER DATABASE josi SET search_path TO josi, public;

-- Grant usage on schema
GRANT USAGE ON SCHEMA josi TO josi;
GRANT CREATE ON SCHEMA josi TO josi;

-- Grant permissions on all tables (for future tables)
ALTER DEFAULT PRIVILEGES IN SCHEMA josi 
    GRANT ALL PRIVILEGES ON TABLES TO josi;
ALTER DEFAULT PRIVILEGES IN SCHEMA josi 
    GRANT ALL PRIVILEGES ON SEQUENCES TO josi;
ALTER DEFAULT PRIVILEGES IN SCHEMA josi 
    GRANT ALL PRIVILEGES ON FUNCTIONS TO josi;

-- Create a function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create indexes on common query patterns (will be created after tables exist)
-- These are comments for reference when tables are created by Alembic
-- CREATE INDEX idx_person_organization_id ON person(organization_id) WHERE is_deleted = false;
-- CREATE INDEX idx_person_email ON person(email) WHERE is_deleted = false;
-- CREATE INDEX idx_astrology_chart_person_id ON astrology_chart(person_id) WHERE is_deleted = false;
-- CREATE INDEX idx_astrology_chart_type ON astrology_chart(chart_type) WHERE is_deleted = false;

-- Performance settings for PostgreSQL 16
-- Note: shared_buffers and max_connections must be set in postgresql.conf or via command line
-- These are session-level settings that can be changed per database
ALTER DATABASE josi SET work_mem = '4MB';
ALTER DATABASE josi SET maintenance_work_mem = '64MB';

-- Log slow queries
ALTER DATABASE josi SET log_min_duration_statement = '1000'; -- Log queries slower than 1 second

-- Set timezone to UTC
ALTER DATABASE josi SET timezone = 'UTC';

-- Vacuum and analyze settings for better performance
-- Note: autovacuum is enabled by default in PostgreSQL
-- These settings can be adjusted per table if needed

-- Create a dedicated schema for cache invalidation tracking
CREATE SCHEMA IF NOT EXISTS cache_invalidation;

-- Table to track which cache keys are associated with which database records
CREATE TABLE IF NOT EXISTS cache_invalidation.cache_dependencies (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    cache_key VARCHAR(500) NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    record_id UUID NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(cache_key, table_name, record_id)
);

-- Index for fast lookups
CREATE INDEX idx_cache_deps_table_record 
    ON cache_invalidation.cache_dependencies(table_name, record_id);
CREATE INDEX idx_cache_deps_key 
    ON cache_invalidation.cache_dependencies(cache_key);

-- Grant permissions on cache schema
GRANT ALL ON SCHEMA cache_invalidation TO josi;
GRANT ALL ON ALL TABLES IN SCHEMA cache_invalidation TO josi;

-- Notify about successful initialization
DO $$
BEGIN
    RAISE NOTICE 'Josi database initialized successfully';
    RAISE NOTICE 'Database: josi';
    RAISE NOTICE 'User: josi';
    RAISE NOTICE 'Extensions enabled: uuid-ossp, pgcrypto, pg_trgm';
    RAISE NOTICE 'Cache invalidation schema created';
END $$;