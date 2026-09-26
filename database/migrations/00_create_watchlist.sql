-- Data Schema Configurations for JobApplicationPipelineTracker.
-- Defines tables, data integrity rules, and hybrid JSON stores.

CREATE TABLE IF NOT EXISTS watchlist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT NOT NULL,
    position_title TEXT NOT NULL,
    closing_date DATE NOT NULL,              
    department TEXT,
    job_link TEXT NOT NULL,
    progress_state TEXT DEFAULT 'TODO',      
    required_documents TEXT NOT NULL,        
    custom_metadata TEXT DEFAULT '{}',       
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_job_instance UNIQUE (company, position_title, closing_date)
);
