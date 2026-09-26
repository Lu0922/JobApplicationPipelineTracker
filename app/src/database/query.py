import sqlite3

def load_watchlist(config_manager) -> dict:
    with sqlite3.connect(config_manager.database_path) as connection :
        cursor = connection.cursor()

        query = """
                SELECT id, company, position_title, closing_date, progress_state
                FROM watchlist 
                ORDER BY closing_date ASC;
                """ 
        
        cursor.execute(query)
        return cursor.fetchall()