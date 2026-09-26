import sqlite3

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDockWidget, QListWidget, QVBoxLayout, QWidget, QListWidgetItem

class DockWatchlist(QDockWidget) :
    def __init__(self, config_manager, parent=None) :
        super().__init__("Application Watchlist", parent)
        self.config_manager = config_manager
        self.logger = self.config_manager.logger

        # Left Dock Widget
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        self.watchlist_view = QListWidget()

        self.setObjectName("WatchlistDock")
        # 🎨 Style the list so entries look like spacious dashboard buttons
        self.watchlist_view.setStyleSheet("""
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #E5E7EB;
            }
            QListWidget::item:hover {
                background-color: #EEF2F6;
                border-radius: 4px;
            }
            QListWidget::item:selected {
                background-color: #E0E7FF;
                color: #4F46E5;
                font-weight: bold;
                border-radius: 4px;
            }
        """)
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.addWidget(self.watchlist_view)
        self.setWidget(container)

    def populate_watchlist(self, jobs_list):
        """
        Clears the view and populates rows natively from your database payload.
        jobs_list format: [(id, company, position_title, closing_date, status), ...]
        """
        self.watchlist_view.clear()
        
        for job_id, company, title, closing_date, status in jobs_list:
            # 1. Construct a clean, scannable text string for the row item
            display_text = f"🎯 {title}\n🏢 {company}\n⏰ Closes: {closing_date}  |  📊 [{status}]"
            
            # 2. Instantiate a clean layout node item
            item = QListWidgetItem(display_text)
            
            # 3. 🛡️ Crucial Data Link: Pack the exact Primary Key database integer into the UI node memory
            item.setData(Qt.UserRole, job_id)
            
            # 4. Inject the item into the visual list container hierarchy
            self.watchlist_view.addItem(item)

    # TODO
    def handle_job_selection(self, item):
        # """Triggers automatically when an entry is clicked."""
        # # Extract the hidden primary key integer directly from the UI node metadata
        # job_id = item.data(Qt.UserRole)
        
        # # Securely fetch the complete dictionary record map for this specific item
        # job_details = self.query_manager.get_job_by_id(job_id)
        
        # if job_details:
        #     # Pass the data map directly into your Right Detail Dashboard dock panel to render
        #     self.dock_details.render_job_profile(job_details)
        print(item.data(Qt.UserRole))