"""
Data Schema Configurations for JobApplicationPipelineTracker.
Defines tables, data integrity rules, and hybrid JSON stores.
"""

CREATE_APPLICATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS watchlist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT NOT NULL,
    position_title TEXT NOT NULL,
    closing_date DATE NOT NULL,              -- Format: YYYY-MM-DD
    department TEXT,
    progress_state TEXT DEFAULT 'TODO',      -- 'TODO', 'Working on CV', 'Complete'
    required_documents TEXT NOT NULL,        -- Comma-separated: 'CV,Criteria,Degree'
    custom_metadata TEXT DEFAULT '{}',       -- Native JSON payload block for custom elements
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 🛡️ Data Integrity Guardian Layer
    -- Blocks accidental double-insertion of the same role closing on the same day.
    CONSTRAINT unique_job_instance UNIQUE (company, position_title, closing_date)
);
"""
