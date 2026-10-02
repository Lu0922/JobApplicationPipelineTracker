# app/src/gui/search_controls.py
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLineEdit, 
                             QComboBox, QPushButton, QDialog, QLabel)
from PySide6.QtCore import Qt, Signal

class FilterDialog(QDialog):
    """A clean, compact floating window to select advanced pipeline filtering criteria."""
    filters_changed = Signal(str, str) # Emits: (status_filter, type_filter)

    def __init__(self, current_status="ALL STATUS", current_type="ALL TYPES", parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚙️ Pipeline Filters")
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint | Qt.CustomizeWindowHint)
        self.setModal(False) # Keep it floating and non-blocking
        self.setMinimumWidth(260)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)

        # 📊 Progress State Filter Row
        layout.addWidget(QLabel("<b>Application Progress State:</b>"))
        self.combo_status = QComboBox()
        self.combo_status.addItems(["ALL STATUS", "TODO", "IN_PROGRESS", "SUBMITTED"])
        self.combo_status.setCurrentText(current_status)
        layout.addWidget(self.combo_status)

        # 🗂️ Application Type Filter Row
        layout.addWidget(QLabel("<b>Application Architecture Type:</b>"))
        self.combo_type = QComboBox()
        self.combo_type.addItems(["ALL TYPES", "SINGLE", "POOL", "REGISTER"])
        self.combo_type.setCurrentText(current_type)
        layout.addWidget(self.combo_type)

        # 🔄 Connect signals to immediately update background dashboard model
        self.combo_status.currentTextChanged.connect(self._emit_filters)
        self.combo_type.currentTextChanged.connect(self._emit_filters)

        # 🎨 Dialog Styling
        self.setStyleSheet("""
            QDialog { background-color: #F8FAFC; }
            QLabel { color: #334155; font-size: 12px; }
            QComboBox { padding: 6px; border: 1px solid #CBD5E1; border-radius: 4px; background: white; }
        """)

    def _emit_filters(self):
        self.filters_changed.emit(self.combo_status.currentText(), self.combo_type.currentText())

class WatchlistSearchHeader(QWidget):
    """Integrated dashboard controller bar housing the text query line and the floating filter button."""
    search_updated = Signal(str, str, str) # Emits: (text_query, status_filter, type_filter)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # 🔍 Main Live Text-Match Query Field
        self.txt_query = QLineEdit()
        self.txt_query.setPlaceholderText("Filter by agency or position title...")
        self.txt_query.textChanged.connect(self._trigger_pipeline_update)
        layout.addWidget(self.txt_query)

        # ⚙️ Small Floating Filter Trigger Button
        self.btn_filter = QPushButton("⚙️")
        self.btn_filter.setToolTip("Open advanced criteria filter panel")
        self.btn_filter.setFixedWidth(36)
        self.btn_filter.clicked.connect(self.toggle_filter_panel)
        layout.addWidget(self.btn_filter)

        # Cache structural active filter states
        self.active_status = "ALL STATUS"
        self.active_type = "ALL TYPES"
        self.filter_dialog = None

        self.setStyleSheet("""
            QLineEdit { padding: 6px; border: 1px solid #CBD5E1; border-radius: 4px; background: white; }
            QPushButton { padding: 6px; border: 1px solid #CBD5E1; border-radius: 4px; background: #F1F5F9; font-size: 14px; }
            QPushButton:hover { background: #E2E8F0; border-color: #94A3B8; }
        """)

    def toggle_filter_panel(self):
        """Spawns or switches visibility focus of the floating criteria settings window."""
        if self.filter_dialog is None:
            # Instantiate coordinates tracking relative to the global workspace widget frame
            self.filter_dialog = FilterDialog(self.active_status, self.active_type, self.window())
            self.filter_dialog.filters_changed.connect(self._update_filter_parameters)
            
            # Position floating dialogue cleanly underneath the trigger icon anchor geometry
            geo = self.btn_filter.mapToGlobal(self.btn_filter.rect().bottomLeft())
            self.filter_dialog.move(geo.x() - 220, geo.y() + 5)
            self.filter_dialog.show()
        else:
            if self.filter_dialog.isVisible():
                self.filter_dialog.hide()
            else:
                self.filter_dialog.show()
                self.filter_dialog.raise_()
                self.filter_dialog.activateWindow()

    def _update_filter_parameters(self, status_val, type_val):
        self.active_status = status_val
        self.active_type = type_val
        self._trigger_pipeline_update()

    def _trigger_pipeline_update(self):
        """Bundles structural layout inputs out to main application model loops."""
        self.search_updated.emit(
            self.txt_query.text().strip(),
            self.active_status,
            self.active_type
        )
