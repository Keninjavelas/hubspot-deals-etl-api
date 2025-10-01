-- File: docker/initdb/init.sql

-- Creates the 'deals' table only if it doesn't already exist
CREATE TABLE IF NOT EXISTS deals (
    id BIGINT PRIMARY KEY,
    dealname TEXT,
    amount NUMERIC,
    pipeline TEXT,
    dealstage TEXT,
    createdate TIMESTAMPTZ,
    hs_lastmodifieddate TIMESTAMPTZ,
    closedate TIMESTAMPTZ,
    deal_owner_id TEXT,
    properties JSONB
);

-- Creates indexes only if they don't already exist
CREATE INDEX IF NOT EXISTS idx_deals_last_modified ON deals (hs_lastmodifieddate);
CREATE INDEX IF NOT EXISTS idx_deals_owner ON deals (deal_owner_id);