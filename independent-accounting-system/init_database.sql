-- ============================================
-- NERDX Independent Accounting System
-- PostgreSQL Database Schema
-- Version: 1.0
-- Created: 2025-10-25
-- ============================================

-- Create database (run as postgres superuser)
-- CREATE DATABASE nerdx_accounting;
-- CREATE USER nerdx_user WITH PASSWORD 'CHANGE_THIS_PASSWORD';
-- GRANT ALL PRIVILEGES ON DATABASE nerdx_accounting TO nerdx_user;

-- Connect to the database
-- \c nerdx_accounting

-- ============================================
-- Extensions
-- ============================================

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pgvector for AI embeddings (optional)
CREATE EXTENSION IF NOT EXISTS vector;

-- Enable pg_trgm for text search
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- ============================================
-- Enum Types
-- ============================================

CREATE TYPE cell_status AS ENUM ('active', 'inactive', 'archived');
CREATE TYPE cell_type AS ENUM ('product', 'service', 'support', 'sales', 'marketing', 'other');

-- ============================================
-- Tables
-- ============================================

-- Cells (Independent Business Units)
CREATE TABLE cells (
    cell_id VARCHAR(50) PRIMARY KEY,
    cell_name VARCHAR(200) NOT NULL,
    cell_type cell_type DEFAULT 'other',
    status cell_status DEFAULT 'active',
    manager_name VARCHAR(100),
    manager_email VARCHAR(200) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Metadata
    description TEXT,
    tags TEXT[],
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Constraints
    CONSTRAINT cell_email_valid CHECK (manager_email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- Revenue Records (from Salesforce CRM)
CREATE TABLE revenue_records (
    revenue_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cell_id VARCHAR(50) NOT NULL REFERENCES cells(cell_id) ON DELETE CASCADE,
    revenue_date DATE NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'KRW',
    source VARCHAR(100) DEFAULT 'Salesforce CRM',

    -- Salesforce Fields
    salesforce_opportunity_id VARCHAR(18),
    salesforce_account_id VARCHAR(18),
    opportunity_name VARCHAR(200),
    stage VARCHAR(50),

    -- Metadata
    description TEXT,
    tags TEXT[],
    metadata JSONB DEFAULT '{}'::jsonb,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT revenue_amount_positive CHECK (amount >= 0)
);

-- Cost Records (from Odoo ERP)
CREATE TABLE cost_records (
    cost_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cell_id VARCHAR(50) NOT NULL REFERENCES cells(cell_id) ON DELETE CASCADE,
    cost_date DATE NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'KRW',
    category VARCHAR(100) DEFAULT 'operational',
    source VARCHAR(100) DEFAULT 'Odoo ERP',

    -- Odoo Fields
    odoo_invoice_id VARCHAR(50),
    odoo_analytic_account_id VARCHAR(50),
    vendor_name VARCHAR(200),
    invoice_number VARCHAR(100),

    -- Metadata
    description TEXT,
    tags TEXT[],
    metadata JSONB DEFAULT '{}'::jsonb,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT cost_amount_positive CHECK (amount >= 0)
);

-- Daily Financial Summaries
CREATE TABLE daily_financial_summaries (
    summary_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cell_id VARCHAR(50) NOT NULL REFERENCES cells(cell_id) ON DELETE CASCADE,
    summary_date DATE NOT NULL,

    -- Financial Metrics
    total_revenue DECIMAL(15, 2) DEFAULT 0,
    total_cost DECIMAL(15, 2) DEFAULT 0,
    gross_profit DECIMAL(15, 2) GENERATED ALWAYS AS (total_revenue - total_cost) STORED,
    gross_profit_margin DECIMAL(5, 4) GENERATED ALWAYS AS (
        CASE
            WHEN total_revenue > 0 THEN (total_revenue - total_cost) / total_revenue
            ELSE 0
        END
    ) STORED,

    -- Counts
    revenue_count INTEGER DEFAULT 0,
    cost_count INTEGER DEFAULT 0,

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Unique constraint
    UNIQUE(cell_id, summary_date)
);

-- Daily Reports (Generated HTML/Email)
CREATE TABLE daily_reports (
    report_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cell_id VARCHAR(50) NOT NULL REFERENCES cells(cell_id) ON DELETE CASCADE,
    report_date DATE NOT NULL,

    -- Report Content
    html_content TEXT,
    email_subject VARCHAR(200),
    email_sent BOOLEAN DEFAULT FALSE,
    email_sent_at TIMESTAMP,

    -- Report Metadata
    generation_time_ms INTEGER,
    file_path VARCHAR(500),

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Unique constraint
    UNIQUE(cell_id, report_date)
);

-- Cell Embeddings (AI/ML - Optional)
CREATE TABLE cell_embeddings (
    embedding_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cell_id VARCHAR(50) NOT NULL REFERENCES cells(cell_id) ON DELETE CASCADE,
    report_date DATE NOT NULL,

    -- Vector Embedding (OpenAI ada-002: 1536 dimensions)
    embedding vector(1536),

    -- Source
    source_type VARCHAR(50) DEFAULT 'daily_report',
    source_text TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Index for fast similarity search
    UNIQUE(cell_id, report_date, source_type)
);

-- ============================================
-- Indexes
-- ============================================

-- Cells
CREATE INDEX idx_cells_status ON cells(status);
CREATE INDEX idx_cells_manager_email ON cells(manager_email);
CREATE INDEX idx_cells_created_at ON cells(created_at DESC);

-- Revenue Records
CREATE INDEX idx_revenue_cell_date ON revenue_records(cell_id, revenue_date DESC);
CREATE INDEX idx_revenue_date ON revenue_records(revenue_date DESC);
CREATE INDEX idx_revenue_salesforce_opp ON revenue_records(salesforce_opportunity_id);
CREATE INDEX idx_revenue_created_at ON revenue_records(created_at DESC);

-- Cost Records
CREATE INDEX idx_cost_cell_date ON cost_records(cell_id, cost_date DESC);
CREATE INDEX idx_cost_date ON cost_records(cost_date DESC);
CREATE INDEX idx_cost_category ON cost_records(category);
CREATE INDEX idx_cost_created_at ON cost_records(created_at DESC);

-- Daily Financial Summaries
CREATE INDEX idx_summary_date ON daily_financial_summaries(summary_date DESC);
CREATE INDEX idx_summary_cell_date ON daily_financial_summaries(cell_id, summary_date DESC);
CREATE INDEX idx_summary_created_at ON daily_financial_summaries(created_at DESC);

-- Daily Reports
CREATE INDEX idx_reports_date ON daily_reports(report_date DESC);
CREATE INDEX idx_reports_cell_date ON daily_reports(cell_id, report_date DESC);
CREATE INDEX idx_reports_email_sent ON daily_reports(email_sent, report_date);

-- Cell Embeddings (HNSW for fast vector search)
CREATE INDEX ON cell_embeddings USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- ============================================
-- Functions & Triggers
-- ============================================

-- Update updated_at timestamp automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to tables
CREATE TRIGGER update_cells_updated_at BEFORE UPDATE ON cells
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_revenue_updated_at BEFORE UPDATE ON revenue_records
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_cost_updated_at BEFORE UPDATE ON cost_records
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_summary_updated_at BEFORE UPDATE ON daily_financial_summaries
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Views
-- ============================================

-- Active Cells Summary
CREATE OR REPLACE VIEW v_active_cells_summary AS
SELECT
    c.cell_id,
    c.cell_name,
    c.cell_type,
    c.manager_name,
    c.manager_email,
    COUNT(DISTINCT r.revenue_id) as revenue_count,
    COUNT(DISTINCT co.cost_id) as cost_count,
    COALESCE(SUM(r.amount), 0) as total_revenue,
    COALESCE(SUM(co.amount), 0) as total_cost,
    COALESCE(SUM(r.amount), 0) - COALESCE(SUM(co.amount), 0) as gross_profit
FROM cells c
LEFT JOIN revenue_records r ON c.cell_id = r.cell_id
LEFT JOIN cost_records co ON c.cell_id = co.cell_id
WHERE c.status = 'active'
GROUP BY c.cell_id, c.cell_name, c.cell_type, c.manager_name, c.manager_email;

-- Recent Daily Summaries (Last 30 Days)
CREATE OR REPLACE VIEW v_recent_daily_summaries AS
SELECT
    c.cell_name,
    dfs.*
FROM daily_financial_summaries dfs
JOIN cells c ON dfs.cell_id = c.cell_id
WHERE dfs.summary_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY dfs.summary_date DESC, c.cell_name;

-- ============================================
-- Sample Data (for testing)
-- ============================================

-- Insert sample cells
INSERT INTO cells (cell_id, cell_name, cell_type, manager_name, manager_email, description)
VALUES
    ('CELL-001', 'Product Development Team', 'product', 'John Doe', 'john.doe@nerdx.com', 'Core product development and R&D'),
    ('CELL-002', 'Marketing Operations', 'marketing', 'Jane Smith', 'jane.smith@nerdx.com', 'Marketing campaigns and brand management'),
    ('CELL-003', 'Sales Team Korea', 'sales', 'Kim Min-jun', 'minjun.kim@nerdx.com', 'B2B sales and customer acquisition')
ON CONFLICT (cell_id) DO NOTHING;

-- ============================================
-- Grants
-- ============================================

-- Grant permissions to application user
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO nerdx_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO nerdx_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO nerdx_user;

-- ============================================
-- Database Statistics
-- ============================================

-- Vacuum and analyze
VACUUM ANALYZE;

-- Display table sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- ============================================
-- Notes
-- ============================================

/*
To initialize the database:
1. Create database and user:
   sudo -u postgres psql
   CREATE DATABASE nerdx_accounting;
   CREATE USER nerdx_user WITH PASSWORD 'your_secure_password';
   GRANT ALL PRIVILEGES ON DATABASE nerdx_accounting TO nerdx_user;

2. Run this script:
   psql -U nerdx_user -d nerdx_accounting -f init_database.sql

3. Verify:
   psql -U nerdx_user -d nerdx_accounting
   \dt  -- List tables
   \dv  -- List views
   SELECT * FROM v_active_cells_summary;

4. Backup:
   pg_dump -U nerdx_user nerdx_accounting > backup_$(date +%Y%m%d).sql

5. Restore:
   psql -U nerdx_user -d nerdx_accounting < backup_YYYYMMDD.sql
*/
