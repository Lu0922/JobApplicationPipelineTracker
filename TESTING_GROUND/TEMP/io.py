import sqlite3
import json

from pathlib import Path

from src.config.config_manager import SystemConfigManager
from src.config.logger import setup_logger

def setup_config_manager() :
    config_path = "json/config.json"

    # 1. Mount config parameters silently (The chicken comes first!)
    config_manager = SystemConfigManager(config_path=config_path)
    
    # 2. Extract your target logging parameters safely from the loaded config
    log_level = config_manager.get("logging", "level", "INFO")
    log_file = config_manager.get("logging", "filename")

    # 3. Instantiate your beautiful universal logger module
    system_name = config_manager.get("config", "system_name")
    logger = setup_logger(name=system_name, log_filename=log_file, level_str=log_level)
    
    # 4. Inject the active logger back into the config manager to close the loop!
    config_manager.set_logger(logger)

    logger.info(f"🚀 [Main] System: {system_name} I/O testing...")
    # logger.debug(f"🔧 [Main] Configuration loaded: {config_manager.config_data}")

    return config_manager

def _read_migrations_directory(migrations_directory: str) -> list[str] :
    files = [f.name for f in Path(migrations_directory).iterdir() if f.is_file]
    return files

def run_migrations(config_manager) -> bool:
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
                
        return True # All migrations succeeded and were committed cleanly
        
    except (sqlite3.Error, OSError) as e:
        print(f"❌ DATABASE MIGRATION CRITICAL BUG: {e}")
        return False # Something failed, entire transaction was rolled back

def inject_new_job(config_manager, job: dict):
    # Context manager handles opening/closing connection perfectly
    with sqlite3.connect(config_manager.database_path) as connection:
        cursor = connection.cursor()  # Safe cursor assignment
        
        try: 
            # 1. Corrected table name to 'watchlist' to match your schema
            cursor.execute("""
            INSERT INTO watchlist (
                company, position_title, closing_date, department, progress_state, required_documents, custom_metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?);
            """, (
                job["company"],
                job["title"],
                job["date"],
                job["dept"],
                job["state"],
                job["docs"],
                json.dumps(job["meta"])  # Serialises dictionary to valid JSON string text
            ))
            
            # Explicit commit preserves stability
            connection.commit()
            print(f"   ↳ Ingested: {job['title']} -> {job['company']}")
            
        except sqlite3.IntegrityError:
            # Capturing this proof signals your relational integrity constraints are functioning perfectly!
            print(f"   ↳ Integrity Guard Active: Skipped existing record ({job['title']} @ {job['company']})")
        finally:
            cursor.close() # Clean resource disposal

if __name__ == "__main__" :
    config_manager = setup_config_manager()
    run_migrations(config_manager=config_manager)

    live_pipeline_seeds = [
        {
            "company": "Department of Communities",
            "title": "Support Officer",
            "date": "2026-09-25",
            "dept": "Technology Branch",
            "state": "Complete",
            "docs": "CV,Selection Criteria,Degree",
            "meta": {"reference_number": "006408", "interviewer": "Virginia Ting"}
        },
        {
            "company": "Department of Justice",
            "title": "Information Release Support Officer",
            "date": "2026-09-28",
            "dept": "Knowledge Information & Technology",
            "state": "Working on CV",
            "docs": "CV,Referees",
            "meta": {"reference_number": "DOJ-2026-IR", "term_months": 6}
        }
    ]

    for job in live_pipeline_seeds :
        inject_new_job(config_manager=config_manager, job=job)