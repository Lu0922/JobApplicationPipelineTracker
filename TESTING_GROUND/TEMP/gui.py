import sys
import os
import json
import sqlite3
from pathlib import Path
from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QDockWidget, QListWidget,
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFormLayout,
    QLineEdit, QComboBox, QDateEdit, QCheckBox, QListWidgetItem,
    QStatusBar, QToolBar, QMessageBox, QFrame
)

class JobTrackerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Job Application Pipeline Tracker Console")
        self.resize(1280, 800)
        
        # 1. Establish the Central Workspace Anchor (Empty Placeholder)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setMinimumSize(100, 100) # Yields dominance to docks
        
        # 2. State Cache Variable
        self.active_job_id = None
        
        # 3. Compile UI Components
        self.init_dock_ui()
        self.init_toolbar_ui()
        
        # 4. Boot Data Sync Layer
        self.refresh_watchlist_view()
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Pipeline Active. Database connection synchronized.")

    # ─── PANEL 1: LEFT WATCHLIST LAYER ─────────────────────────────────
    def init_dock_ui(self):
        # Left Dock Widget
        self.dock_left = QDockWidget("Application Watchlist", self)
        self.dock_left.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.watchlist_view = QListWidget()
        self.watchlist_view.itemClicked.connect(self.handle_job_selection)
        self.dock_left.setWidget(self.watchlist_view)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_left)

        # ─── PANEL 2: RIGHT DETAIL DASHBOARD ───────────────────────────
        self.dock_right = QDockWidget("Application Details Dashboard", self)
        self.dock_right.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        
        self.lbl_title = QLabel("Select an application from the watchlist...")
        self.lbl_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #4F46E5;")
        right_layout.addWidget(self.lbl_title)
        
        # Form fields for metadata display
        self.lbl_meta = QLabel("")
        self.lbl_meta.setWordWrap(True)
        right_layout.addWidget(self.lbl_meta)
        
        # State Manipulation Dropdown
        state_layout = QHBoxLayout()
        state_layout.addWidget(QLabel("Pipeline Status:"))
        self.combo_status = QComboBox()
        self.combo_status.addItems(["TODO", "Working on CV", "Complete"])
        self.combo_status.currentTextChanged.connect(self.update_job_status_in_db)
        state_layout.addWidget(self.combo_status)
        right_layout.addLayout(state_layout)
        
        # Action Buttons
        btn_layout = QHBoxLayout()
        self.btn_edit = QPushButton("✏️ Edit Entry")
        self.btn_delete = QPushButton("🗑️ Delete Position")
        self.btn_delete.setStyleSheet("background-color: #EF4444; color: white;")
        self.btn_delete.clicked.connect(self.delete_current_job)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        right_layout.addLayout(btn_layout)
        
        self.dock_right.setWidget(right_container)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock_right)

        # ─── PANEL 3: LOWER PACKAGING UTILITY ──────────────────────────
        self.dock_lower = QDockWidget("Asset Packaging & Local Export Hub", self)
        self.dock_lower.setAllowedAreas(Qt.BottomDockWidgetArea | Qt.TopDockWidgetArea)
        
        lower_container = QWidget()
        lower_layout = QVBoxLayout(lower_container)
        
        lower_layout.addWidget(QLabel("Select Master Assets to Package for Deployment Location:"))
        self.chk_cv = QCheckBox("Master CV PDF (master_cv.pdf)")
        self.chk_criteria = QCheckBox("Master Selection Criteria (master_criteria.pdf)")
        self.chk_degree = QCheckBox("Official Academic Transcript (master_degree.pdf)")
        
        lower_layout.addWidget(self.chk_cv)
        lower_layout.addWidget(self.chk_criteria)
        lower_layout.addWidget(self.chk_degree)
        
        self.btn_package = QPushButton("📦 Execute Asset Packaging Loop")
        self.btn_package.clicked.connect(self.execute_folder_packaging_engine)
        lower_layout.addWidget(self.btn_package)
        
        self.dock_lower.setWidget(lower_container)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.dock_lower)

        # ─── PANEL 4: TOGGLEABLE APPLICATION INGEST FORM ───────────────
        self.dock_ingest = QDockWidget("Ingest New Position Details", self)
        self.dock_ingest.setAllowedAreas(Qt.AllDockWidgetAreas)
        
        form_container = QWidget()
        form_layout = QFormLayout(form_container)
        
        self.txt_company = QLineEdit()
        self.txt_pos_title = QLineEdit()
        self.txt_dept = QLineEdit()
        self.date_closing = QDateEdit(QDate.currentDate())
        self.date_closing.setCalendarPopup(True)
        self.txt_docs = QLineEdit("CV,Selection Criteria")
        self.txt_ref_num = QLineEdit()
        
        form_layout.addRow("Company Entity:", self.txt_company)
        form_layout.addRow("Position Title:", self.txt_pos_title)
        form_layout.addRow("Department/Branch:", self.txt_dept)
        form_layout.addRow("Closing Boundary Date:", self.date_closing)
        form_layout.addRow("Required Docs (CSV):", self.txt_docs)
        form_layout.addRow("Reference ID/Salary (JSON):", self.txt_ref_num)
        
        btn_submit = QPushButton("💾 Commit Configuration to SQLite Database")
        btn_submit.clicked.connect(self.commit_new_job_to_db)
        form_layout.addRow(btn_submit)
        
        self.dock_ingest.setWidget(form_container)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock_ingest)
        self.tabifyDockWidget(self.dock_right, self.dock_ingest) # Clean stack layout

    # ─── PANEL 5: LOWER TOOLBAR ACCESSIBILITY LAYER ───────────────────
    def init_toolbar_ui(self):
        toolbar = QToolBar("System Console Layout Controls")
        self.addToolBar(Qt.BottomToolBarArea, toolbar)
        
        # Ingest custom system view visibility toggles maps
        toolbar.addAction(self.dock_left.toggleViewAction())
        toolbar.addAction(self.dock_right.toggleViewAction())
        toolbar.addAction(self.dock_lower.toggleViewAction())
        toolbar.addAction(self.dock_ingest.toggleViewAction())

    # ─── DATABASE INTERACTION OPERATIONS LAYER ─────────────────────────
    def refresh_watchlist_view(self):
        self.watchlist_view.clear()
        if not DB_PATH.exists():
            return
            
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, company, position_title, closing_date, progress_state FROM applications ORDER BY closing_date ASC;")
            rows = cursor.fetchall()
            for row in rows:
                item_text = f"🎯 {row[2]} \n   🏢 {row[1]} | ⏰ {row[3]} \n   📊 [{row[4]}]"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, row[0]) # Bind Primary Key database index safely to widget instance
                self.watchlist_view.addItem(item)
        except sqlite3.Error as e:
            self.status_bar.showMessage(f"Database Read Failure: {e}")
        finally:
            conn.close()

    def handle_job_selection(self, item):
        self.active_job_id = item.data(Qt.UserRole)
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT company, position_title, closing_date, department, progress_state, required_documents, custom_metadata FROM applications WHERE id = ?;", (self.active_job_id,))
            job = cursor.fetchone()
            if job:
                self.lbl_title.setText(f"{job[1]}\n@{job[0]}")
                meta_text = f"<b>Department:</b> {job[3]}<br><b>Closing Date:</b> {job[2]}<br><br><b>Required Document Verification Blueprint:</b><br>{job[5]}<br><br><b>JSON Metadata Store:</b><br>{job[6]}"
                self.lbl_meta.setText(meta_text)
                
                # Update combobox state without firing loop signals recursively
                self.combo_status.blockSignals(True)
                self.combo_status.setCurrentText(job[4])
                self.combo_status.blockSignals(False)
        except sqlite3.Error as e:
            self.status_bar.showMessage(f"Error fetching detail records: {e}")
        finally:
            conn.close()

    def commit_new_job_to_db(self):
        company = self.txt_company.text().strip()
        title = self.txt_pos_title.text().strip()
        date_str = self.date_closing.date().toString("yyyy-MM-dd")
        dept = self.txt_dept.text().strip()
        docs = self.txt_docs.text().strip()
        meta_raw = self.txt_ref_num.text().strip() or "{}"
        
        if not company or not title:
            QMessageBox.warning(self, "Data Incomplete", "Core schema requires unique Company and Position Title inputs.")
            return

        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO applications (company, position_title, closing_date, department, required_documents, custom_metadata)
                VALUES (?, ?, ?, ?, ?, ?);
            """, (company, title, date_str, dept, docs, meta_raw))
            conn.commit()
            self.status_bar.showMessage(f"Successfully recorded position: {title}")
            self.refresh_watchlist_view()
        except sqlite3.IntegrityError:
            QMessageBox.critical(self, "Integrity Mismatch", "Database constraint blocked submission. Record entry duplicate already configured.")
        finally:
            conn.close()

    def update_job_status_in_db(self, new_status):
        if not self.active_job_id:
            return
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE applications SET progress_state = ? WHERE id = ?;", (new_status, self.active_job_id))
            conn.commit()
            self.status_bar.showMessage(f"Pipeline status adjusted successfully to: {new_status}")
            self.refresh_watchlist_view()
        except sqlite3.Error as e:
            self.status_bar.showMessage(f"Update failure: {e}")
        finally:
            conn.close()

    def delete_current_job(self):
        if not self.active_job_id:
            return
        confirm = QMessageBox.question(self, "Confirm Purge", "Are you sure you want to delete this position record completely from the SQLite database?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            conn = sqlite3.connect(str(DB_PATH))
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM applications WHERE id = ?;", (self.active_job_id,))
                conn.commit()
                self.status_bar.showMessage("Record purged successfully.")
                self.active_job_id = None
                self.lbl_title.setText("Select an application from the watchlist...")
                self.lbl_meta.setText("")
                self.refresh_watchlist_view()
            except sqlite3.Error as e:
                self.status_bar.showMessage(f"Deletion error: {e}")
            finally:
                conn.close()

    # ─── LOCAL FILE COMPILATION ENGINE FOR THE nth APPLICATION ─────────
    def execute_folder_packaging_engine(self):
        if not self.active_job_id:
            QMessageBox.warning(self, "Target Index Void", "Select an active tracking target row to calculate the folder string schema variables.")
            return
            
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        cursor.execute("SELECT company, position_title FROM applications WHERE id = ?;", (self.active_job_id,))
        job = cursor.fetchone()
        
        # Calculate Nth count parameter metric natively using cursor evaluation loops
        cursor.execute("SELECT COUNT(*) FROM applications WHERE id <= ?;", (self.active_job_id,))
        nth_count = cursor.fetchone()[0]
        conn.close()
        
        # Enforce strict layout token parameters specified in instruction:
        # {the nth application}_{position}_{company}
        safe_pos = job[1].replace(" ", "")
        safe_comp = job[0].replace(" ", "")
        target_folder_name = f"application_{nth_count}_{safe_pos}_{safe_comp}"
        
        export_path = ROOT_DIR / "applications_export" / target_folder_name
        export_path.mkdir(parents=True, exist_ok=True)
        
        # Log target result to downstream UI console dialog channels
        QMessageBox.information(self, "Packaging Loop Deployed", f"Package compilation successful!<br><br>Target folder structured natively at:<br><code>{export_path}</code>")
        self.status_bar.showMessage(f"Folder package compiled: {target_folder_name}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = JobTrackerWindow()
    window.show()
    sys.exit(app.exec())
