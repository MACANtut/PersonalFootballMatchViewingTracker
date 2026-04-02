# window_events.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QPushButton, QFrame, QScrollArea,
                               QSizePolicy, QDialog)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPainter, QPixmap
from add_event_window import AddEventWindow


class EventWidget(QFrame):
    """Виджет для отображения одного события"""
    def __init__(self, event_data, parent=None):
        super().__init__(parent)
        self.event_data = event_data
        self.initUI()
        
    def initUI(self):
        self.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 2px solid #9bb89b;
                border-radius: 8px;
                margin: 2px 0px;
            }
            QFrame:hover {
                background-color: #f0f8f0;
                border-color: #6b8f6b;
            }
            QLabel {
                color: #2c4c3b;
                font-size: 12px;
                padding: 5px;
            }
            QLabel#teamLabel {
                font-weight: bold;
                font-size: 13px;
            }
            QLabel#scoreLabel {
                font-weight: bold;
                color: #1e4a2e;
                font-size: 14px;
            }
            QLabel#statusLabel {
                color: #6b8f6b;
                font-style: italic;
            }
            QLabel#dateLabel {
                color: #8f9e8f;
                font-size: 11px;
            }
            QLabel#commentLabel {
                color: #527352;
                font-size: 11px;
                font-style: italic;
                background-color: #f0f5f0;
                padding: 5px 8px;
                border-radius: 4px;
                margin-top: 3px;
            }
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 10, 15, 10)
        main_layout.setSpacing(5)
        
        # Верхняя строка с командами, счетом, статусом и датой
        top_layout = QHBoxLayout()
        top_layout.setSpacing(15)
        
        teams_label = QLabel(f"{self.event_data['team1']} - {self.event_data['team2']}")
        teams_label.setObjectName("teamLabel")
        teams_label.setMinimumWidth(200)
        top_layout.addWidget(teams_label)
        
        score_text = f"{self.event_data['score1']}:{self.event_data['score2']}"
        if self.event_data['status'] == "Запланирован":
            score_text = "?:?"
        score_label = QLabel(score_text)
        score_label.setObjectName("scoreLabel")
        score_label.setMinimumWidth(50)
        score_label.setAlignment(Qt.AlignCenter)
        top_layout.addWidget(score_label)
        
        status_label = QLabel(self.event_data['status'])
        status_label.setObjectName("statusLabel")
        status_label.setMinimumWidth(100)
        top_layout.addWidget(status_label)
        
        top_layout.addStretch()
        
        if self.event_data.get('created_at'):
            date_str = self.event_data['created_at'].strftime("%d.%m.%Y %H:%M")
        else:
            date_str = "Дата не указана"
        date_label = QLabel(date_str)
        date_label.setObjectName("dateLabel")
        top_layout.addWidget(date_label)
        
        main_layout.addLayout(top_layout)
        
        # Комментарий, если есть
        if self.event_data.get('comment') and self.event_data['comment'].strip():
            comment_label = QLabel(f" {self.event_data['comment']}")
            comment_label.setObjectName("commentLabel")
            comment_label.setWordWrap(True)
            main_layout.addWidget(comment_label)


class EventsWindow(QWidget):
    """Окно со списком событий пользователя"""
    event_added = Signal()
    
    def __init__(self, user_data=None, db=None, parent=None):
        super().__init__(parent)
        self.user_data = user_data
        self.db = db
        self.background_pixmap = None
        self.events_list = []
        self.add_event_dialog = None
        self.initUI()
        self.load_events()
        
    def initUI(self):
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
            QLabel#eventsTitle {
                color: #1e4a2e;
                font-size: 20px;
                font-weight: bold;
                padding: 8px 20px;
                background-color: rgba(150, 180, 150, 0.3);
                border-radius: 8px;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #d0e0d0;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background-color: #6b8f6b;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #527352;
            }
            QPushButton#addEventButton {
                background-color: #6b8f6b;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 13px;
                min-width: 160px;
            }
            QPushButton#addEventButton:hover {
                background-color: #527352;
            }
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(15)
        
        # Заголовок
        events_title = QLabel("Ваши события")
        events_title.setObjectName("eventsTitle")
        events_title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(events_title)
        
        # Область со списком событий
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameStyle(QFrame.NoFrame)
        scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.events_container = QWidget()
        self.events_container.setStyleSheet("background-color: transparent;")
        self.events_layout = QVBoxLayout(self.events_container)
        self.events_layout.setSpacing(5)
        self.events_layout.setContentsMargins(5, 5, 5, 5)
        self.events_layout.addStretch()
        
        scroll_area.setWidget(self.events_container)
        main_layout.addWidget(scroll_area)
        
        # Кнопка добавления события (справа снизу)
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 10, 0, 0)
        button_layout.addStretch()
        
        self.add_event_button = QPushButton("+ Добавить событие")
        self.add_event_button.setObjectName("addEventButton")
        self.add_event_button.clicked.connect(self.open_add_event_dialog)
        button_layout.addWidget(self.add_event_button)
        
        main_layout.addWidget(button_container)
    
    def set_background_pixmap(self, pixmap):
        """Устанавливает фоновое изображение"""
        if pixmap and not pixmap.isNull():
            self.background_pixmap = pixmap
            self.update()
    
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
    
    def resizeEvent(self, event):
        """Обновляет фон при изменении размера"""
        if self.background_pixmap and not self.background_pixmap.isNull():
            self.update()
        super().resizeEvent(event)
    
    def load_events(self):
        """Загружает события пользователя из базы данных"""
        if self.user_data and self.db and self.user_data.get('id'):
            try:
                self.events_list = self.db.get_user_events(self.user_data['id'])
                self.update_events_display()
            except Exception as e:
                print(f"Ошибка загрузки событий: {e}")
                self.events_list = []
    
    def update_events_display(self):
        """Обновляет отображение списка событий"""
        # Очищаем контейнер, оставляя только stretch
        while self.events_layout.count() > 1:
            item = self.events_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not self.events_list:
            no_events_label = QLabel("У вас пока нет добавленных событий")
            no_events_label.setAlignment(Qt.AlignCenter)
            no_events_label.setStyleSheet("""
                QLabel {
                    color: #8f9e8f;
                    font-size: 14px;
                    font-style: italic;
                    padding: 30px;
                    background-color: rgba(255, 255, 255, 0.7);
                    border: 2px dashed #9bb89b;
                    border-radius: 8px;
                }
            """)
            self.events_layout.insertWidget(0, no_events_label)
        else:
            for event in self.events_list:
                event_widget = EventWidget(event)
                self.events_layout.insertWidget(self.events_layout.count() - 1, event_widget)
    
    def open_add_event_dialog(self):
        """Открывает диалоговое окно для добавления события"""
        self.add_event_dialog = AddEventWindow(self)
        self.add_event_dialog.set_user_data(self.user_data)
        self.add_event_dialog.set_database(self.db)
        
        if self.background_pixmap:
            self.add_event_dialog.set_background_pixmap(self.background_pixmap)
        
        if self.add_event_dialog.exec() == QDialog.Accepted:
            self.load_events()
            self.event_added.emit()