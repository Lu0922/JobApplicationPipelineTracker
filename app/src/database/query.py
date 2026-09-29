import sqlite3
import json

from src.config.commands import Commands

def load_watchlist(database_path) -> dict:
    with sqlite3.connect(database_path) as connection :
        cursor = connection.cursor()

        query = """
                SELECT id, company, position_title, closing_date, closing_time, progress_state
                FROM watchlist 
                ORDER BY closing_date ASC;
                """ 
        
        cursor.execute(query)
        return cursor.fetchall()

def get_job_by_id(database_path: str, job_id: int) -> dict | None:
    """Safely extracts a complete application data map using a targeted ID."""
    query = """
            SELECT id, company, position_title, closing_date, closing_time, department, job_link, progress_state, required_documents, custom_metadata
            FROM watchlist
            WHERE id = ?;
            """
    try:
        with sqlite3.connect(database_path) as connection:
            # Configure row factory to access columns by string name keys cleanly
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            
            cursor.execute(query, (job_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
                
            # Parse row keys dynamically into your PySide6 dashboard dictionary format
            return {
                "id": row["id"],
                "company": row["company"],
                "title": row["position_title"],
                "closing_date": row["closing_date"],
                "closing_time": row["closing_time"],
                "job_link": row["job_link"],
                "department": row["department"],
                "status": row["progress_state"],
                "documents": [d.strip() for d in row["required_documents"].split(",") if d.strip()],
                "metadata": json.loads(row["custom_metadata"]) if row["custom_metadata"] else {}
            }
    except (sqlite3.Error, json.JSONDecodeError) as e:
        print(f"🚨 Read Query Failure: {e}")
        return None

def update_status(database_path: str, job_id: int, new_status: str) -> Commands:
    """Updates the pipeline stage string of a specific row context safely."""
    query = """
            UPDATE watchlist
            SET progress_state = ? 
            WHERE id = ?;
            """
    try:
        with sqlite3.connect(database_path) as connection:
            cursor = connection.cursor()
            cursor.execute(query, (new_status, job_id))
            connection.commit()
            return Commands.SUCCESS
    except sqlite3.Error as e:
        print(f"🚨 Write Query Failure: {e}")
        return Commands.FAILURE

def delete_record(database_path:str, job_id: int) -> Commands:
    """
    Permanently purges a specific application row from the sqlite database layer.
    Utilises strict parameter binding to block malicious SQL injection vectors.
    """
    query = """
            DELETE FROM watchlist 
            WHERE id = ?;
            """
    try:
        with sqlite3.connect(database_path) as connection:
            cursor = connection.cursor()
            
            # Execute the parameterized delete transaction
            cursor.execute(query, (job_id,))
            connection.commit()
            
            # Verify if a row was actually found and deleted
            if cursor.rowcount > 0:
                print(f"🗑️ Database Record ID {job_id} successfully purged from local storage data layers.")
                return Commands.SUCCESS
            else:
                print(f"⚠️ Warning: Purge operation triggered on non-existent Record ID {job_id}.")
                return Commands.FAILURE
                
    except sqlite3.Error as e:
        print(f"🚨 Critical write transactional failure during deletion execution loop: {e}")
        return Commands.FAILURE

def update_job_by_id(database_path: str, job_id: int, payload: dict) :
    with sqlite3.connect(database_path) as connection:
            cursor = connection.cursor()  # Safe cursor assignment
            
            try: 
                # 1. Removed trailing comma and fixed SET syntax
                query = """
                        UPDATE watchlist
                        SET company = ?,
                            position_title = ?,
                            closing_date = ?,
                            closing_time = ?,
                            department = ?,
                            job_link = ?,
                            required_documents = ?,
                            custom_metadata = ?
                        WHERE id = ?;
                        """
                
                cursor.execute(query, (
                    payload["company"],
                    payload["title"],
                    payload["date"],
                    payload["time"],
                    payload["dept"],
                    payload["job_link"],
                    payload["docs"],
                    json.dumps(payload["meta"]),
                    job_id
                ))
                
                # Explicit commit preserves stability
                connection.commit()
                print(f"   ↳ Updated: {payload['title']} -> {payload['company']}")
                return Commands.SUCCESS
                
            except sqlite3.IntegrityError:
                # Capturing this proof signals your relational integrity constraints are functioning perfectly!
                print(f"   ↳ Integrity Guard Active: Skipped existing record ({payload['title']} @ {payload['company']})")
                return Commands.FAIL
            finally:
                cursor.close() # Clean resource disposal