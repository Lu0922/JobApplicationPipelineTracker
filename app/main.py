# app/main.py

from src.config.config_manager import SystemConfigManager
from src.config.logger import setup_logger

def main():
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

if __name__ == '__main__' :
    main()