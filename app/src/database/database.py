# app/src/database.py

from src.database.migration_worker import MigrationWorker

class Database:
    def __init__(self, config_manager) :
        self.logger = config_manager.logger

        self.migration_worker = MigrationWorker(config_manager, self)

 
    def run_migration(self) :
        return self.migration_worker.run_migration()
