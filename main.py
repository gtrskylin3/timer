
import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QHBoxLayout, QVBoxLayout, 
                             QPushButton, QLabel, QDialog, QSpinBox, QDialogButtonBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Set Time')
        self.layout = QVBoxLayout(self)

        time_layout = QHBoxLayout()
        self.hour_spinbox = self.create_spinbox(0, 23)
        self.minute_spinbox = self.create_spinbox(0, 59)
        self.second_spinbox = self.create_spinbox(0, 59)
        
        time_layout.addWidget(self.hour_spinbox)
        time_layout.addWidget(QLabel(':'))
        time_layout.addWidget(self.minute_spinbox)
        time_layout.addWidget(QLabel(':'))
        time_layout.addWidget(self.second_spinbox)
        
        self.layout.addLayout(time_layout)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.layout.addWidget(buttons)

    def create_spinbox(self, min_val, max_val):
        spinbox = QSpinBox()
        spinbox.setRange(min_val, max_val)
        spinbox.setFont(QFont('Arial', 16))
        return spinbox

    def get_time(self):
        return (self.hour_spinbox.value(), self.minute_spinbox.value(), self.second_spinbox.value())

class TimerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Always on Top Timer')
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.total_seconds = 0
        self.is_paused = True
        self.is_stopwatch_mode = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)

        self.background_widget = QWidget(self)
        self.background_widget.setObjectName("backgroundWidget")
        self.background_widget.setStyleSheet("#backgroundWidget { background-color: black; border-radius: 10px; }")
        
        main_layout = QVBoxLayout(self.background_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Top bar for close button
        top_bar_layout = QHBoxLayout()
        top_bar_layout.addStretch() # Push button to the right
        
        self.close_button = QPushButton('x') # Text for close button
        self.close_button.setFixedSize(12, 14)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: black;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        self.close_button.clicked.connect(self.close) # Connect to window close method
        top_bar_layout.addWidget(self.close_button)

        main_layout.addLayout(top_bar_layout) # Add top bar to main layout
        
        time_layout = QHBoxLayout()
        self.hour_label = self.create_time_label('00')
        self.minute_label = self.create_time_label('00')
        self.second_label = self.create_time_label('00')

        time_layout.addStretch()
        time_layout.addWidget(self.hour_label)
        time_layout.addWidget(self.create_label(':'))
        time_layout.addWidget(self.minute_label)
        time_layout.addWidget(self.create_label(':'))
        time_layout.addWidget(self.second_label)
        time_layout.addStretch()

        button_layout = QHBoxLayout()
        self.play_pause_button = self.create_button('▶', "#5900ff")
        self.stop_button = self.create_button('■', "#dc7535")
        self.settings_button = self.create_button('⚙', "#048ec0")
        
        self.play_pause_button.clicked.connect(self.toggle_play_pause)
        self.stop_button.clicked.connect(self.stop_timer)
        self.settings_button.clicked.connect(self.open_settings)

        button_layout.addStretch()
        button_layout.addWidget(self.play_pause_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addStretch()
        button_layout.addWidget(self.settings_button)

        main_layout.addLayout(time_layout)
        main_layout.addLayout(button_layout)
        
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.background_widget)
        self.layout().setContentsMargins(0,0,0,0)

        self.old_pos = None
        self.update_display()

    def create_time_label(self, text):
        label = QLabel(text)
        label.setFont(QFont('Arial', 24))
        label.setStyleSheet("color: white;")
        return label

    def create_label(self, text):
        label = QLabel(text)
        label.setFont(QFont('Arial', 24))
        label.setStyleSheet("color: white;")
        return label

    def create_button(self, text, color):
        button = QPushButton(text)
        button.setFixedSize(60, 60)
        button.setFont(QFont('Arial', 24))
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: {QColor(color).lighter(115).name()};
            }}
        """)
        return button

    def toggle_play_pause(self):
        if self.is_paused:
            if self.total_seconds == 0:  # Start stopwatch
                self.is_stopwatch_mode = True
                self.timer.start(1000)
                self.play_pause_button.setText('=')
                self.is_paused = False
            elif self.total_seconds > 0: # Start countdown
                self.is_stopwatch_mode = False # Ensure it's not stopwatch mode
                self.timer.start(1000)
                self.play_pause_button.setText('=')
                self.is_paused = False
        else:
            self.timer.stop()
            self.play_pause_button.setText('▶')
            self.is_paused = True
            self.is_stopwatch_mode = False # Stop and reset stopwatch mode

    def stop_timer(self):
        self.timer.stop()
        self.total_seconds = 0
        self.is_stopwatch_mode = False # Reset stopwatch mode
        self.update_display()
        if not self.is_paused:
            self.toggle_play_pause() # Reset button to play
        self.is_paused = True

    def open_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec():
            hours, minutes, seconds = dialog.get_time()
            self.total_seconds = hours * 3600 + minutes * 60 + seconds
            self.is_stopwatch_mode = False # Reset stopwatch mode when new time is set
            self.update_display()
            if not self.is_paused:
                self.toggle_play_pause() # Stop timer and reset button if running
            self.is_paused = True


    def update_time(self):
        if self.is_stopwatch_mode:
            self.total_seconds += 1
            self.update_display()
        elif self.total_seconds > 0: # Countdown mode
            self.total_seconds -= 1
            self.update_display()
        else: # Countdown finished
            self.timer.stop()
            if not self.is_paused:
                self.toggle_play_pause() # Reset button to play
            self.is_paused = True
            
    def update_display(self):
        hours = self.total_seconds // 3600
        minutes = (self.total_seconds % 3600) // 60
        seconds = self.total_seconds % 60
        self.hour_label.setText(f"{hours:02}")
        self.minute_label.setText(f"{minutes:02}")
        self.second_label.setText(f"{seconds:02}")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos is not None and event.buttons() & Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    timer_app = TimerApp()
    timer_app.show()
    sys.exit(app.exec())
