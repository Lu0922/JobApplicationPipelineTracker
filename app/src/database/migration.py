# app/src/database/migration.py

import sqlite3

from pathlib import Path

from src.config.commands import Commands

def _read_migrations_directory(migrations_directory: str) -> list[str] :
    files = [f.name for f in Path(migrations_directory).iterdir() if f.is_file]
    return files

def run_migrations(config_manager) -> Commands:
    path = config_manager.database_path

    sql_files = _read_migrations_directory(migrations_directory=config_manager.migrations_directory)
    
    try:
        # Open one single connection for the entire batch of migrations
        with sqlite3.connect(path) as connection:
            for file in sql_files:
                file_path = config_manager.migrations_directory / file
                
                with open(file_path, "r", encoding="utf-8") as f:
                    sql_script = f.read()
                    
                # Run the migration using the active connection
                connection.executescript(sql_script)
                
        return Commands.SUCCESS # All migrations succeeded and were committed cleanly
        
    except (sqlite3.Error, OSError) as e:
        print(f"❌ DATABASE MIGRATION CRITICAL BUG: {e}")
        return Commands.FAIL # Something failed, entire transaction was rolled back


# def load_schema_and_connect(database_directory: str):
#     # Verify the migration script can locate your schema architecture
#     if not database_directory.exists():
#         raise FileNotFoundError(f"❌ Cannot locate schema file at: {SQL_SCHEMA_FILE}")
        
#     print(f"✅ Found SQL Schema: {SQL_SCHEMA_FILE.name}")
#     print(f"📦 Target Database Set: {DB_FILE}")
    
#     # Read the raw .sql script file
#     with open(SQL_SCHEMA_FILE, "r") as f:
#         sql_script = f.read()
        
#     # Connect to the DB (SQLite will automatically generate the file if missing)
#     connection = sqlite3.connect(str(DB_FILE))
#     return connection, sql_script

# def run_migrations():
#     """
#     Executes database schema builds and handles data migration/seeding.
#     """
#     print("=" * 60)
#     print("🚀 INITIALISING PIPELINE DATABASE MIGRATION WORKER")
#     print("=" * 60)
    
#     # Connect to embedded engine file
#     connection = sqlite3.connect(DB_FILE)
#     cursor = connection.cursor()
    
#     try:
#         # 1. Enforce database schema definitions
#         cursor.execute(CREATE_APPLICATIONS_TABLE)
#         connection.commit()
#         print("📁 System Architecture Verification: 'applications' table is secure.")
        
#     except sqlite3.Error as e:
#         print(f"❌ DATABASE MIGRATION CRITICAL BUG: {e}")
#         connection.close()
#         return

#     # 2. Package your active pipeline targets as production seed payloads
#     live_pipeline_seeds = [
#         {
#             "company": "Department of Communities",
#             "title": "Support Officer",
#             "date": "2026-09-25",
#             "dept": "Technology Branch",
#             "state": "Complete",
#             "docs": "CV,Selection Criteria,Degree",
#             "meta": {"reference_number": "006408", "interviewer": "Virginia Ting"}
#         },
#         {
#             "company": "Department of Justice",
#             "title": "Information Release Support Officer",
#             "date": "2026-09-28",
#             "dept": "Knowledge Information & Technology",
#             "state": "Working on CV",
#             "docs": "CV,Referees",
#             "meta": {"reference_number": "DOJ-2026-IR", "term_months": 6}
#         }
#     ]

#     # 3. Securely ingest seed data via parametrized queries
#     seeded_count = 0
#     skipped_count = 0
    
#     for job in live_pipeline_seeds:
#         try:
#             cursor.execute("""
#             INSERT INTO applications (
#                 company, position_title, closing_date, department, progress_state, required_documents, custom_metadata
#             ) VALUES (?, ?, ?, ?, ?, ?, ?);
#             """, (
#                 job["company"],
#                 job["title"],
#                 job["date"],
#                 job["dept"],
#                 job["state"],
#                 job["docs"],
#                 json.dumps(job["meta"])  # Serialises dictionary to valid JSON string text
#             ))
#             print(f"   ↳ Ingested: {job['title']} -> {job['company']}")
#             seeded_count += 1
#         except sqlite3.IntegrityError:
#             # Capturing this proof signals your relational integrity constraints are functioning perfectly!
#             print(f"   ↳ Integrity Guard Active: Skipped existing record ({job['title']} @ {job['company']})")
#             skipped_count += 1

#     connection.commit()
#     connection.close()
    
#     print("-" * 60)
#     print(f"🏁 MIGRATION RUN COMPLETE. Seeded: {seeded_count} | Preserved: {skipped_count}")
#     print("=" * 60)