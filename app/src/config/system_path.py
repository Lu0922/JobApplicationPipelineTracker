"""
config.py
Central Configuration Manager for the Application Pipeline.
Establishes system root paths and handles global application properties.
"""
from pathlib import Path

# 1. Establish the absolute base anchor point of the project source code
# Anchored to: JobApplicationPipelineTracker/app/src/
SRC_DIR = Path(__file__).resolve().parent

# 2. Derive the True Project Root Directory: JobApplicationPipelineTracker/
PROJECT_ROOT = SRC_DIR.parents[1]

# 3. Structural Data Paths (Decoupled from code execution context)
DATABASE_DIR = PROJECT_ROOT / "database"
MIGRATIONS_DIR = DATABASE_DIR / "migrations"

# 4. Global Constant File Outputs
DB_PATH = DATABASE_DIR / "watchlist.db"
SCHEMA_PATH = MIGRATIONS_DIR / "watchlist.sql"

# 5. Local File Packaging Constants (Your custom specification layout)
SOURCE_QUALIFICATIONS_DIR = PROJECT_ROOT / "assets" / "master_docs"
TARGET_OUTPUT_DIR = PROJECT_ROOT / "applications_export"

# Enforce target directory existence on boot layer
DATABASE_DIR.mkdir(parents=True, exist_ok=True)
MIGRATIONS_DIR.mkdir(parents=True, exist_ok=True)
