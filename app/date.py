from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QDateEdit
from PySide6.QtCore import QDate
import sys

def handle_date_change(qdate_obj):
    # 1. Raw PySide6 object
    print("QDate Object:", qdate_obj) 
    
    # 2. Native Python datetime.date object
    print("Python Date:", qdate_obj.toPython()) 
    
    # 3. Custom String (e.g., DD/MM/YYYY)
    print("Formatted String:", qdate_obj.toString("dd/MM/yyyy"))
    print("-" * 30)

app = QApplication(sys.argv)
window = QWidget()
layout = QVBoxLayout(window)

date_edit = QDateEdit(QDate.currentDate())
date_edit.setCalendarPopup(True)

# The dateChanged signal automatically passes a QDate object to your function
date_edit.dateChanged.connect(handle_date_change)

layout.addWidget(date_edit)
window.show()
sys.exit(app.exec())

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTimeEdit
from PySide6.QtCore import QTime
import sys

def handle_time_change(qtime_obj):
    # 1. Raw PySide6 object (PySide6.QtCore.QTime(HH, MM, SS, MS))
    print("QTime Object:", qtime_obj) 
    
    # 2. Native Python datetime.time object (HH:MM:SS)
    print("Python Time:", qtime_obj.toPython()) 
    
    # 3. Custom String (e.g., 12-hour format with AM/PM)
    print("Formatted String:", qtime_obj.toString("hh:mm AP"))
    print("-" * 30)

app = QApplication(sys.argv)
window = QWidget()
layout = QVBoxLayout(window)

# Create the time editor and set it to the current system time
time_edit = QTimeEdit(QTime.currentTime())

# The timeChanged signal automatically passes a QTime object to the function
time_edit.timeChanged.connect(handle_time_change)

layout.addWidget(time_edit)
window.show()
sys.exit(app.exec())
