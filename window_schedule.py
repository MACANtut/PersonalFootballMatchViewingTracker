# window_schedule.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                               QLabel, QPushButton, QFrame, QWidget)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class ScheduleWindow(QDialog):
    back_to_profile = Signal()
    
    def __init__(self, user_data=None, db=None, parent=None):
        super().__init__(parent)
        self.user_data = user_data
        self.db = db
        self.setWindowTitle("График просмотренных матчей")
        self.setFixedSize(900, 900)
        self.setModal(True)
        self.initUI()
        self.create_empty_chart()
        
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
        
        # Верхняя панель с кнопкой назад и заголовком
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
        top_layout.addWidget(title_label)
        
        right_spacer = QWidget()
        right_spacer.setFixedSize(40, 40)
        right_spacer.setStyleSheet("background-color: transparent;")
        top_layout.addWidget(right_spacer)
        
        main_layout.addLayout(top_layout)
        
        # Основной контент
        self.content_frame = QFrame()
        self.content_frame.setObjectName("contentFrame")
        
        content_layout = QVBoxLayout(self.content_frame)
        content_layout.setSpacing(15)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # Создаем виджет для графика matplotlib
        self.figure = Figure(figsize=(6, 4), dpi=100, facecolor='#f0f5f0')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumHeight(350)
        content_layout.addWidget(self.canvas)
        
        main_layout.addWidget(self.content_frame)
    
    def create_empty_chart(self):
        """Создает пустой график с осями X и Y"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Создаем пустые данные для осей
        clubs = []
        counts = []
        
        # Создаем столбчатую диаграмму с пустыми данными
        bars = ax.bar(clubs, counts, color='#6b8f6b', edgecolor='#527352', linewidth=1.5)
        
        # Настройка осей
        ax.set_xlabel('Название клуба', fontsize=11, fontweight='bold', color='#2c4c3b')
        ax.set_ylabel('Количество просмотренных матчей', fontsize=11, fontweight='bold', color='#2c4c3b')
        ax.set_title('Статистика просмотренных матчей по клубам', fontsize=12, fontweight='bold', color='#1e4a2e', pad=15)
        
        # Устанавливаем пределы осей
        ax.set_xlim(-0.5, 0.5)
        ax.set_ylim(0, 10)
        
        # Добавляем сетку для удобства
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.grid(axis='x', alpha=0.3, linestyle='--')
        
        # Настраиваем подписи осей
        ax.set_xticks([])
        ax.set_yticks(range(0, 11, 2))
        ax.set_yticklabels(['0', '2', '4', '6', '8', '10'], fontsize=9, color='#2c4c3b')
        
        # Убираем верхнюю и правую границы
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#9bb89b')
        ax.spines['bottom'].set_color('#9bb89b')
        
        # Устанавливаем цвет фона
        ax.set_facecolor('#f0f5f0')
        self.figure.patch.set_facecolor('#f0f5f0')
        
        # Добавляем текст-подсказку в центр графика
        ax.text(0, 5, 'Здесь будет отображаться статистика\nпросмотренных матчей', 
               ha='center', va='center', fontsize=11, color='#8f9e8f',
               style='italic', alpha=0.7)
        
        # Настраиваем отступы
        self.figure.tight_layout()
        
        self.canvas.draw()
    
    def go_back(self):
        """Возвращает в окно профиля"""
        self.back_to_profile.emit()
        self.close()
    
    def closeEvent(self, event):
        """При закрытии окна возвращаемся в профиль"""
        self.back_to_profile.emit()
        super().closeEvent(event)