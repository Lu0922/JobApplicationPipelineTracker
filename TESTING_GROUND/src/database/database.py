# app/src/database.py

from src.config.commands import Commands
from src.database.migration import run_migrations
from src.database.ingestions import inject_new_job

class Database:
    def __init__(self, config_manager) :
        self.config_manager = config_manager
        self.logger = config_manager.logger

    def run_migration(self) -> Commands:
        return run_migrations(config_manager=self.config_manager)

    def inject_new_job(self) -> Commands:
        return inject_new_job(config_manager=self.config_manager)