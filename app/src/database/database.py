# app/src/database.py

from src.config.commands import Commands
from src.database.migration import run_migrations
from src.database.ingestions import insert_new_job
from src.database.query import (
        load_watchlist, get_job_by_id, update_status, delete_record,
        update_job_by_id   
)

class Database:
    def __init__(self, config_manager) :
        self.config_manager = config_manager
        self.logger = config_manager.logger
        self.database_path = config_manager.database_path

    def run_migration(self) -> Commands:
        return run_migrations(config_manager=self.config_manager)

    def insert_new_job(self, job) -> Commands:
        return insert_new_job(database_path=self.database_path, job=job)

    def load_watchlist(self) -> dict:
        return load_watchlist(database_path=self.database_path)

    def get_job_by_id(self, job_id) -> dict:
        return get_job_by_id(database_path=self.database_path, job_id=job_id)

    def update_status(self, job_id, new_status) -> Commands:
        return update_status(database_path=self.database_path, job_id=job_id, new_status=new_status)

    def update_job_by_id(self, job_id: int, payload: dict) :
        return update_job_by_id(database_path=self.database_path, job_id=job_id, payload=payload)

    def delete_record(self, job_id) -> Commands:
        return delete_record(database_path=self.database_path, job_id=job_id)