-- 0001_add_application_type_to_watchlist.sql

-- 1. Create a migration transaction block to guarantee schema safety
BEGIN TRANSACTION;

-- 2. Inject the new structured application_type field with a strict constraint check
ALTER TABLE watchlist 
ADD COLUMN application_type TEXT NOT NULL DEFAULT 'SINGLE'
CHECK (application_type IN ('SINGLE', 'POOL', 'REGISTER'));

COMMIT;
