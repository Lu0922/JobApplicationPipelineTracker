# app/main.py
import sys

from src.config.config_manager import SystemConfigManager
from src.config.logger import setup_logger

from PySide6.QtWidgets import QApplication

from src.database.database import Database
from src.ui.gui import JobTrackerWindow

def setup_config_manager():
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

    logger.info(f"🚀 [Main] System: {system_name} Launching...")
    logger.debug(f"🔧 [Main] Configuration loaded: {config_manager.config_data}")

    return config_manager

if __name__ == '__main__' :
    config_manager = setup_config_manager()
    database_engine = Database(config_manager=config_manager)
    # database_engine.run_migration()

    app = QApplication(sys.argv)
    window = JobTrackerWindow(config_manager=config_manager, database_engine=database_engine)
    window.show()
    sys.exit(app.exec())



    # live_pipeline_seeds = [
    #     {
    #         "company": "Department of Communities",
    #         "title": "Support Officer",
    #         "date": "2026-09-25",
    #         "time": "16:00",
    #         "dept": "Technology Branch",
    #         "state": "Complete",
    #         "job_link": "FAKE_LINK",
    #         "docs": "CV,Selection Criteria,Degree",
    #         "meta": {"reference_number": "006408", "interviewer": "Virginia Ting"}
    #     },
    #     {
    #         "company": "Department of Justice",
    #         "title": "Information Release Support Officer",
    #         "date": "2026-09-28",
    #         "time": "16:00",
    #         "dept": "Knowledge Information & Technology",
    #         "state": "Working on CV",
    #         "job_link": "FAKE_LINK",
    #         "docs": "CV,Referees",
    #         "meta": {"reference_number": "DOJ-2026-IR", "term_months": 6}
    #     }
    # ]
    # for job in live_pipeline_seeds :
    #     database_engine.insert_new_job(job=job)