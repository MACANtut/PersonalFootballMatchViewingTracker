# program.py
import os
import sys

sys.dont_write_bytecode = True

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QPushButton, QLabel, QFrame,
                               QGridLayout, QLineEdit, QMessageBox, QDialog,
                               QScrollArea, QStackedWidget, QSizePolicy)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QPainter, QPalette, QBrush, QFont, QPainterPath, QIcon
from database import Database
from window_chat import ChatWindow
from window_profile import ProfileWindow
from windows_users import UsersWindow
from window_players import PlayersWindow
from window_clubs import ClubsWindow
from background_settings import BackgroundDialog
from add_event_window import AddEventWindow
from window_events import EventsWindow


class StyledMessageBox:
    @staticmethod
    def _get_text_size(text, font=None):
        if not font:
            font = QFont("Segoe UI", 12)
        lines = text.split('\n')
        max_line_length = max(len(line) for line in lines) if lines else len(text)
        width = min(max_line_length * 8 + 80, 500)
        height = len(lines) * 25 + 80
        return width, height

    @staticmethod
    def _setup_message_box(msg_box, title, text, icon):
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        msg_box.setIcon(icon)

        width, height = StyledMessageBox._get_text_size(text)

        msg_box.setMinimumWidth(width)
        msg_box.setMaximumWidth(min(width + 100, 600))
        msg_box.setMinimumHeight(height)
        msg_box.setMaximumHeight(min(height + 100, 500))

        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #e8f0e8;
                min-width: 250px;
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
            QPushButton:pressed {
                background-color: #3e5a3e;
            }
        """)

        layout = msg_box.layout()
        if layout:
            layout.setSpacing(10)
            layout.setContentsMargins(20, 15, 20, 15)

    @staticmethod
    def information(parent, title, text):
        msg_box = QMessageBox(parent)
        StyledMessageBox._setup_message_box(msg_box, title, text, QMessageBox.Information)
        ok_button = msg_box.addButton("ОК", QMessageBox.AcceptRole)
        msg_box.exec()
        return msg_box.clickedButton() == ok_button

    @staticmethod
    def warning(parent, title, text):
        msg_box = QMessageBox(parent)
        StyledMessageBox._setup_message_box(msg_box, title, text, QMessageBox.Warning)
        ok_button = msg_box.addButton("ОК", QMessageBox.AcceptRole)
        msg_box.exec()
        return msg_box.clickedButton() == ok_button

    @staticmethod
    def critical(parent, title, text):
        msg_box = QMessageBox(parent)
        StyledMessageBox._setup_message_box(msg_box, title, text, QMessageBox.Critical)
        ok_button = msg_box.addButton("ОК", QMessageBox.AcceptRole)
        msg_box.exec()
        return msg_box.clickedButton() == ok_button

    @staticmethod
    def question(parent, title, text):
        msg_box = QMessageBox(parent)
        StyledMessageBox._setup_message_box(msg_box, title, text, QMessageBox.Question)

        width, height = StyledMessageBox._get_text_size(text)
        msg_box.setMinimumWidth(width + 50)

        yes_button = msg_box.addButton("Да", QMessageBox.YesRole)
        no_button = msg_box.addButton("Нет", QMessageBox.NoRole)
        no_button.setObjectName("noButton")

        no_button.setStyleSheet("""
            QPushButton {
                background-color: #8f9e8f;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 25px;
                font-weight: bold;
                font-size: 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #748774;
            }
        """)

        msg_box.setDefaultButton(no_button)
        msg_box.exec()
        return msg_box.clickedButton() == yes_button


class BackgroundFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.background_pixmap = None
        self.setAttribute(Qt.WA_OpaquePaintEvent, False)

    def set_background_image(self, pixmap):
        self.background_pixmap = pixmap
        self.update()

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


class MainWindow(QMainWindow):
    def __init__(self, user_data=None, db=None):
        super().__init__()
        self.user_data = user_data
        self.db = db
        self.setWindowTitle("Персональный трекер футбольных матчей")
        self.setMinimumSize(1200, 700)
        self.resize(1300, 750)

        # Установка иконки приложения
        icon_path = r"Эмблемы\icon.ico"
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            # Альтернативный путь - ищем иконку в папке с программой
            local_icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Эмблемы", "icon.ico")
            if os.path.exists(local_icon_path):
                self.setWindowIcon(QIcon(local_icon_path))

        self.is_admin = (user_data and user_data.get('username') == 'admin')

        self.chat_widget = None
        self.users_widget = None
        self.players_widget = None
        self.clubs_widget = None
        self.add_event_widget = None
        self.background_pixmap = None
        self.background_path = None
        self.avatar_pixmap = None
        
        # Словарь для отслеживания состояния фона в каждом виджете
        self.widget_background_set = {
            'events': False,
            'chat': False,
            'users': False,
            'players': False,
            'clubs': False,
            'add_event': False
        }
        
        # Текущее активное окно
        self.current_widget_name = None

        if self.db and self.user_data:
            avatar_path = self.db.get_user_avatar_path(self.user_data['id'])
            if avatar_path and os.path.exists(avatar_path):
                pixmap = QPixmap(avatar_path)
                if not pixmap.isNull():
                    self.avatar_pixmap = self.create_circular_avatar(pixmap)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #e8f0e8;
            }
            QFrame#leftPanel {
                background-color: #d0e0d0;
                border-right: 2px solid #9bb89b;
            }
            QLabel {
                color: #2c4c3b;
                font-weight: bold;
            }
            QLabel#avatar {
                background-color: #ffffff;
                border: 3px solid #6b8f6b;
                color: #2c4c3b;
                border-radius: 40px;
            }
            QLabel#avatar:hover {
                background-color: #f0f8f0;
                border-color: #527352;
            }
            QLabel#eventsTitle {
                color: #2c4c3b;
                font-size: 18px;
                font-weight: bold;
                background-color: rgba(150, 180, 150, 0.8);
                padding: 10px;
                border-radius: 8px;
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
                padding-left: 15px;
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
            QPushButton#settingsButton {
                background-color: #6b8f6b;
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 24px;
                font-weight: bold;
                padding: 0px;
                min-width: 40px;
                min-height: 40px;
                max-width: 40px;
                max-height: 40px;
            }
            QPushButton#settingsButton:hover {
                background-color: #527352;
            }
            QPushButton#settingsButton:disabled {
                background-color: #9bb89b;
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
        """)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        left_panel = QFrame()
        left_panel.setObjectName("leftPanel")
        left_panel.setMinimumWidth(200)
        left_panel.setMaximumWidth(280)

        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(20, 30, 20, 30)
        left_layout.setSpacing(10)

        self.avatar_label = QLabel()
        self.avatar_label.setObjectName("avatar")
        self.avatar_label.setFixedSize(80, 80)
        self.avatar_label.setAlignment(Qt.AlignCenter)
        self.avatar_label.setCursor(Qt.PointingHandCursor)
        self.avatar_label.mousePressEvent = self.avatar_clicked
        self.update_avatar_display()
        left_layout.addWidget(self.avatar_label, 0, Qt.AlignHCenter)

        left_layout.addSpacing(20)

        chat_button = QPushButton("Чат пользователей")
        chat_button.setEnabled(True)
        chat_button.setFixedHeight(40)
        chat_button.clicked.connect(self.open_chat_window)
        left_layout.addWidget(chat_button)

        events_button = QPushButton("События")
        events_button.setEnabled(True)
        events_button.setFixedHeight(40)
        events_button.clicked.connect(self.open_events_window)
        left_layout.addWidget(events_button)

        left_layout.addStretch()

        if self.is_admin:
            clubs_button = QPushButton("Список клубов")
            clubs_button.setEnabled(True)
            clubs_button.setFixedHeight(40)
            clubs_button.clicked.connect(self.open_clubs_window)
            left_layout.addWidget(clubs_button)

            players_button = QPushButton("Игроки")
            players_button.setEnabled(True)
            players_button.setFixedHeight(40)
            players_button.clicked.connect(self.open_players_window)
            left_layout.addWidget(players_button)

            users_button = QPushButton("Список пользователей")
            users_button.setEnabled(True)
            users_button.setFixedHeight(40)
            users_button.clicked.connect(self.open_users_window)
            left_layout.addWidget(users_button)

        left_layout.addSpacing(10)

        self.right_panel = BackgroundFrame()
        self.right_panel.setObjectName("rightPanel")
        self.right_panel.setStyleSheet("""
            QFrame#rightPanel {
                background-color: #e8f0e8;
            }
        """)

        right_layout = QVBoxLayout(self.right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(20, 20, 20, 10)
        top_bar.addStretch()

        settings_button = QPushButton("⚙️")
        settings_button.setObjectName("settingsButton")
        settings_button.setEnabled(True)
        settings_button.setFixedSize(40, 40)
        font = QFont("Segoe UI", 20)
        font.setBold(True)
        settings_button.setFont(font)
        settings_button.clicked.connect(self.change_background)
        top_bar.addWidget(settings_button)

        right_layout.addLayout(top_bar)

        content_container = QWidget()
        content_container.setStyleSheet("background-color: transparent;")
        content_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(20, 0, 20, 20)
        content_layout.setSpacing(10)

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background-color: transparent;")
        self.stacked_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        content_layout.addWidget(self.stacked_widget)

        right_layout.addWidget(content_container)

        self.events_widget = EventsWindow(self.user_data, self.db, self)
        self.events_widget.setParent(self.stacked_widget)
        self.events_widget.setWindowFlags(Qt.Widget)
        self.events_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.stacked_widget.addWidget(self.events_widget)

        self.stacked_widget.setCurrentWidget(self.events_widget)
        self.current_widget_name = 'events'

        main_layout.addWidget(left_panel)
        main_layout.addWidget(self.right_panel, 1)

        if self.db and self.user_data:
            background_path = self.db.get_user_background_path(self.user_data['id'])
            if background_path and os.path.exists(background_path):
                pixmap = QPixmap(background_path)
                if not pixmap.isNull():
                    self.background_pixmap = pixmap
                    self.background_path = background_path
                    self.right_panel.set_background_image(pixmap)
                    # Устанавливаем фон для виджета событий при старте
                    self.events_widget.set_background_pixmap(pixmap)
                    self.widget_background_set['events'] = True

    def create_circular_avatar(self, pixmap):
        size = min(pixmap.width(), pixmap.height())
        x_offset = (pixmap.width() - size) // 2
        y_offset = (pixmap.height() - size) // 2
        cropped = pixmap.copy(x_offset, y_offset, size, size)
        scaled = cropped.scaled(80, 80, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)

        circular_pixmap = QPixmap(80, 80)
        circular_pixmap.fill(Qt.transparent)

        painter = QPainter(circular_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addEllipse(0, 0, 80, 80)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, scaled)
        painter.end()

        return circular_pixmap

    def _set_widget_background(self, widget, widget_name, background_pixmap=None):
        """Универсальный метод установки фона для виджета"""
        if not widget:
            return
        
        pixmap = background_pixmap or self.background_pixmap
        
        # Если фон уже установлен для этого виджета, не устанавливаем повторно
        if self.widget_background_set.get(widget_name, False):
            return
        
        if pixmap and not pixmap.isNull():
            # Для разных типов виджетов разные методы установки фона
            if hasattr(widget, 'set_background_pixmap'):
                widget.set_background_pixmap(pixmap)
                self.widget_background_set[widget_name] = True
            elif hasattr(widget, 'set_background') and self.background_path:
                widget.set_background(self.background_path)
                self.widget_background_set[widget_name] = True

    def _switch_to_widget(self, widget, widget_name, load_method=None):
        """Универсальный метод переключения между виджетами"""
        if not widget:
            return
        
        # Если это уже текущий виджет, не переключаем
        if self.current_widget_name == widget_name:
            # Просто обновляем данные, если нужно
            if load_method and callable(load_method):
                load_method()
            return
        
        # Устанавливаем фон только если он еще не установлен для этого виджета
        if not self.widget_background_set.get(widget_name, False):
            self._set_widget_background(widget, widget_name)
        
        # Переключаемся на виджет
        self.stacked_widget.setCurrentWidget(widget)
        self.current_widget_name = widget_name
        
        # Вызываем метод загрузки данных, если он есть
        if load_method and callable(load_method):
            load_method()
        
        # Обновляем отображение
        if hasattr(self, 'background_pixmap') and self.background_pixmap:
            widget.update()

    def open_events_window(self):
        """Открытие окна событий"""
        if not hasattr(self, 'events_widget') or not self.events_widget:
            return
        
        self._switch_to_widget(
            self.events_widget, 
            'events', 
            lambda: self.events_widget.load_events()
        )
        self.events_widget.main_window = self

    def on_achievements_updated(self):
        if self.db and self.user_data:
            avatar_path = self.db.get_user_avatar_path(self.user_data['id'])
            if avatar_path and os.path.exists(avatar_path):
                pixmap = QPixmap(avatar_path)
                if not pixmap.isNull():
                    self.avatar_pixmap = self.create_circular_avatar(pixmap)
                    self.update_avatar_display()

    def show_events_view(self):
        """Показ окна событий"""
        self.open_events_window()

    def update_avatar_display(self):
        if self.avatar_pixmap and not self.avatar_pixmap.isNull():
            self.avatar_label.setPixmap(self.avatar_pixmap)
            self.avatar_label.setText("")
        else:
            self.avatar_label.setText("👤")
            self.avatar_label.setPixmap(QPixmap())

    def update_avatar(self, avatar_pixmap):
        self.avatar_pixmap = avatar_pixmap
        self.update_avatar_display()

    def change_background(self):
        """Изменение фона с обновлением во всех виджетах"""
        dialog = BackgroundDialog(self, self.user_data, self.db)
        if dialog.exec() == QDialog.Accepted:
            try:
                pixmap = QPixmap(dialog.selected_file)
                if not pixmap.isNull():
                    self.background_pixmap = pixmap
                    self.background_path = dialog.selected_file
                    self.right_panel.set_background_image(pixmap)
                    
                    # Сбрасываем флаги установки фона для всех виджетов
                    for key in self.widget_background_set:
                        self.widget_background_set[key] = False
                    
                    # Обновляем фон во всех существующих виджетах
                    if hasattr(self, 'events_widget') and self.events_widget:
                        if hasattr(self.events_widget, '_background_set'):
                            self.events_widget._background_set = False
                        self.events_widget.set_background_pixmap(pixmap)
                        self.widget_background_set['events'] = True
                    
                    if hasattr(self, 'chat_widget') and self.chat_widget:
                        self.chat_widget.set_background(dialog.selected_file)
                        self.widget_background_set['chat'] = True
                    
                    if hasattr(self, 'users_widget') and self.users_widget:
                        self.users_widget.set_background_pixmap(pixmap)
                        self.widget_background_set['users'] = True
                    
                    if hasattr(self, 'players_widget') and self.players_widget:
                        self.players_widget.set_background_pixmap(pixmap)
                        self.widget_background_set['players'] = True
                    
                    if hasattr(self, 'clubs_widget') and self.clubs_widget:
                        self.clubs_widget.set_background_pixmap(pixmap)
                        self.widget_background_set['clubs'] = True
                    
                    self.right_panel.setStyleSheet("""
                        QFrame#rightPanel {
                            background-color: transparent;
                        }
                    """)
                    StyledMessageBox.information(self, "Успех", "Фон успешно изменен!")
                else:
                    StyledMessageBox.critical(self, "Ошибка", "Не удалось загрузить изображение")
            except Exception as e:
                StyledMessageBox.critical(self, "Ошибка", f"Не удалось применить фон: {str(e)}")

    def resizeEvent(self, event):
        if hasattr(self, 'background_pixmap') and self.background_pixmap:
            self.right_panel.set_background_image(self.background_pixmap)
        super().resizeEvent(event)

    def avatar_clicked(self, event):
        if self.user_data:
            profile_dialog = ProfileWindow(self.user_data, self.db, self)
            if hasattr(self, 'avatar_pixmap') and self.avatar_pixmap:
                profile_dialog.set_avatar(self.avatar_pixmap)
            if hasattr(self, 'background_pixmap') and self.background_pixmap and not self.background_pixmap.isNull():
                profile_dialog.set_background_pixmap(self.background_pixmap)

            profile_dialog.avatar_updated.connect(self.update_avatar)
            profile_dialog.exec()

    def open_chat_window(self):
        """Открытие окна чата"""
        if not self.chat_widget:
            self.chat_widget = ChatWindow(self.user_data, self.db)
            self.chat_widget.setParent(self.stacked_widget)
            self.chat_widget.setWindowFlags(Qt.Widget)
            if hasattr(self.chat_widget, 'back_button'):
                self.chat_widget.back_button.hide()
            self.chat_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.stacked_widget.addWidget(self.chat_widget)
        
        self._switch_to_widget(self.chat_widget, 'chat')

    def open_users_window(self):
        """Открытие окна пользователей (только админ)"""
        if not self.is_admin:
            return
        
        if not self.users_widget:
            self.users_widget = UsersWindow(self.db, self)
            self.users_widget.setParent(self.stacked_widget)
            self.users_widget.setWindowFlags(Qt.Widget)
            if hasattr(self.users_widget, 'back_button'):
                self.users_widget.back_button.hide()
            self.users_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.stacked_widget.addWidget(self.users_widget)
        
        # Устанавливаем фон перед показом
        if self.background_pixmap and not self.widget_background_set.get('users', False):
            self.users_widget.set_background_pixmap(self.background_pixmap)
            self.widget_background_set['users'] = True
        
        self.stacked_widget.setCurrentWidget(self.users_widget)
        self.current_widget_name = 'users'
        
        # Обновляем список пользователей при каждом открытии
        self.users_widget.load_users()

    def open_players_window(self):
        """Открытие окна игроков (только админ)"""
        if not self.is_admin:
            return
        
        if not self.players_widget:
            self.players_widget = PlayersWindow(
                is_admin=True,
                parent=self,
                user_data=self.user_data,
                db=self.db
            )
            self.players_widget.setParent(self.stacked_widget)
            self.players_widget.setWindowFlags(Qt.Widget)
            if hasattr(self.players_widget, 'back_button'):
                self.players_widget.back_button.hide()
            self.players_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.stacked_widget.addWidget(self.players_widget)
        
        self._switch_to_widget(self.players_widget, 'players')

    def open_clubs_window(self):
        """Открытие окна клубов (только админ)"""
        if not self.is_admin:
            return
        
        if not self.clubs_widget:
            self.clubs_widget = ClubsWindow()
            self.clubs_widget.setParent(self.stacked_widget)
            self.clubs_widget.setWindowFlags(Qt.Widget)
            if hasattr(self.clubs_widget, 'back_button'):
                self.clubs_widget.back_button.hide()
            self.clubs_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.stacked_widget.addWidget(self.clubs_widget)
        
        self._switch_to_widget(self.clubs_widget, 'clubs')

    def open_add_event_window(self):
        """Открытие окна добавления события"""
        if not self.add_event_widget:
            self.add_event_widget = AddEventWindow(self)
            self.add_event_widget.setParent(self.stacked_widget)
            self.add_event_widget.setWindowFlags(Qt.Widget)
            if hasattr(self.add_event_widget, 'back_button'):
                self.add_event_widget.back_button.hide()
            self.add_event_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.add_event_widget.finished.connect(self.on_add_event_finished)
            self.stacked_widget.addWidget(self.add_event_widget)
        
        self._switch_to_widget(self.add_event_widget, 'add_event')
        
        if hasattr(self, 'user_data') and self.user_data:
            self.add_event_widget.set_user_data(self.user_data)
        if hasattr(self, 'db') and self.db:
            self.add_event_widget.set_database(self.db)

    def on_add_event_finished(self, result):
        if result == QDialog.Accepted:
            if hasattr(self, 'events_widget') and self.events_widget:
                self.events_widget.load_events()
        self.show_events_view()


class RegistrationForm(QWidget):
    def __init__(self, login_window, db):
        super().__init__()
        self.login_window = login_window
        self.db = db
        self.fields = {}
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Регистрация")
        self.setFixedSize(450, 500)

        # Установка иконки для окна регистрации
        icon_path = r"Эмблемы\icon.ico"
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            local_icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Эмблемы", "icon.ico")
            if os.path.exists(local_icon_path):
                self.setWindowIcon(QIcon(local_icon_path))

        self.setStyleSheet("""
            QWidget {
                background-color: #e8f0e8;
            }
            QLabel {
                color: #2c4c3b;
                font-weight: bold;
                font-size: 12px;
            }
            QLineEdit {
                background-color: #ffffff;
                border: 2px solid #9bb89b;
                border-radius: 5px;
                padding: 8px;
                color: #1e3a2e;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #4d7a4d;
                background-color: #f8fff8;
            }
            QLineEdit.error {
                border: 2px solid #d46b6b;
                background-color: #fff0f0;
            }
            QPushButton {
                background-color: #6b8f6b;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #527352;
            }
            QPushButton:pressed {
                background-color: #3e5a3e;
            }
            QPushButton#cancelButton {
                background-color: #8f9e8f;
            }
            QPushButton#cancelButton:hover {
                background-color: #748774;
            }
            QPushButton#registerButton {
                background-color: #2196F3;
            }
            QPushButton#registerButton:hover {
                background-color: #1976D2;
            }
        """)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(25)
        main_layout.setContentsMargins(40, 30, 40, 30)

        title_label = QLabel("РЕГИСТРАЦИЯ")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: #1e4a2e;
                font-size: 20px;
                font-weight: bold;
                padding: 10px;
                background-color: rgba(150, 180, 150, 0.3);
                border-radius: 8px;
            }
        """)
        main_layout.addWidget(title_label)

        grid_layout = QGridLayout()
        grid_layout.setVerticalSpacing(15)
        grid_layout.setHorizontalSpacing(15)
        grid_layout.setColumnStretch(1, 1)

        field_names = ['Имя', 'Фамилия', 'Логин', 'Пароль', 'Любимый клуб']

        for i, name in enumerate(field_names):
            label = QLabel(name + ":")
            label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

            line_edit = QLineEdit()
            line_edit.setObjectName(f"field_{name}")

            if name == 'Пароль':
                line_edit.setEchoMode(QLineEdit.Password)

            if name == 'Любимый клуб':
                line_edit.setPlaceholderText("необязательно")

            grid_layout.addWidget(label, i, 0)
            grid_layout.addWidget(line_edit, i, 1)

            self.fields[name] = line_edit

        main_layout.addLayout(grid_layout)
        main_layout.addStretch()

        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.clicked.connect(self.cancel_registration)

        self.register_button = QPushButton("Зарегистрироваться")
        self.register_button.setObjectName("registerButton")
        self.register_button.clicked.connect(self.register_user)

        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.register_button)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def validate_fields(self):
        required_fields = ['Имя', 'Фамилия', 'Логин', 'Пароль']

        for field in self.fields.values():
            field.setProperty('class', '')
            field.style().unpolish(field)
            field.style().polish(field)

        for field_name in required_fields:
            field = self.fields[field_name]
            if not field.text().strip():
                return False, field_name
        return True, None

    def register_user(self):
        is_valid, empty_field = self.validate_fields()

        if not is_valid:
            empty_widget = self.fields[empty_field]
            empty_widget.setProperty('class', 'error')
            empty_widget.style().unpolish(empty_widget)
            empty_widget.style().polish(empty_widget)

            StyledMessageBox.warning(self, "Ошибка регистрации",
                                   f"Поле '{empty_field}' обязательно для заполнения!")
            return

        username = self.fields['Логин'].text().strip()

        if username.lower() == 'admin':
            StyledMessageBox.warning(self, "Ошибка регистрации",
                                   "Логин 'admin' зарезервирован для администратора!")
            return

        if self.db.check_username_exists(username):
            StyledMessageBox.warning(self, "Ошибка регистрации",
                                   "Пользователь с таким логином уже существует!")
            return

        success, user_id, message = self.db.register_user(
            first_name=self.fields['Имя'].text().strip(),
            last_name=self.fields['Фамилия'].text().strip(),
            username=username,
            password=self.fields['Пароль'].text().strip(),
            favorite_club=self.fields['Любимый клуб'].text().strip()
        )

        if success:
            StyledMessageBox.information(self, "Успешная регистрация",
                                       f"Добро пожаловать, {self.fields['Имя'].text().strip()} {self.fields['Фамилия'].text().strip()}!")

            for field in self.fields.values():
                field.clear()
                field.setProperty('class', '')
                field.style().unpolish(field)
                field.style().polish(field)

            self.hide()
            self.login_window.show()
        else:
            StyledMessageBox.critical(self, "Ошибка регистрации", message)

    def cancel_registration(self):
        if StyledMessageBox.question(self, "Подтверждение", "Вы уверены, что хотите отменить регистрацию?"):
            self.hide()
            self.login_window.show()


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.registration_window = None
        self.main_window = None
        try:
            self.db = Database()
        except Exception as e:
            StyledMessageBox.critical(None, "Ошибка", f"Ошибка подключения: {e}")
            sys.exit(1)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Вход в систему")
        self.setFixedSize(400, 350)

        # Установка иконки для окна входа
        icon_path = r"Эмблемы\icon.ico"
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            local_icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Эмблемы", "icon.ico")
            if os.path.exists(local_icon_path):
                self.setWindowIcon(QIcon(local_icon_path))

        self.setStyleSheet("""
            QWidget {
                background-color: #e8f0e8;
            }
            QLabel {
                color: #2c4c3b;
                font-weight: bold;
                font-size: 12px;
            }
            QLineEdit {
                background-color: #ffffff;
                border: 2px solid #9bb89b;
                border-radius: 5px;
                padding: 8px;
                color: #1e3a2e;
                font-size: 12px;
                selection-background-color: #7fa07f;
            }
            QLineEdit:focus {
                border-color: #4d7a4d;
                background-color: #f8fff8;
            }
            QLineEdit.error {
                border: 2px solid #d46b6b;
                background-color: #fff0f0;
            }
            QPushButton {
                background-color: #6b8f6b;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #527352;
            }
            QPushButton:pressed {
                background-color: #3e5a3e;
            }
            QPushButton#registerButton {
                background-color: #2196F3;
            }
            QPushButton#registerButton:hover {
                background-color: #1976D2;
            }
            QPushButton#loginButton {
                background-color: #6b8f6b;
            }
        """)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(25)
        main_layout.setContentsMargins(40, 30, 40, 30)

        title_label = QLabel("BBC")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: #1e4a2e;
                font-size: 20px;
                font-weight: bold;
                padding: 10px;
                background-color: rgba(150, 180, 150, 0.3);
                border-radius: 8px;
            }
        """)
        main_layout.addWidget(title_label)

        grid_layout = QGridLayout()
        grid_layout.setVerticalSpacing(15)
        grid_layout.setHorizontalSpacing(15)
        grid_layout.setColumnStretch(1, 1)

        login_label = QLabel("Логин:")
        login_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.login_input = QLineEdit()
        self.login_input.setObjectName("login_field")
        self.login_input.setPlaceholderText("Введите логин")
        grid_layout.addWidget(login_label, 0, 0)
        grid_layout.addWidget(self.login_input, 0, 1)

        password_label = QLabel("Пароль:")
        password_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.password_input = QLineEdit()
        self.password_input.setObjectName("password_field")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Введите пароль")
        grid_layout.addWidget(password_label, 1, 0)
        grid_layout.addWidget(self.password_input, 1, 1)

        main_layout.addLayout(grid_layout)
        main_layout.addStretch()

        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        self.register_btn = QPushButton("Зарегистрироваться")
        self.register_btn.setObjectName("registerButton")
        self.register_btn.clicked.connect(self.open_registration)

        self.login_btn = QPushButton("Войти")
        self.login_btn.setObjectName("loginButton")
        self.login_btn.clicked.connect(self.login)

        button_layout.addStretch()
        button_layout.addWidget(self.register_btn)
        button_layout.addWidget(self.login_btn)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def open_registration(self):
        if not self.registration_window:
            self.registration_window = RegistrationForm(self, self.db)
        self.hide()
        self.registration_window.show()

    def login(self):
        login = self.login_input.text().strip()
        password = self.password_input.text().strip()

        self.login_input.setProperty('class', '')
        self.login_input.style().unpolish(self.login_input)
        self.login_input.style().polish(self.login_input)

        self.password_input.setProperty('class', '')
        self.password_input.style().unpolish(self.password_input)
        self.password_input.style().polish(self.password_input)

        if login == 'admin':
            success, user_data, message = self.db.login_user(login, password)
        else:
            if not login or not password:
                if not login:
                    self.login_input.setProperty('class', 'error')
                    self.login_input.style().unpolish(self.login_input)
                    self.login_input.style().polish(self.login_input)

                if not password:
                    self.password_input.setProperty('class', 'error')
                    self.password_input.style().unpolish(self.password_input)
                    self.password_input.style().polish(self.password_input)

                StyledMessageBox.warning(self, "Ошибка входа", "Заполните все поля!")
                return

            success, user_data, message = self.db.login_user(login, password)

        if success:
            self.login_input.clear()
            self.password_input.clear()
            self.hide()

            self.main_window = MainWindow(user_data, self.db)
            self.main_window.show()
        else:
            StyledMessageBox.warning(self, "Ошибка входа", message)


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Установка иконки для всего приложения
    icon_path = r"Эмблемы\icon.ico"
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    else:
        local_icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Эмблемы", "icon.ico")
        if os.path.exists(local_icon_path):
            app.setWindowIcon(QIcon(local_icon_path))

    login_window = LoginWindow()
    login_window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()