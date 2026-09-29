# app/src/gui/dashboard_dock.py
import json
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QComboBox, QPushButton, QCheckBox, QMessageBox
)

class DockDashboard(QDockWidget):
    # 📡 Signals emitted to inform the main window controller of database mutation requests
    status_updated = Signal(int, str)  # Emits: (job_id, new_status_string)
    delete_requested = Signal(int)     # Emits: (job_id)
    edit_requested = Signal(int)

    def __init__(self, config_manager, parent=None):
        super().__init__("Application Details Dashboard", parent)
        self.config_manager = config_manager
        self.logger = config_manager.logger
        self.parent = parent
        self.setAllowedAreas(Qt.RightDockWidgetArea)
        self.setObjectName("DashBoardDock")
        
        # Track the active primary key runtime context locally
        self.active_job_id = None
        
        # 🧪 Construct the Visual Layout Tree
        self.init_ui()

    def init_ui(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(20)
        
        # 1. Header Information Layer
        self.lbl_title = QLabel("Select an application from the watchlist...")
        self.lbl_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #4F46E5;")
        self.lbl_title.setWordWrap(True)
        layout.addWidget(self.lbl_title)
        
        # 2. Text Descriptive Metadata Display
        self.lbl_meta = QLabel("Metadata tracking profiles will populate here.")
        self.lbl_meta.setStyleSheet("font-size: 14px; color: #FFFFFF;")
        self.lbl_meta.setWordWrap(True)
        layout.addWidget(self.lbl_meta)
        
        # 3. Dynamic Document Verification Checklist Canvas
        self.lbl_check_header = QLabel("Required Document Checklist:")
        self.lbl_check_header.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(self.lbl_check_header)
        
        self.checklist_container = QWidget()
        self.checklist_layout = QVBoxLayout(self.checklist_container)
        self.checklist_layout.setContentsMargins(5, 0, 5, 0)
        layout.addWidget(self.checklist_container)
        
        # 4. Pipeline State Control Dropdown
        state_layout = QHBoxLayout()
        state_layout.addWidget(QLabel("Pipeline Status:"))
        self.combo_status = QComboBox()
        self.combo_status.addItems(["TODO", "Working on CV", "Complete"])
        self.combo_status.currentTextChanged.connect(self._on_status_changed)
        state_layout.addWidget(self.combo_status)
        layout.addLayout(state_layout)
        
        # 5. Core Operational Action Controls
        btn_layout = QHBoxLayout()
        self.btn_edit = QPushButton("✏️ Edit Details")
        self.btn_edit.clicked.connect(self._on_edit_clicked)
        self.btn_delete = QPushButton("🗑️ Delete Position")
        self.btn_delete.setStyleSheet("background-color: #EF4444; color: white; font-weight: bold;")
        self.btn_delete.clicked.connect(self._on_delete_clicked)

        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        layout.addLayout(btn_layout)
        
        layout.addStretch() # Forces elements to stay tightly pinned to the top layer
        self.setWidget(container)

    # ─── DATA INGESTION ENGINE ──────────────────────────────────────────
    def render_job_profile(self, job: dict):
        """
        Receives the structural dictionary payload from the main window controller.
        Parses keys and safely draws elements on screen.
        """
        self.active_job_id = job["id"]
        
        # Update text labels
        self.lbl_title.setText(f"🎯 {job['title']}\n🏢 {job['company']}")

        notes = ""
        for key, value in job['metadata'].items() :
            line = f"<b>{key}:</b>\t\t{value}<br>"
            notes += line

        # Clean string layout for JSON metadata fields
        meta_html = f"""
        <b>Department/Branch:</b>{job['department'] or 'Not Specified'}<br>
        <b>Closing Date Limit:</b> <span style='color: #DC2626;'>{job['closing_date']} : {job['closing_time']}</span><br>
        <b>Link:</b><a href="{job['job_link']}">{job['job_link']}</a><br><br>
        <b>Custom Notes:</b><br><br>
        {notes}
        """
        self.lbl_meta.setText(meta_html)
        
        # Update pipeline state combo without triggering recursive signal loop traps
        self.combo_status.blockSignals(True)
        self.combo_status.setCurrentText(job["status"])
        self.combo_status.blockSignals(False)
        
        # 🧹 Clear old checklists dynamically before building the new model
        while self.checklist_layout.count():
            child = self.checklist_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        # Generate check-boxes on-the-fly matching the specific role rows array requirements
        if job["documents"]:
            for doc in job["documents"]:
                clean_name = doc.strip()
                if clean_name:
                    checkbox = QCheckBox(f"Verify: {clean_name}")
                    self.checklist_layout.addWidget(checkbox)
        else:
            self.checklist_layout.addWidget(QLabel("No documents required for this role profile."))

    # ─── INTERNAL LOGIC SIGNALS EVENT INTERCEPTORS ─────────────────────
    def _on_status_changed(self, new_status: str):
        """Dispatches status updates outward when you tweak the dropdown."""
        if self.active_job_id is not None:
            self.status_updated.emit(self.active_job_id, new_status)

    def _on_delete_clicked(self):
        """Intercepts delete operations and requests authorization via Dialog."""
        if self.active_job_id is None:
            return
            
        confirm = QMessageBox.question(
            self, "Confirm Record Purge", 
            "Are you sure you want to permanently delete this application instance from the local database layer?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            self.delete_requested.emit(self.active_job_id)
            self._reset_dashboard_state()

    def _on_edit_clicked(self):
        if self.active_job_id is None:
            return 

        self.edit_requested.emit(self.active_job_id)

    def _reset_dashboard_state(self):
        """Brings elements back to neutral layout canvas fields after standard deletions."""
        self.active_job_id = None
        self.lbl_title.setText("Select an application from the watchlist...")
        self.lbl_meta.setText("Metadata tracking profiles will populate here.")
        while self.checklist_layout.count():
            child = self.checklist_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
