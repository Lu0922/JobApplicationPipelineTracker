# app/src/gui/packaging_dock.py
import os
import shutil
from pathlib import Path
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QListWidget, 
    QListWidgetItem, QFileDialog, QMessageBox
)

from src.ui.layout import update_json

class DockPackaging(QDockWidget):
    # 📡 Emitted when a package cycle finishes, alerting MainWindow to fetch fresh row statistics
    packaging_complete = Signal()

    def __init__(self, config_manager, parent=None):
        super().__init__("Asset Packaging & Local Export Hub", parent)
        self.config_manager = config_manager
        self.logger = config_manager.logger
        self.parent = parent   
        self.setObjectName("PackagingDock")
        
        # Runtime Data Triggers
        self.active_job_context = None
        self.current_index = 0

        # 🧪 Construct the Visual Layout Tree
        self.init_ui()

        # 🔌 Automatically load saved paths from your centralized JSON file on boot
        self.load_persisted_paths()
        self.update_job_context()
        
    def init_ui(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(10)

        # ─── SECTION 1: QUALIFICATIONS DIRECTORY CONFIG ────────────────
        qual_layout = QHBoxLayout()
        self.txt_qual_path = QLineEdit()
        self.txt_qual_path.setPlaceholderText("Select your Master Qualifications directory path...")
        self.txt_qual_path.textChanged.connect(self._scan_qualifications_directory)

        btn_browse_qual = QPushButton("📁 Browse")
        btn_browse_qual.clicked.connect(self._browse_qualifications_dir)
        
        qual_layout.addWidget(QLabel("Source Docs:"))
        qual_layout.addWidget(self.txt_qual_path)
        qual_layout.addWidget(btn_browse_qual)
        layout.addLayout(qual_layout)

        # ─── SECTION 2: DIGITAL INTERACTIVE ASSET CHECKLIST ────────────
        layout.addWidget(QLabel("Detected Master Qualification Files (Check to Include):"))
        self.asset_list_view = QListWidget()
        layout.addWidget(self.asset_list_view)

        # ─── SECTION 3: EXPORT OUTPUT DIRECTORY CONFIG ─────────────────
        output_layout = QHBoxLayout()
        self.txt_output_path = QLineEdit()
        self.txt_output_path.setPlaceholderText("Select where application folders should be generated...")
        self.txt_output_path.textChanged.connect(self._scan_output_directory)
        
        btn_browse_out = QPushButton("📁 Browse")
        btn_browse_out.clicked.connect(self._browse_output_dir)
        
        output_layout.addWidget(QLabel("Export Dest:"))
        output_layout.addWidget(self.txt_output_path)
        output_layout.addWidget(btn_browse_out)
        layout.addLayout(output_layout)

        # ─── SECTION 4: EXECUTION CORE ENGINE TRIPPERS ──────────────────
        self.lbl_counter = QLabel(f"Current Application Index Count: {self.current_index} (Folder prefix will map to: {self.current_index + 1})")
        self.lbl_counter.setStyleSheet("color: #4B5563; font-style: italic;")
        layout.addWidget(self.lbl_counter)

        self.btn_execute_package = QPushButton("📦 Execute Asset Packaging Loop")
        self.btn_execute_package.setStyleSheet("background-color: #10B981; color: white; font-weight: bold; font-size: 13px; padding: 6px;")
        self.btn_execute_package.clicked.connect(self._on_execute_packaging)
        layout.addWidget(self.btn_execute_package)
        self.setWidget(container)

    # ─── CONTEXT INTERACTION CAPTURE PADS ──────────────────────────────
    def update_job_context(self):
        """Receives active pipeline metadata when row selection triggers are fired."""
        self.lbl_counter.setText(
            f"Current Application Index Count: {self.current_index} "
            f"(Folder prefix will map to: {self.current_index + 1})"
        )

    # ─── REPOSITORY SCANNER & FILE DISCOVERY METHODS ───────────────────
    def _browse_qualifications_dir(self):
        """Launches graphical directory canvas picker for master documents."""
        directory = QFileDialog.getExistingDirectory(self, "Select Master Qualifications Directory", self.txt_qual_path.text())
        if directory:
            self.txt_qual_path.setText(directory)
            update_json(config_path=self.config_manager.config_path, category="assets",key="qualifications_source_directory", value=directory)

    def _browse_output_dir(self):
        """Launches graphical directory canvas picker for target exports."""
        directory = QFileDialog.getExistingDirectory(self, "Select Application Export Directory", self.txt_output_path.text())
        if directory:
            self.txt_output_path.setText(directory)
            update_json(config_path=self.config_manager.config_path, category="assets",key="applications_export_directory", value=directory)

    def _scan_qualifications_directory(self, target_path_str: str):
        """Scans folder directory paths dynamically and inserts items in alphabetical order."""
        self.asset_list_view.clear()
        source_dir = Path(target_path_str.strip())
        
        if not source_dir.exists() or not source_dir.is_dir():
            return
            
        try:
            # 📂 Extract filenames, filter out hidden files, and apply a strict alphabetical sort
            sorted_files = sorted([item.name for item in source_dir.iterdir() if item.is_file() and not item.name.startswith('.')])
            
            # 🧱 Append the sorted items cleanly into the interactive list panel
            for filename in sorted_files:
                list_item = QListWidgetItem(filename)
                list_item.setFlags(list_item.flags() | Qt.ItemIsUserCheckable)
                list_item.setCheckState(Qt.Unchecked)
                self.asset_list_view.addItem(list_item)
                
        except OSError as e:
            print(f"⚠️ Directory scanning access error encountered: {e}")


    def _scan_output_directory(self, target_path_str: str):
        current_index = 0
        try:
            with os.scandir(target_path_str) as output_dir:
                for dir in output_dir:
                    if dir.is_dir() and not dir.name.startswith('.'):
                        try :
                            entry_index = int(dir.name.split('_')[0])
                        except ValueError :
                            continue
                        current_index = max(current_index, entry_index)

                self.current_index = int(current_index)
        except OSError as e:
            print(f"⚠️ Directory scanning access error encountered: {e}")

    # ─── LOCAL STORAGE MANAGEMENT PERSISTENCE CORE ──────────────────────
    def load_persisted_paths(self):
        """Loads cached system variables cleanly from config maps on system launch."""
        qual_path = self.config_manager.get("assets", "qualifications_source_directory")
        out_path = self.config_manager.get("assets", "applications_export_directory")
        
        if qual_path:
            self.txt_qual_path.setText(qual_path)
        if out_path:
            self.txt_output_path.setText(out_path)

    # ─── PACKAGING EXECUTION & SHUTIL REPLICATION ENGINE ──────────────
    def _on_execute_packaging(self):
        """Compiles selected checkable files and duplicates them to dynamic destination targets."""
        if not self.active_job_context:
            QMessageBox.warning(self, "Context Target Void", "Select an active tracking row target row from your Watchlist first.")
            return
            
        output_dir_base = self.txt_output_path.text().strip()
        source_dir_base = self.txt_qual_path.text().strip()
        
        if not output_dir_base or not source_dir_base:
            QMessageBox.warning(self, "Directories Unconfigured", "Both your Source Documents and Export Destination directory fields must be defined.")
            return

        # Collate explicit files currently checked off inside list panels
        selected_filenames = []
        for index in range(self.asset_list_view.count()):
            item = self.asset_list_view.item(index)
            if item.checkState() == Qt.Checked:
                selected_filenames.append(item.text())

        if not selected_filenames:
            QMessageBox.warning(self, "Asset Packages Blank", "Check at least one file box inside the dashboard list panel to package.")
            return

        # Calculate strict target output format parameters token required by instruction:
        # {number of application + 1}_{Position title}_{Company name}
        next_app_prefix = self.current_index + 1
        safe_title = self.active_job_context["title"].replace(" ", "_")
        safe_company = self.active_job_context["company"].replace(" ", "_")
        
        target_folder_name = f"{next_app_prefix}_{safe_title}_{safe_company}"
        final_deployment_path = Path(output_dir_base) / target_folder_name

        try:
            # Construct target path location folders securely onto system harddrive channels
            final_deployment_path.mkdir(parents=True, exist_ok=True)
            
            # Replicate files natively across system folder channels using high-performance loops
            for filename in selected_filenames:
                source_file_pointer = Path(source_dir_base) / filename
                destination_file_pointer = final_deployment_path / filename
                shutil.copy2(str(source_file_pointer), str(destination_file_pointer)) # Preserves original metadata tags
                
            QMessageBox.information(
                self, "Packaging Operation Success", 
                f"Successfully processed package pipeline!<br><br>Target Folder Built:<br><code>{final_deployment_path}</code>"
            )
            self.packaging_complete.emit()
            
        except (OSError, shutil.Error) as e:
            QMessageBox.critical(self, "Packaging Engine Fault", f"File System Copy Operations Encountered Critical Blockage:<br>{e}")
