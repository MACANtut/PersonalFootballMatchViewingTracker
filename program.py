import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QLabel, QFrame)
from PySide6.QtCore import Qt
from window_rols import RulesWindow  # Импортируем окно правил

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Персональный трекер футбольных матчей")
        self.setFixedSize(900, 600)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Установка зеленовато-бело-серой цветовой гаммы (как в окне авторизации)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #e8f0e8;
            }
            QFrame#leftPanel {
                background-color: #d0e0d0;  /* Светло-зеленый для левой панели */
                border-right: 2px solid #9bb89b;
            }
            QFrame#rightPanel {
                background-color: #e8f0e8;  /* Основной фон */
            }
            QLabel {
                color: #2c4c3b;
                font-weight: bold;
            }
            QLabel#avatar {
                background-color: #ffffff;
                border: 3px solid #6b8f6b;
                color: #2c4c3b;
                font-size: 40px;
            }
            QLabel#avatar:hover {
                background-color: #f0f8f0;
                border-color: #527352;
            }
            QLabel#eventsTitle {
                color: #2c4c3b;
                font-size: 18px;
                font-weight: bold;
                background-color: rgba(150, 180, 150, 0.3);
                padding: 10px;
                border-radius: 8px;
            }
            QLabel#eventCircle {
                background-color: #ffffff;
                border: 3px solid #6b8f6b;
                color: #2c4c3b;
                font-size: 36px;
                font-weight: bold;
            }
            QPushButton {
                background-color: #6b8f6b;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
                font-size: 14px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #527352;
            }
            QPushButton:pressed {
                background-color: #3e5a3e;
            }
            QPushButton:disabled {
                background-color: #9bb89b;
                color: #e8f0e8;
            }
            QPushButton#adminButton {
                background-color: #8f9e8f;
            }
            QPushButton#adminButton:hover {
                background-color: #748774;
            }
            QPushButton#settingsButton {
                background-color: #6b8f6b;
                color: white;
                font-size: 20px;
                border-radius: 20px;
            }
            QPushButton#settingsButton:hover {
                background-color: #527352;
            }
            QPushButton#settingsButton:disabled {
                background-color: #9bb89b;
            }
        """)
        
        # Главный горизонтальный layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ЛЕВАЯ ПАНЕЛЬ С КНОПКАМИ
        left_panel = QFrame()
        left_panel.setObjectName("leftPanel")
        left_panel.setFixedWidth(250)
        
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(20, 30, 20, 30)
        left_layout.setSpacing(10)
        left_layout.setAlignment(Qt.AlignTop)
        
        # Кликабельная аватарка
        avatar = QLabel("👤")
        avatar.setObjectName("avatar")
        avatar.setFixedSize(80, 80)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setCursor(Qt.PointingHandCursor)
        avatar.mousePressEvent = self.avatar_clicked
        left_layout.addWidget(avatar, 0, Qt.AlignHCenter)
        
        left_layout.addSpacing(20)
        
        # Кнопки для всех пользователей
        chat_button = QPushButton("Чат пользователей")
        chat_button.setEnabled(False)
        chat_button.setFixedHeight(40)
        chat_button.setStyleSheet("padding-left: 15px;")
        left_layout.addWidget(chat_button)
        
        add_event_button = QPushButton("Добавить событие")
        add_event_button.setEnabled(False)
        add_event_button.setFixedHeight(40)
        add_event_button.setStyleSheet("padding-left: 15px;")
        left_layout.addWidget(add_event_button)
        
        # Кнопка "Правила" - теперь активная
        rules_button = QPushButton("Правила")
        rules_button.setEnabled(True)  # Включаем кнопку
        rules_button.setFixedHeight(40)
        rules_button.setStyleSheet("padding-left: 15px;")
        rules_button.clicked.connect(self.open_rules_window)  # Подключаем обработчик
        left_layout.addWidget(rules_button)
        
        left_layout.addSpacing(10)
        
        # Дополнительные кнопки для администратора
        clubs_button = QPushButton("Список клубов")
        clubs_button.setObjectName("adminButton")
        clubs_button.setEnabled(False)
        clubs_button.setFixedHeight(40)
        clubs_button.setStyleSheet("padding-left: 15px;")
        left_layout.addWidget(clubs_button)
        
        players_button = QPushButton("Игроки")
        players_button.setObjectName("adminButton")
        players_button.setEnabled(False)
        players_button.setFixedHeight(40)
        players_button.setStyleSheet("padding-left: 15px;")
        left_layout.addWidget(players_button)
        
        users_button = QPushButton("Список пользователей")
        users_button.setObjectName("adminButton")
        users_button.setEnabled(False)
        users_button.setFixedHeight(40)
        users_button.setStyleSheet("padding-left: 15px;")
        left_layout.addWidget(users_button)
        
        left_layout.addStretch()
        
        # ПРАВАЯ ПАНЕЛЬ
        right_panel = QFrame()
        right_panel.setObjectName("rightPanel")
        
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(20, 20, 20, 20)
        
        # Верхняя панель с кнопкой настройки фона
        top_bar = QHBoxLayout()
        top_bar.addStretch()
        
        # Кнопка настройки фона в виде шестеренки
        settings_button = QPushButton("⚙️")
        settings_button.setObjectName("settingsButton")
        settings_button.setEnabled(False)
        settings_button.setFixedSize(40, 40)
        settings_button.setStyleSheet("""
            QPushButton {
                qproperty-alignment: AlignCenter;
                padding: 0px;
            }
        """)
        top_bar.addWidget(settings_button)
        
        right_layout.addLayout(top_bar)
        
        right_layout.addSpacing(20)
        
        # Заголовок "Ваши события"
        events_title = QLabel("Ваши события")
        events_title.setObjectName("eventsTitle")
        events_title.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(events_title)
        
        right_layout.addSpacing(20)
        
        # Контейнер для событий (1 и 2) - большие круги
        events_container = QWidget()
        events_layout = QHBoxLayout(events_container)
        events_layout.setSpacing(40)
        events_layout.setAlignment(Qt.AlignCenter)
        
        for i in ["1", "2"]:
            circle_container = QVBoxLayout()
            
            circle = QLabel(i)
            circle.setObjectName("eventCircle")
            circle.setFixedSize(100, 100)
            circle.setAlignment(Qt.AlignCenter)
            circle_container.addWidget(circle, 0, Qt.AlignCenter)
            
            events_layout.addLayout(circle_container)
        
        right_layout.addWidget(events_container)
        right_layout.addStretch()
        
        # Добавляем панели
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel, 1)
        
        # Переменная для хранения ссылки на окно правил
        self.rules_window = None
    
    def avatar_clicked(self, event):
        print("Переход в профиль (заглушка)")
    
    def open_rules_window(self):
        """Открывает окно с правилами"""
        if self.rules_window is None or not self.rules_window.isVisible():
            self.rules_window = RulesWindow()
            self.rules_window.show()
        else:
            # Если окно уже открыто, просто активируем его
            self.rules_window.raise_()
            self.rules_window.activateWindow()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Устанавливаем стиль Fusion для более современного вида
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())