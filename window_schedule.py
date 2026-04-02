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
        self.setFixedSize(900, 900)
        self.setModal(True)
        self.initUI()
        self.load_chart_data()
        
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
            QLabel#statsLabel {
                color: #2c4c3b;
                font-size: 13px;
                font-weight: bold;
                padding: 10px;
                background-color: rgba(255, 255, 255, 0.8);
                border-radius: 8px;
                border: 1px solid #9bb89b;
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
            QPushButton#refreshButton {
                background-color: #6b8f6b;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton#refreshButton:hover {
                background-color: #527352;
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
        
        # Кнопка обновления
        self.refresh_button = QPushButton("🔄 Обновить")
        self.refresh_button.setObjectName("refreshButton")
        self.refresh_button.setFixedSize(120, 40)
        self.refresh_button.clicked.connect(self.load_chart_data)
        top_layout.addWidget(self.refresh_button)
        
        main_layout.addLayout(top_layout)
        
        # Основной контент
        self.content_frame = QFrame()
        self.content_frame.setObjectName("contentFrame")
        
        content_layout = QVBoxLayout(self.content_frame)
        content_layout.setSpacing(15)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # Создаем виджет для графика matplotlib
        self.figure = Figure(figsize=(6, 5), dpi=100, facecolor='#f0f5f0')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumHeight(400)
        content_layout.addWidget(self.canvas)
        
        # Статистическая информация
        self.stats_label = QLabel("")
        self.stats_label.setObjectName("statsLabel")
        self.stats_label.setAlignment(Qt.AlignCenter)
        self.stats_label.setWordWrap(True)
        self.stats_label.setMinimumHeight(80)
        content_layout.addWidget(self.stats_label)
        
        main_layout.addWidget(self.content_frame)
    
    def load_chart_data(self):
        """Загружает данные о событиях пользователя и строит график топ-5 команд"""
        if not self.user_data or not self.db:
            self.show_empty_chart("Нет данных пользователя")
            return
        
        try:
            # Получаем все события пользователя
            events = self.db.get_user_events(self.user_data['id'])
            
            if not events:
                self.show_empty_chart("У вас пока нет добавленных событий")
                return
            
            # Подсчитываем частоту появления команд
            team_counts = {}
            
            for event in events:
                team1 = event['team1']
                team2 = event['team2']
                
                team_counts[team1] = team_counts.get(team1, 0) + 1
                team_counts[team2] = team_counts.get(team2, 0) + 1
            
            # Сортируем по убыванию и берем топ-5
            sorted_teams = sorted(team_counts.items(), key=lambda x: x[1], reverse=True)
            top_teams = sorted_teams[:5]
            
            if not top_teams:
                self.show_empty_chart("Нет данных для отображения")
                return
            
            # Подготавливаем данные для графика
            teams = [team for team, count in top_teams]
            counts = [count for team, count in top_teams]
            
            # Строим график
            self.create_bar_chart(teams, counts)
            
            # Обновляем текстовую статистику
            total_matches = len(events)
            total_views = sum(counts)
            
            stats_text = f"📊 Статистика:\n"
            stats_text += f"• Всего событий: {total_matches}\n"
            stats_text += f"• Всего упоминаний команд: {total_views}\n"
            stats_text += f"• Уникальных команд: {len(team_counts)}\n\n"
            stats_text += f"🏆 Топ-5 команд:\n"
            
            for i, (team, count) in enumerate(top_teams, 1):
                percentage = (count / total_views) * 100 if total_views > 0 else 0
                stats_text += f"{i}. {team} - {count} раз(а) ({percentage:.1f}%)\n"
            
            self.stats_label.setText(stats_text)
            
        except Exception as e:
            print(f"Ошибка загрузки данных для графика: {e}")
            self.show_empty_chart(f"Ошибка загрузки данных: {str(e)}")
    
    def create_bar_chart(self, teams, counts):
        """Создает столбчатую диаграмму с топ-5 командами"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Создаем градиент цветов от темно-зеленого к светло-зеленому
        colors = plt.cm.Greens(np.linspace(0.4, 0.9, len(teams)))
        
        # Создаем столбчатую диаграмму
        bars = ax.bar(teams, counts, color=colors, edgecolor='#2c4c3b', linewidth=1.5)
        
        # Добавляем значения на столбцы
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.3,
                    str(count), ha='center', va='bottom', 
                    fontsize=10, fontweight='bold', color='#2c4c3b')
        
        # Настройка осей
        ax.set_xlabel('Название клуба', fontsize=12, fontweight='bold', color='#2c4c3b')
        ax.set_ylabel('Количество упоминаний', fontsize=12, fontweight='bold', color='#2c4c3b')
        ax.set_title('Топ-5 команд по частоте добавления в события', 
                    fontsize=14, fontweight='bold', color='#1e4a2e', pad=20)
        
        # Поворачиваем подписи на оси X для лучшей читаемости
        ax.set_xticklabels(teams, rotation=15, ha='right', fontsize=10)
        
        # Устанавливаем целые значения на оси Y
        max_count = max(counts) if counts else 1
        ax.set_ylim(0, max_count + 2)
        ax.set_yticks(range(0, max_count + 3, 1))
        
        # Добавляем сетку для удобства
        ax.grid(axis='y', alpha=0.3, linestyle='--', color='#9bb89b')
        ax.set_axisbelow(True)
        
        # Убираем верхнюю и правую границы
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#9bb89b')
        ax.spines['bottom'].set_color('#9bb89b')
        
        # Устанавливаем цвет фона
        ax.set_facecolor('#f0f5f0')
        self.figure.patch.set_facecolor('#f0f5f0')
        
        # Настраиваем отступы
        self.figure.tight_layout()
        
        self.canvas.draw()
    
    def show_empty_chart(self, message):
        """Показывает пустой график с сообщением"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Создаем пустые данные для осей
        ax.set_xlabel('Название клуба', fontsize=12, fontweight='bold', color='#2c4c3b')
        ax.set_ylabel('Количество упоминаний', fontsize=12, fontweight='bold', color='#2c4c3b')
        ax.set_title('Топ-5 команд по частоте добавления в события', 
                    fontsize=14, fontweight='bold', color='#1e4a2e', pad=20)
        
        # Устанавливаем пределы осей
        ax.set_xlim(-0.5, 0.5)
        ax.set_ylim(0, 10)
        
        # Добавляем сетку
        ax.grid(axis='y', alpha=0.3, linestyle='--', color='#9bb89b')
        ax.grid(axis='x', alpha=0.3, linestyle='--', color='#9bb89b')
        
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
        ax.text(0, 5, message, 
               ha='center', va='center', fontsize=12, color='#8f9e8f',
               style='italic', alpha=0.7)
        
        # Настраиваем отступы
        self.figure.tight_layout()
        
        self.canvas.draw()
        
        # Очищаем текстовую статистику
        self.stats_label.setText("")
    
    def go_back(self):
        """Возвращает в окно профиля"""
        self.back_to_profile.emit()
        self.close()
    
    def paintEvent(self, event):
        """Рисует фон"""
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
        """Устанавливает фоновое изображение"""
        if pixmap and not pixmap.isNull():
            self.background_pixmap = pixmap
            self.update()
    
    def resizeEvent(self, event):
        """Обновляет фон при изменении размера"""
        if self.background_pixmap and not self.background_pixmap.isNull():
            self.update()
        super().resizeEvent(event)
    
    def closeEvent(self, event):
        """При закрытии окна возвращаемся в профиль"""
        self.back_to_profile.emit()
        super().closeEvent(event)