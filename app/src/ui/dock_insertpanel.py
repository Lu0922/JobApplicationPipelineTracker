# app/arc/ui/dock_editpanel.py
import sys

from PySide6.QtCore import Qt, Signal, QDate, QTime
from PySide6.QtWidgets import (
    QDockWidget, QWidget, QFormLayout, QLineEdit, QTextEdit,
    QPushButton, QMessageBox, QHBoxLayout,
    QDateEdit, QTimeEdit, QComboBox
)

class DockInsertPanel(QDockWidget):
    form_complete = Signal(dict)

    def __init__(self, config_manager, parent=None):
        super().__init__("New Job Insert Panel", parent)
        self.config_manager = config_manager
        self.logger = self.config_manager.logger
        self.parent = parent
        self.setObjectName("InsertPanelDock")
        self.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable | QDockWidget.DockWidgetFeature.DockWidgetFloatable)

        self.init_ui()
        # self.insert_test_data()

    def init_ui(self):
        container = QWidget()
        form_layout = QFormLayout(container)
        form_layout.setSpacing(10)

        """
        company TEXT NOT NULL,
        position_title TEXT NOT NULL,
        closing_date DATE NOT NULL,
        closing_time TIME NOT NULL DEFAULT '00:00',              
        department TEXT
        """
        self.txt_company_name = QLineEdit()
        self.txt_company_name.setPlaceholderText("Enter Company name")

        self.txt_department_name = QLineEdit()
        self.txt_department_name.setPlaceholderText("Enter department name")

        self.txt_position_title = QLineEdit()
        self.txt_position_title.setPlaceholderText("Enter Position Title")

        self.txt_application_type =  QComboBox()
        self.txt_application_type.addItems(["Single", "Pool", "Registered", "Other"])

        closing_time_layout = QHBoxLayout()
        self.closing_date = QDateEdit(QDate.currentDate())
        self.closing_date.setDisplayFormat("yyyy/MM/dd")
        self.closing_date.setCalendarPopup(True)
        self.closing_time = QTimeEdit(QTime.currentTime())
        self.closing_time.setDisplayFormat("HH:mm")
        closing_time_layout.addWidget(self.closing_date)
        closing_time_layout.addWidget(self.closing_time)

        """
        job_link TEXT NOT NULL,
        progress_state TEXT DEFAULT 'TODO',      
        required_documents TEXT NOT NULL,        
        custom_metadata TEXT DEFAULT '{}',       
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        """
        self.txt_job_link = QLineEdit()
        self.txt_job_link.setPlaceholderText("Enter The Link to the job ad")

        self.txt_required_documents = QLineEdit()
        self.txt_required_documents.setPlaceholderText("Enter The required documents, separate with ','")
        
        self.txt_custom_notes = QTextEdit()
        self.txt_custom_notes.setPlaceholderText("Enter addition notes in the from key:value; eg: Contact_Person:Rebecca_Hall")

        # 3. Add rows to the form (Label Text, Widget/Layout)
        form_layout.addRow("🏢 Company Name:", self.txt_company_name)
        form_layout.addRow("🔴 Department:", self.txt_department_name)
        form_layout.addRow("🔴 Position Title:", self.txt_position_title)
        form_layout.addRow("🔴 Application Type:", self.txt_application_type)
        form_layout.addRow("🕒 Closing Time:", closing_time_layout)
        form_layout.addRow("🔗 Job Link:", self.txt_job_link)
        form_layout.addRow("📁 Required Documents:", self.txt_required_documents)
        form_layout.addRow("📎 Additional Notes:", self.txt_custom_notes)

        self.btn_execute_insert = QPushButton("📦 Execute Insert new job to database")
        self.btn_execute_insert.setStyleSheet("background-color: #10B981; color: white; font-weight: bold; font-size: 13px; padding: 6px;")
        self.btn_execute_insert.clicked.connect(self._on_execute_insert)
        form_layout.addWidget(self.btn_execute_insert)
        self.setWidget(container)

    def _on_execute_insert(self) :
        payload = {

        }       
        """
        company TEXT NOT NULL,
        position_title TEXT NOT NULL,
        closing_date DATE NOT NULL,
        closing_time TIME NOT NULL DEFAULT '00:00',              
        department TEXT
        """
        payload["company"] = self.txt_company_name.text().replace(' ', '_')
        payload["title"] = self.txt_position_title.text().replace(' ', '_')
        payload["type"] = self.txt_application_type.currentText().upper()
        payload["date"] = self.closing_date.date().toString("yyyy/MM/dd")
        payload["time"] = self.closing_time.time().toString("HH:mm")
        payload["dept"] = self.txt_department_name.text().replace(' ', '_')

        """
        job_link TEXT NOT NULL,
        progress_state TEXT DEFAULT 'TODO',      
        required_documents TEXT NOT NULL,        
        custom_metadata TEXT DEFAULT '{}',       
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        """

        payload["job_link"] = self.txt_job_link.text().strip()
        payload["state"] = "TODO"
        payload["docs"] = self.txt_required_documents.text().replace(' ', '_')
        notes = self.txt_custom_notes.toPlainText().split('\n')

        payload["meta"] = {}
        for line in notes :
            try :
                entry = line.split(':')
                payload["meta"][f"{entry[0]}"] = entry[1]
            except IndexError:
                self.logger.info(f"Meta data insert skipped for {line}")
                continue

        confirm = QMessageBox.question(
            self, "Confirm Record Insert", 
            "Are you sure you want to insert this new entry",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            self.form_complete.emit(payload)