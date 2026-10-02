# app/arc/ui/dock_insertpanel.py
import sys

from PySide6.QtCore import Qt, Signal, QDate, QTime
from PySide6.QtWidgets import (
    QDockWidget, QWidget, QFormLayout, QLineEdit, QTextEdit,
    QPushButton, QMessageBox, QHBoxLayout, QLabel,
    QDateEdit, QTimeEdit, QComboBox
)

class DockEditPanel(QDockWidget):
    form_complete = Signal(int, dict)

    def __init__(self, config_manager, active_job_id, job_details, parent=None):
        super().__init__("Job Update Panel", parent)
        self.config_manager = config_manager
        self.logger = self.config_manager.logger
        self.parent = parent
        self.setObjectName("EditPanelDock")
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setAttribute(Qt.WidgetAttribute.WA_AlwaysStackOnTop)
        self.destroyed.connect(self.clear_dock_reference)

        self.active_job_id = active_job_id

        self.init_ui()
        self._populate_active_job_details(job_details)

    def init_ui(self):
        container = QWidget()
        form_layout = QFormLayout(container)
        form_layout.setSpacing(10)
 
        form_layout.addWidget(QLabel(f"Active job id: {self.active_job_id}"))

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
        self.closing_date.setCalendarPopup(True)
        self.closing_date.setDisplayFormat("yyyy/MM/dd")
        self.closing_time = QTimeEdit(QTime.currentTime())
        self.closing_time.setDisplayFormat("HH:mm")
        closing_time_layout.addWidget(self.closing_date)
        closing_time_layout.addWidget(self.closing_time)

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

        self.btn_execute_update = QPushButton("📦 Execute Update job details")
        self.btn_execute_update.setStyleSheet("background-color: #10B981; color: white; font-weight: bold; font-size: 13px; padding: 6px;")
        self.btn_execute_update.clicked.connect(self._on_execute_update)
        form_layout.addWidget(self.btn_execute_update)
        self.setWidget(container)

    def _on_execute_update(self) :
        payload = {}       

        payload["company"] = self.txt_company_name.text().replace(' ', '_')
        payload["title"] = self.txt_position_title.text().replace(' ', '_')
        payload["type"] = self.txt_application_type.currentText().upper()
        payload["date"] = self.closing_date.date().toString("yyyy/MM/dd")
        payload["time"] = self.closing_time.time().toString("HH:mm")
        payload["dept"] = self.txt_department_name.text().replace(' ', '_')
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
            self, "Confirm Record Update", 
            "Are you sure you want to update this entry",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            self.form_complete.emit(self.active_job_id, payload)
            self.close()

    def _populate_active_job_details(self, job: dict) :
        self.txt_company_name.setText(job["company"])
        self.txt_department_name.setText(job["department"])
        self.txt_position_title.setText(job["title"])
        self.txt_application_type.setCurrentText(job["application_type"])

        closing_date_obj = QDate.fromString(job["closing_date"], "yyyy-MM-dd")
        closing_time_obj = QTime.fromString(job["closing_time"], "HH:mm")
        self.closing_date.setDate(closing_date_obj)
        self.closing_time.setTime(closing_time_obj)

        self.txt_job_link.setText(job["job_link"])
        docs = ""
        for doc in job["documents"] :
            docs += f"{doc},"

        self.txt_required_documents.setText(docs[:-1])

        notes = ""
        for key, value in job["metadata"].items() :
            notes += f"{key}:{value}\n"
        
        self.txt_custom_notes.setText(notes)

    def clear_dock_reference(self):
        self.parent.dock_editpanel = None