# app/src/database/ingestion.py

import sqlite3
import json

from src.config.commands import Commands

def inject_new_job(config_manager, job: dict) -> Commands:
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
            return Commands.SUCCESS
            
        except sqlite3.IntegrityError:
            # Capturing this proof signals your relational integrity constraints are functioning perfectly!
            print(f"   ↳ Integrity Guard Active: Skipped existing record ({job['title']} @ {job['company']})")
            return Commands.FAIL
        finally:
            cursor.close() # Clean resource disposal