import sys

from src.config.commands import Commands
from src.config.config_manager import SystemConfigManager
from src.config.logger import setup_logger

from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import QApplication

from src.ui.gui import JobTrackerWindow


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

if __name__ == '__main__' :
    config_manager = setup_config_manager()
    app = QApplication(sys.argv)
    window = JobTrackerWindow(config_manager=config_manager)
    window.show()
    sys.exit(app.exec())