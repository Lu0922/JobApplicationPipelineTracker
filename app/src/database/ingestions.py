# app/src/database/ingestion.py

import sqlite3
import json

from src.config.commands import Commands

def insert_new_job(database_path, job: dict) -> Commands:
    # Context manager handles opening/closing connection perfectly
    with sqlite3.connect(database_path) as connection:
        cursor = connection.cursor()  # Safe cursor assignment
        
        try: 
            # 1. Corrected table name to 'watchlist' to match your schema
            cursor.execute("""
            INSERT INTO watchlist (
                company, position_title, closing_date, closing_time, department, progress_state, job_link, required_documents, custom_metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                job["company"],
                job["title"],
                job["date"],
                job["time"],
                job["dept"],
                job["state"],
                job["job_link"],
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