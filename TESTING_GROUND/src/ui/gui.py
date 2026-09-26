import sys
import os
import json
import sqlite3
from pathlib import Path
from PySide6.QtCore import Qt, QByteArray
from PySide6.QtWidgets import (
        QMainWindow, QWidget, QDockWidget, QListWidget
)
from PySide6.QtGui import QCloseEvent

from src.ui.layout import save_layout_state, load_layout_state
from src.ui.watchlist_dock import DockWatchlist

class JobTrackerWindow(QMainWindow):
    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        self.logger = config_manager.logger

        self.setWindowTitle("Job Application Pipeline Tracker Console")
        self.setObjectName("MainWindow")

        # 1. Initialize structural layout panels first so they exist in memory
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.init_dock_ui()
        # self.init_toolbar_ui()
        
        # 2. Extract and restore geometric layout vectors from JSON
        layout_data = load_layout_state(self.config_manager.config_path)
        if layout_data and "window_geometry" in layout_data and "window_state" in layout_data:
            # Reconstruct binary blocks from stored hex data strings
            geom_bytes = QByteArray.fromHex(layout_data["window_geometry"].encode("utf-8"))
            state_bytes = QByteArray.fromHex(layout_data["window_state"].encode("utf-8"))
            
            self.restoreGeometry(geom_bytes)
            self.restoreState(state_bytes)
            print("🔄 Dock layout sizes and window positions restored from config.json")
        else:
            # Fallback default dimensions if configuration is blank
            self.resize(1280, 800)

        # Connect the click event signal cleanly across your files
        self.dock_watchlist.watchlist_view.itemClicked.connect(self.dock_watchlist.handle_job_selection)
        
        # Run the initial data render on boot layer
        self.refresh_ui_data()

    def refresh_ui_data(self):
        """Fetches fresh data rows securely and passes them directly to the view."""
        active_rows = self.dock_watchlist.load_watchlist_from_database()
        self.dock_watchlist.populate_watchlist(active_rows)

    def init_dock_ui(self):
        self.dock_watchlist = DockWatchlist(config_manager=self.config_manager, parent=self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_watchlist)

    def closeEvent(self, event: QCloseEvent):
        """Intercepts application shutdown signals to cache layout metrics."""
        # Capture raw binary parameters representing panel positions and sizes
        geometry_bytes = self.saveGeometry()
        state_bytes = self.saveState()
        
        # Persist layout variables down to your configuration file
        save_layout_state(geometry_bytes=geometry_bytes, state_bytes=state_bytes, config_path=self.config_manager.config_path)
        print("Explicit window geometry and dock configurations cached successfully.")
        event.accept()