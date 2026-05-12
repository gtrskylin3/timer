import sys
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QDialog,
    QSpinBox,
    QDialogButtonBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor
from pathlib import Path
from datetime import date
import json

BASE_DIR = Path(__file__).parent.resolve()
DATA_DIR = BASE_DIR / "data.json"


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки")
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.background_widget = QWidget(self)
        self.background_widget.setObjectName("backgroundWidget")

        self.layout = QVBoxLayout(self.background_widget)
        self.layout.setContentsMargins(15, 10, 15, 15)

        # Top bar for close button
        # top_bar_layout = QHBoxLayout()
        # top_bar_layout.addStretch()
        self.close_button = QPushButton("x")
        self.close_button.setFixedSize(6, 7)
        self.close_button.clicked.connect(self.reject)
        # top_bar_layout.addWidget(self.close_button)
        # self.layout.addLayout(top_bar_layout)

        # Title
        title = QLabel("Установить время")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(title)

        time_layout = QHBoxLayout()
        self.hour_spinbox = self.create_spinbox(0, 23)
        self.minute_spinbox = self.create_spinbox(0, 59)
        self.second_spinbox = self.create_spinbox(0, 59)

        time_layout.addWidget(self.hour_spinbox)
        time_layout.addWidget(QLabel(":"))
        time_layout.addWidget(self.minute_spinbox)
        time_layout.addWidget(QLabel(":"))
        time_layout.addWidget(self.second_spinbox)

        self.layout.addLayout(time_layout)

        # Кнопка статистики
        self.stats_button = QPushButton("📊 Посмотреть статистику")
        self.stats_button.setFixedHeight(35)
        self.stats_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.stats_button.clicked.connect(self.show_statistics)
        self.layout.addWidget(self.stats_button)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.layout.addWidget(buttons)

        ok_button = buttons.button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setText("Применить")

        main_dialog_layout = QVBoxLayout(self)
        main_dialog_layout.addWidget(self.background_widget)
        main_dialog_layout.setContentsMargins(0, 0, 0, 0)

        self.setStyleSheet("""
            QWidget#backgroundWidget {
                background-color: #1e1e1e;
                border-radius: 10px;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
            QSpinBox {
                background-color: #2a2a2a;
                color: white;
                border: 1px solid #3c3c3c;
                border-radius: 5px;
                padding: 5px;
                font-size: 16px;
            }
            QPushButton {
                background-color: #3c3c3c;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 12px;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
        """)

        self.close_button.setStyleSheet("""
             QPushButton {
                background-color: #dc3545; color: black; border: none; border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)

        self.stats_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)

        for button in buttons.buttons():
            button.setCursor(Qt.CursorShape.PointingHandCursor)

        self.old_pos = None

    def create_spinbox(self, min_val, max_val):
        spinbox = QSpinBox()
        spinbox.setRange(min_val, max_val)
        spinbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return spinbox

    def get_time(self):
        return (
            self.hour_spinbox.value(),
            self.minute_spinbox.value(),
            self.second_spinbox.value(),
        )

    def show_statistics(self):
        stats_dialog = StatisticsDialog(self)
        stats_dialog.exec()

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


class StatisticsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Статистика использования")
        self.setMinimumWidth(450)
        self.setMinimumHeight(350)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.background_widget = QWidget(self)
        self.background_widget.setObjectName("backgroundWidget")

        layout = QVBoxLayout(self.background_widget)
        layout.setContentsMargins(15, 10, 15, 15)

        # Top bar
        top_bar_layout = QHBoxLayout()
        top_bar_layout.addStretch()
        self.close_button = QPushButton("x")
        self.close_button.setFixedSize(12, 14)
        self.close_button.clicked.connect(self.accept)
        top_bar_layout.addWidget(self.close_button)
        layout.addLayout(top_bar_layout)

        # Заголовок
        title = QLabel("📊 Статистика по дням")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Дата", "Время"])
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)

        layout.addWidget(self.table)

        # Итого
        self.total_label = QLabel()
        self.total_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.total_label)

        main_dialog_layout = QVBoxLayout(self)
        main_dialog_layout.addWidget(self.background_widget)
        main_dialog_layout.setContentsMargins(0, 0, 0, 0)

        self.setStyleSheet("""
            QWidget#backgroundWidget {
                background-color: #1e1e1e;
                border-radius: 10px;
            }
            QLabel {
                color: white;
                padding: 5px;
            }
            QTableWidget {
                background-color: #2a2a2a;
                color: white;
                border: none;
                gridline-color: #3c3c3c;
                border-radius: 5px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #3c3c3c;
            }
            QTableWidget::item:alternate {
                background-color: #2f2f2f;
            }
            QHeaderView::section {
                background-color: #3c3c3c;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)

        self.close_button.setStyleSheet("""
             QPushButton {
                background-color: #dc3545; color: white; border: none; border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)

        # Загрузка данных
        self.load_statistics()

        self.old_pos = None

    def load_statistics(self):
        stats = {}
        if DATA_DIR.exists():
            with open(DATA_DIR, "r", encoding="utf-8") as f:
                try:
                    stats = json.load(f)
                except json.JSONDecodeError:
                    stats = {}

        if not stats:
            self.table.setRowCount(1)
            self.table.setItem(0, 0, QTableWidgetItem("Нет данных"))
            self.table.setItem(0, 1, QTableWidgetItem("—"))
            self.total_label.setText("Всего: 0 часов")
            return

        sorted_dates = sorted(stats.keys(), reverse=True)
        self.table.setRowCount(len(sorted_dates))
        total_seconds = 0

        for row, date_str in enumerate(sorted_dates):
            seconds = stats[date_str]
            total_seconds += seconds

            try:
                date_obj = date.fromisoformat(date_str)
                formatted_date = date_obj.strftime("%d.%m.%Y")
            except:
                formatted_date = date_str

            date_item = QTableWidgetItem(formatted_date)
            date_item.setFlags(date_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

            h, m, s = seconds // 3600, (seconds % 3600) // 60, seconds % 60
            time_str = f"{h}ч {m}м"
            hours_item = QTableWidgetItem(time_str)
            hours_item.setFlags(hours_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            hours_item.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )

            self.table.setItem(row, 0, date_item)
            self.table.setItem(row, 1, hours_item)

        total_h, total_m = total_seconds // 3600, (total_seconds % 3600) // 60
        self.total_label.setText(f"Всего: {total_h}ч {total_m}м")

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


class TimerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Always on Top Timer")
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.total_seconds = 0
        self.is_paused = True
        self.is_stopwatch_mode = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)

        self.background_widget = QWidget(self)
        self.background_widget.setObjectName("backgroundWidget")
        self.background_widget.setStyleSheet(
            "#backgroundWidget { background-color: black; border-radius: 10px; }"
        )

        main_layout = QVBoxLayout(self.background_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Top bar for close button
        top_bar_layout = QHBoxLayout()
        top_bar_layout.addStretch()  # Push button to the right


        # Minimize button
        self.minimize_button = QPushButton("−")  # Minus symbol for minimize
        self.minimize_button.setFixedSize(12, 14)
        self.minimize_button.setStyleSheet("""
            QPushButton {
                background-color: black;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: black;
            }
        """)
        self.minimize_button.clicked.connect(self.showMinimized)
        top_bar_layout.addWidget(self.minimize_button)

        self.close_button = QPushButton("x")  # Text for close button
        self.close_button.setFixedSize(12, 14)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: black;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        self.close_button.clicked.connect(self.close)  # Connect to window close method
        top_bar_layout.addWidget(self.close_button)

        main_layout.addLayout(top_bar_layout)  # Add top bar to main layout

        time_layout = QHBoxLayout()
        self.hour_label = self.create_time_label("00")
        self.minute_label = self.create_time_label("00")
        self.second_label = self.create_time_label("00")

        time_layout.addStretch()
        time_layout.addWidget(self.hour_label)
        time_layout.addWidget(self.create_label(":"))
        time_layout.addWidget(self.minute_label)
        time_layout.addWidget(self.create_label(":"))
        time_layout.addWidget(self.second_label)
        time_layout.addStretch()

        button_layout = QHBoxLayout()
        self.play_pause_button = self.create_button("▶", "#5900ff")
        self.stop_button = self.create_button("■", "#dc7535")
        self.settings_button = self.create_button("⚙", "#048ec0")

        self.play_pause_button.clicked.connect(self.toggle_play_pause)
        self.stop_button.clicked.connect(self.stop_timer)
        self.settings_button.clicked.connect(self.open_settings)

        button_layout.addStretch()
        button_layout.addWidget(self.play_pause_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.settings_button)
        button_layout.addStretch()

        main_layout.addLayout(time_layout)
        main_layout.addLayout(button_layout)

        main_dialog_layout = QVBoxLayout(self)
        main_dialog_layout.addWidget(self.background_widget)
        main_dialog_layout.setContentsMargins(0, 0, 0, 0)

        self.old_pos = None
        self.update_display()

    def create_time_label(self, text):
        label = QLabel(text)
        label.setFont(QFont("Arial", 24))
        label.setStyleSheet("color: white;")
        return label

    def create_label(self, text):
        label = QLabel(text)
        label.setFont(QFont("Arial", 24))
        label.setStyleSheet("color: white;")
        return label

    def create_button(self, text, color):
        button = QPushButton(text)
        button.setFixedSize(30, 30)
        button.setFont(QFont("Arial", 12))
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: black;
                color: white;
                border: none;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: {QColor('black').lighter(115).name()};
            }}
        """)
        return button

    def toggle_play_pause(self):
        if self.is_paused:
            if self.total_seconds == 0 and not self.is_stopwatch_mode:
                self.is_stopwatch_mode = True

            self.timer.start(1000)
            self.play_pause_button.setText("II")
            self.is_paused = False
        else:  # Pausing
            self.timer.stop()
            self.play_pause_button.setText("▶")
            self.is_paused = True

    def save_stats(self, file_path=DATA_DIR):
        if not self.total_seconds:
            return

        # 1. Читаем существующие данные
        stats = {}
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    stats = json.load(f)
                except json.JSONDecodeError:
                    stats = {}  # Файл пуст или повреждён

        # 2. Обновляем статистику за сегодня
        today = str(date.today())  # Формат: 'YYYY-MM-DD'
        stats[today] = stats.get(today, 0) + self.total_seconds

        # 3. Сохраняем обратно
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2)

    def stop_timer(self):
        self.timer.stop()
        self.save_stats()
        self.total_seconds = 0
        self.is_stopwatch_mode = False  # Reset stopwatch mode
        self.update_display()
        if not self.is_paused:
            self.toggle_play_pause()  # Reset button to play
        self.is_paused = True

    def open_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec():
            hours, minutes, seconds = dialog.get_time()
            self.total_seconds = hours * 3600 + minutes * 60 + seconds
            self.is_stopwatch_mode = False  # Reset stopwatch mode when new time is set
            self.update_display()
            if not self.is_paused:
                self.toggle_play_pause()  # Stop timer and reset button if running
            self.is_paused = True

    def update_time(self):
        if self.is_stopwatch_mode:
            self.total_seconds += 1
            self.update_display()
        elif self.total_seconds > 0:  # Countdown mode
            self.total_seconds -= 1
            self.update_display()
        else:  # Countdown finished
            self.timer.stop()
            if not self.is_paused:
                self.toggle_play_pause()  # Reset button to play
            self.is_paused = True

    def get_format_time(self, total_seconds):
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return hours, minutes, seconds

    def update_display(self):
        hours, minutes, seconds = self.get_format_time(self.total_seconds)
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    timer_app = TimerApp()
    timer_app.show()
    sys.exit(app.exec())
