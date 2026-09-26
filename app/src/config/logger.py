import logging
import sys
import os
from pathlib import Path

def setup_logger(name: str, log_filename: str = "app.log", level_str: str = "INFO") -> logging.Logger:
    """Generates a standardized system tracking logger with dynamic level filtering."""
    logger = logging.getLogger(name)
    
    # If the logger has already been configured in this thread space, return it directly
    if logger.handlers:
        return logger
        
    # Map configuration strings to explicit Python logging levels natively
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    target_level = level_map.get(level_str.upper().strip(), os.getenv("LOG_LEVEL", "INFO").upper())
    logger.setLevel(target_level)
    
    # Define our universal cockpit formatting layout blueprint
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] (%(filename)s:%(lineno)d) ──► %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # 🖥️ Console Terminal Stream Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(target_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 💾 Local Persistent Disk File Handler
    log_dir = Path(__file__).resolve().parents[2] / "logs"
    log_dir.mkdir(exist_ok=True)
    
    file_handler = logging.FileHandler(log_dir / log_filename, encoding="utf-8")
    file_handler.setLevel(target_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger
