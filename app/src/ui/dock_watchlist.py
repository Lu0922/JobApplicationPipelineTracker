import sqlite3

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QDockWidget, QListWidget, QVBoxLayout, QWidget, QListWidgetItem, QPushButton, QLineEdit

class DockWatchlist(QDockWidget) :
    job_selected = Signal(int)
    def __init__(self, config_manager, parent=None) :
        super().__init__("Application Watchlist", parent)
        self.config_manager = config_manager
        self.logger = self.config_manager.logger
        self.active_watchlist = []  # Store the current list of jobs for internal reference

        # Left Dock Widget
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable | QDockWidget.DockWidgetFeature.DockWidgetFloatable)
        
        container = QWidget()
        layout = QVBoxLayout(container)

        # search feild and filter button
        # self.search_header = QVBoxLayout()

        # self.search_field = QLineEdit()
        # self.search_field.setPlaceholderText("Filter by agency or position title...")

        # self.filter_button = QPushButton("🔍 Filter Watchlist")
        # self.filter_button.clicked.connect(self.open_filter_dialog)

        self.watchlist_view = QListWidget()
        # 🔗 Internal Routing: Intercept list clicks inside this class
        self.watchlist_view.itemClicked.connect(self._on_item_clicked)

        self.setObjectName("WatchlistDock")
        # 🎨 Style the list so entries look like spacious dashboard buttons
        self.watchlist_view.setStyleSheet("""
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #E5E7EB;
            }
            QListWidget::item:hover {
                background-color: #EEF255;
                border-radius: 4px;
            }
            QListWidget::item:selected {
                background-color: #E0E755;
                color: #4F46E5;
                font-weight: bold;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.watchlist_view)
        self.setWidget(container)

    def populate_watchlist(self, jobs_list):
        """
        Clears the view and populates rows natively from your database payload.
        jobs_list format: [(id, company, position_title, closing_date, status), ...]
        """
        self.watchlist_view.clear()
        
        for job_id, company, title, closing_date, closing_time, status, application_type in jobs_list:
            # 1. Construct a clean, scannable text string for the row item
            display_text = f"📊 [{status}] {application_type}\n🎯 {title}\n🏢 {company}\n⏰ Closes: {closing_date} - {closing_time}"
   
            # 2. Instantiate a clean layout node item
            item = QListWidgetItem(display_text)
            if application_type.upper() != "SINGLE":
                item.setForeground(QColor("#4F46E5"))  # Purple for non-single applications

            if status.upper() != "TODO" :
                item.setForeground(QColor("#999999"))

            # 3. 🛡️ Crucial Data Link: Pack the exact Primary Key database integer into the UI node memory
            item.setData(Qt.UserRole, job_id)
            
            # 4. Inject the item into the visual list container hierarchy
            self.watchlist_view.addItem(item)

        self.active_watchlist = jobs_list  # Update the internal reference for future operations

    def _on_item_clicked(self, item):
        """Internal callback that isolates the click event inside the module."""
        job_id = item.data(Qt.UserRole)
        if job_id is not None:
            # 🚀 Broadcast the raw ID outward. The dock doesn't care who is listening!
            self.job_selected.emit(job_id)

    def open_filter_dialog(self):
        pass