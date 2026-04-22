# window_schedule.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                               QLabel, QPushButton, QFrame, QWidget,
                               QMessageBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPainter, QPixmap
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np


class ScheduleWindow(QDialog):
    back_to_profile = Signal()

    def __init__(self, user_data=None, db=None, parent=None):
        super().__init__(parent)
        self.user_data = user_data
        self.db = db
        self.background_pixmap = None
        self.setWindowTitle("График просмотренных матчей")
        self.setFixedSize(800, 600)
        self.setModal(True)
        self.initUI()
        self.load_chart_data()

    def _setup_message_box(self, msg_box, text):
        lines = text.split('\n')
        max_line_length = max(len(line) for line in lines) if lines else len(text)
        width = min(max_line_length * 8 + 80, 500)
        height = len(lines) * 25 + 80
        msg_box.setMinimumWidth(width)
        msg_box.setMaximumWidth(min(width + 50, 600))
        msg_box.setMinimumHeight(height)
        msg_box.setMaximumHeight(min(height + 50, 500))
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #e8f0e8;
            }
            QMessageBox QLabel {
                color: #2c4c3b;
                font-weight: bold;
                font-size: 12px;
                padding: 15px;
                word-wrap: break-word;
            }
            QPushButton {
                background-color: #6b8f6b;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 25px;
                font-weight: bold;
                font-size: 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #527352;
            }
        """)
        msg_box.addButton("ОК", QMessageBox.AcceptRole)

    def initUI(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #e8f0e8;
            }
            QFrame#contentFrame {
                background-color: #f0f5f0;
                border: 2px solid #9bb89b;
                border-radius: 10px;
            }
            QLabel {
                color: #2c4c3b;
                font-size: 12px;
            }
            QLabel#titleLabel {
                color: #1e4a2e;
                font-size: 20px;
                font-weight: bold;
                padding: 8px 20px;
                background-color: rgba(150, 180, 150, 0.3);
                border-radius: 8px;
            }
            QPushButton#backButton {
                background-color: #8f9e8f;
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 28px;
                font-weight: bold;
                padding: 0px;
                min-width: 40px;
                min-height: 40px;
                max-width: 40px;
                max-height: 40px;
            }
            QPushButton#backButton:hover {
                background-color: #748774;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)

        self.back_button = QPushButton(" ⇦")
        self.back_button.setObjectName("backButton")
        font = QFont()
        font.setBold(True)
        font.setPointSize(28)
        self.back_button.setFont(font)
        self.back_button.clicked.connect(self.go_back)
        top_layout.addWidget(self.back_button)

        title_label = QLabel("График просмотренных матчей")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        top_layout.addWidget(title_label, 1)

        spacer_widget = QWidget()
        spacer_widget.setFixedSize(40, 40)
        top_layout.addWidget(spacer_widget)

        main_layout.addLayout(top_layout)

        self.content_frame = QFrame()
        self.content_frame.setObjectName("contentFrame")

        content_layout = QVBoxLayout(self.content_frame)
        content_layout.setSpacing(15)
        content_layout.setContentsMargins(20, 20, 20, 20)

        self.figure = Figure(figsize=(7, 5), dpi=100, facecolor='#f0f5f0')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumHeight(450)
        content_layout.addWidget(self.canvas)

        main_layout.addWidget(self.content_frame)

    def load_chart_data(self):
        if not self.user_data or not self.db:
            self.show_empty_chart("Нет данных пользователя")
            return

        try:
            events = self.db.get_user_events(self.user_data['id'])

            if not events:
                self.show_empty_chart("У вас пока нет добавленных событий")
                return

            team_counts = {}

            for event in events:
                team1 = event['team1']
                team2 = event['team2']

                team_counts[team1] = team_counts.get(team1, 0) + 1
                team_counts[team2] = team_counts.get(team2, 0) + 1

            sorted_teams = sorted(team_counts.items(), key=lambda x: x[1], reverse=True)
            top_teams = sorted_teams[:5]

            if not top_teams:
                self.show_empty_chart("Нет данных для отображения")
                return

            teams = [team for team, count in top_teams]
            counts = [count for team, count in top_teams]

            self.create_bar_chart(teams, counts)

        except Exception:
            self.show_empty_chart("Ошибка загрузки данных")

    def create_bar_chart(self, teams, counts):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        colors = plt.cm.Greens(np.linspace(0.4, 0.9, len(teams)))

        bars = ax.bar(teams, counts, color=colors, edgecolor='#2c4c3b', linewidth=1.5)

        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.3,
                    str(count), ha='center', va='bottom',
                    fontsize=10, fontweight='bold', color='#2c4c3b')

        ax.set_xlabel('Название клуба', fontsize=12, fontweight='bold', color='#2c4c3b')
        ax.set_ylabel('Количество упоминаний', fontsize=12, fontweight='bold', color='#2c4c3b')
        ax.set_title('Топ-5 команд по частоте добавления в события',
                    fontsize=14, fontweight='bold', color='#1e4a2e', pad=20)

        ax.set_xticklabels(teams, rotation=15, ha='right', fontsize=10)

        max_count = max(counts) if counts else 1
        ax.set_ylim(0, max_count + 2)
        ax.set_yticks(range(0, max_count + 3, 1))

        ax.grid(axis='y', alpha=0.3, linestyle='--', color='#9bb89b')
        ax.set_axisbelow(True)

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#9bb89b')
        ax.spines['bottom'].set_color('#9bb89b')

        ax.set_facecolor('#f0f5f0')
        self.figure.patch.set_facecolor('#f0f5f0')

        self.figure.tight_layout()
        self.canvas.draw()

    def show_empty_chart(self, message):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        ax.set_xlabel('Название клуба', fontsize=12, fontweight='bold', color='#2c4c3b')
        ax.set_ylabel('Количество упоминаний', fontsize=12, fontweight='bold', color='#2c4c3b')
        ax.set_title('Топ-5 команд по частоте добавления в события',
                    fontsize=14, fontweight='bold', color='#1e4a2e', pad=20)

        ax.set_xlim(-0.5, 0.5)
        ax.set_ylim(0, 10)

        ax.grid(axis='y', alpha=0.3, linestyle='--', color='#9bb89b')
        ax.grid(axis='x', alpha=0.3, linestyle='--', color='#9bb89b')

        ax.set_xticks([])
        ax.set_yticks(range(0, 11, 2))
        ax.set_yticklabels(['0', '2', '4', '6', '8', '10'], fontsize=9, color='#2c4c3b')

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#9bb89b')
        ax.spines['bottom'].set_color('#9bb89b')

        ax.set_facecolor('#f0f5f0')
        self.figure.patch.set_facecolor('#f0f5f0')

        ax.text(0, 5, message,
               ha='center', va='center', fontsize=12, color='#8f9e8f',
               style='italic', alpha=0.7)

        self.figure.tight_layout()
        self.canvas.draw()

    def go_back(self):
        self.back_to_profile.emit()
        self.close()

    def paintEvent(self, event):
        if self.background_pixmap and not self.background_pixmap.isNull():
            painter = QPainter(self)
            scaled_pixmap = self.background_pixmap.scaled(
                self.size(),
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )
            x = (self.width() - scaled_pixmap.width()) // 2
            y = (self.height() - scaled_pixmap.height()) // 2
            painter.drawPixmap(x, y, scaled_pixmap)
        else:
            super().paintEvent(event)

    def set_background_pixmap(self, pixmap):
        if pixmap and not pixmap.isNull():
            self.background_pixmap = pixmap
            self.update()

    def resizeEvent(self, event):
        if self.background_pixmap and not self.background_pixmap.isNull():
            self.update()
        super().resizeEvent(event)

    def closeEvent(self, event):
        self.back_to_profile.emit()
        super().closeEvent(event)