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
from src.ui.dock_watchlist import DockWatchlist
from src.ui.dock_dashboard import DockDashboard
from src.ui.dock_packaging import DockPackaging
from src.ui.dock_insertpanel import DockInsertPanel
from src.ui.dock_editpanel import DockEditPanel

class JobTrackerWindow(QMainWindow):
    def __init__(self, config_manager, database_engine):
        super().__init__()
        self.config_manager = config_manager
        self.logger = config_manager.logger
        self.database_engine = database_engine

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
        # 🔌 Route the custom signal straight to the query broker method
        self.dock_watchlist.job_selected.connect(self.route_data_to_dashboard)
        self.dock_dashboard.status_updated.connect(self.handle_database_status_mutation)
        self.dock_dashboard.delete_requested.connect(self.handle_database_deletion_request)
        self.dock_dashboard.edit_requested.connect(self.handle_database_update_request)
        self.dock_insertpanel.form_complete.connect(self.insert_new_job)
        

        # Run the initial data render on boot layer
        self.refresh_ui_data()

#   ================================================================================================
#   UI handling functions
#   ================================================================================================

    def refresh_ui_data(self):
        """Fetches fresh data rows securely and passes them directly to the view."""
        active_rows = self.database_engine.load_watchlist()
        self.dock_watchlist.populate_watchlist(active_rows)

    def init_dock_ui(self):
        self.dock_watchlist = DockWatchlist(config_manager=self.config_manager, parent=self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_watchlist)

        self.dock_dashboard = DockDashboard(config_manager=self.config_manager, parent=self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock_dashboard)

        self.dock_packaging = DockPackaging(config_manager=self.config_manager,parent=self)
        self.tabifyDockWidget(self.dock_dashboard, self.dock_packaging)

        self.dock_insertpanel = DockInsertPanel(config_manager=self.config_manager, parent=self)
        self.tabifyDockWidget(self.dock_packaging, self.dock_insertpanel)

        self.dock_editpanel = None

    def closeEvent(self, event: QCloseEvent):
        """Intercepts application shutdown signals to cache layout metrics."""
        # Capture raw binary parameters representing panel positions and sizes
        geometry_bytes = self.saveGeometry()
        state_bytes = self.saveState()
        
        # Persist layout variables down to your configuration file
        save_layout_state(geometry_bytes=geometry_bytes, state_bytes=state_bytes, config_path=self.config_manager.config_path)
        print("Explicit window geometry and dock configurations cached successfully.")
        event.accept()

#   ================================================================================================
#   Communication Between Docks
#   ================================================================================================
    def handle_database_status_mutation(self, job_id: int, new_status: str):
        # Securely invoke your secure query manager update transactions
        self.database_engine.update_status(job_id, new_status)
        # self.status_bar.showMessage(f"Pipeline database records successfully updated to: {new_status}")
        self.refresh_ui_data() # Trigger an immediate refresh loop on your watchlist item labels

    def handle_database_deletion_request(self, job_id: int):
        self.database_engine.delete_record(job_id)
        # self.status_bar.showMessage("Job tracking row purged cleanly from database system files.")
        self.refresh_ui_data()

    def handle_database_update_request(self, job_id: int):
        job_details = self.database_engine.get_job_by_id(job_id)

        # spawn the edit panel
        self.dock_editpanel = DockEditPanel(config_manager=self.config_manager, active_job_id=job_id, job_details=job_details)
        self.dock_editpanel.form_complete.connect(self.update_active_job)
        self.tabifyDockWidget(self.dock_packaging, self.dock_editpanel)

    def update_active_job(self, job_id: int, payload: dict) :
        self.database_engine.update_job_by_id(job_id=job_id, payload=payload)
        self.route_data_to_dashboard(job_id)

    def route_data_to_dashboard(self, job_id: int):
        job_details = self.database_engine.get_job_by_id(job_id)
        
        if job_details:
            self.dock_dashboard.render_job_profile(job_details)
            # Pipe active row dictionary contexts and runtime database counter metrics directly down into your packaging system!
            self.dock_packaging.update_job_context()

    def insert_new_job(self, payload: dict) :
        # from insert panel to database
        self.database_engine.insert_new_job(payload)
        self.refresh_ui_data() 