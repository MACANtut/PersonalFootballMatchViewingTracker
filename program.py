import os
import sys

sys.dont_write_bytecode = True

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QLabel, QFrame,
                               QGridLayout, QLineEdit, QMessageBox, QDialog)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QPainter, QPalette, QBrush, QFont
from database import Database
from window_rules import RulesWindow
from window_chat import ChatWindow
from window_profile import ProfileWindow
from windows_users import UsersWindow
from background_settings import BackgroundDialog


class StyledMessageBox:
    """Класс для создания стилизованных сообщений в едином стиле"""
    
    @staticmethod
    def information(parent, title, text):
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #e8f0e8;
            }
            QMessageBox QLabel {
                color: #2c4c3b;
                font-weight: bold;
                font-size: 12px;
                min-width: 250px;
                padding: 15px;
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
        ok_button = msg_box.addButton("ОК", QMessageBox.AcceptRole)
        msg_box.exec()
        return msg_box.clickedButton() == ok_button
    
    @staticmethod
    def warning(parent, title, text):
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #e8f0e8;
            }
            QMessageBox QLabel {
                color: #2c4c3b;
                font-weight: bold;
                font-size: 12px;
                min-width: 250px;
                padding: 15px;
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
        ok_button = msg_box.addButton("ОК", QMessageBox.AcceptRole)
        msg_box.exec()
        return msg_box.clickedButton() == ok_button
    
    @staticmethod
    def critical(parent, title, text):
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #e8f0e8;
            }
            QMessageBox QLabel {
                color: #2c4c3b;
                font-weight: bold;
                font-size: 12px;
                min-width: 250px;
                padding: 15px;
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
        ok_button = msg_box.addButton("ОК", QMessageBox.AcceptRole)
        msg_box.exec()
        return msg_box.clickedButton() == ok_button
    
    @staticmethod
    def question(parent, title, text):
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #e8f0e8;
            }
            QMessageBox QLabel {
                color: #2c4c3b;
                font-weight: bold;
                font-size: 12px;
                min-width: 250px;
                padding: 15px;
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
            QPushButton#noButton {
                background-color: #8f9e8f;
            }
            QPushButton#noButton:hover {
                background-color: #748774;
            }
        """)
        yes_button = msg_box.addButton("Да", QMessageBox.YesRole)
        no_button = msg_box.addButton("Нет", QMessageBox.NoRole)
        no_button.setObjectName("noButton")
        msg_box.setDefaultButton(no_button)
        msg_box.exec()
        return msg_box.clickedButton() == yes_button


class BackgroundFrame(QFrame):
    """Кастомный фрейм с поддержкой масштабируемого фонового изображения"""
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
        self.setFixedSize(900, 600)
        
        self.rules_window = None
        self.chat_window = None
        self.users_window = None
        self.background_pixmap = None
        self.background_path = None
        self.avatar_pixmap = None
        
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
            QLabel#eventCircle {
                background-color: rgba(255, 255, 255, 0.9);
                border: 3px solid #6b8f6b;
                color: #2c4c3b;
                font-size: 36px;
                font-weight: bold;
                border-radius: 50px;
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
            QPushButton#adminButton {
                background-color: #8f9e8f;
            }
            QPushButton#adminButton:hover {
                background-color: #748774;
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
        """)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        left_panel = QFrame()
        left_panel.setObjectName("leftPanel")
        left_panel.setFixedWidth(250)
        
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(20, 30, 20, 30)
        left_layout.setSpacing(10)
        left_layout.setAlignment(Qt.AlignTop)
        
        self.avatar_label = QLabel()
        self.avatar_label.setObjectName("avatar")
        self.avatar_label.setFixedSize(80, 80)
        self.avatar_label.setAlignment(Qt.AlignCenter)
        self.avatar_label.setCursor(Qt.PointingHandCursor)
        self.avatar_label.mousePressEvent = self.avatar_clicked
        self.avatar_label.setText("👤")
        self.avatar_label.setPixmap(QPixmap())
        self.update_avatar_display()
        left_layout.addWidget(self.avatar_label, 0, Qt.AlignHCenter)
        
        left_layout.addSpacing(20)
        
        chat_button = QPushButton("Чат пользователей")
        chat_button.setEnabled(True)
        chat_button.setFixedHeight(40)
        chat_button.clicked.connect(self.open_chat_window)
        left_layout.addWidget(chat_button)
        
        add_event_button = QPushButton("Добавить событие")
        add_event_button.setEnabled(False)
        add_event_button.setFixedHeight(40)
        left_layout.addWidget(add_event_button)
        
        rules_button = QPushButton("Правила")
        rules_button.setEnabled(True)
        rules_button.setFixedHeight(40)
        rules_button.clicked.connect(self.open_rules_window)
        left_layout.addWidget(rules_button)
        
        left_layout.addSpacing(10)
        
        clubs_button = QPushButton("Список клубов")
        clubs_button.setObjectName("adminButton")
        clubs_button.setEnabled(False)
        clubs_button.setFixedHeight(40)
        left_layout.addWidget(clubs_button)
        
        players_button = QPushButton("Игроки")
        players_button.setObjectName("adminButton")
        players_button.setEnabled(False)
        players_button.setFixedHeight(40)
        left_layout.addWidget(players_button)
        
        users_button = QPushButton("Список пользователей")
        users_button.setObjectName("adminButton")
        users_button.setEnabled(True)
        users_button.setFixedHeight(40)
        users_button.clicked.connect(self.open_users_window)
        left_layout.addWidget(users_button)
        
        left_layout.addStretch()
        
        self.right_panel = BackgroundFrame()
        self.right_panel.setObjectName("rightPanel")
        self.right_panel.setStyleSheet("""
            QFrame#rightPanel {
                background-color: #e8f0e8;
            }
        """)
        
        right_layout = QVBoxLayout(self.right_panel)
        right_layout.setContentsMargins(20, 20, 20, 20)
        
        top_bar = QHBoxLayout()
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
        right_layout.addSpacing(20)
        
        events_title = QLabel("Ваши события")
        events_title.setObjectName("eventsTitle")
        events_title.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(events_title)
        
        right_layout.addSpacing(20)
        
        events_container = QWidget()
        events_container.setStyleSheet("background-color: transparent;")
        events_layout = QHBoxLayout(events_container)
        events_layout.setSpacing(40)
        events_layout.setAlignment(Qt.AlignCenter)
        
        for i in ["1", "2"]:
            circle = QLabel(i)
            circle.setObjectName("eventCircle")
            circle.setFixedSize(100, 100)
            circle.setAlignment(Qt.AlignCenter)
            events_layout.addWidget(circle)
        
        right_layout.addWidget(events_container)
        right_layout.addStretch()
        
        main_layout.addWidget(left_panel)
        main_layout.addWidget(self.right_panel, 1)
    
    def update_avatar_display(self):
        """Обновляет отображение аватара в главном окне"""
        if self.avatar_pixmap and not self.avatar_pixmap.isNull():
            self.avatar_label.setPixmap(self.avatar_pixmap)
            self.avatar_label.setText("")
        else:
            self.avatar_label.setText("👤")
            self.avatar_label.setPixmap(QPixmap())
    
    def change_background(self):
        """Открывает диалог выбора фона и применяет его"""
        dialog = BackgroundDialog(self)
        if dialog.exec() == QDialog.Accepted:
            try:
                pixmap = QPixmap(dialog.selected_file)
                if not pixmap.isNull():
                    self.background_pixmap = pixmap
                    self.background_path = dialog.selected_file
                    
                    self.right_panel.set_background_image(pixmap)
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
        """Обновляет фон при изменении размера окна"""
        if hasattr(self, 'background_pixmap') and self.background_pixmap:
            self.right_panel.set_background_image(self.background_pixmap)
        super().resizeEvent(event)
    
    def avatar_clicked(self, event):
        """Открывает окно профиля пользователя"""
        if self.user_data:
            profile_dialog = ProfileWindow(self.user_data, self.db, self)
            if hasattr(self, 'avatar_pixmap') and self.avatar_pixmap:
                profile_dialog.set_avatar(self.avatar_pixmap)
            # Передаем pixmap, а не путь
            if hasattr(self, 'background_pixmap') and self.background_pixmap and not self.background_pixmap.isNull():
                profile_dialog.set_background_pixmap(self.background_pixmap)
            
            profile_dialog.avatar_updated.connect(self.update_avatar)
            profile_dialog.exec()
        else:
            print("Нет данных пользователя")
    
    def update_avatar(self, avatar_pixmap):
        """Обновляет аватар в главном окне"""
        self.avatar_pixmap = avatar_pixmap
        self.update_avatar_display()
    
    def open_rules_window(self):
        if self.rules_window is None or not self.rules_window.isVisible():
            self.rules_window = RulesWindow()
            if self.background_path:
                self.rules_window.set_background(self.background_path)
            self.rules_window.show()
        else:
            self.rules_window.raise_()
            self.rules_window.activateWindow()
    
    def open_chat_window(self):
        """Открывает окно чата"""
        if self.user_data:
            self.chat_window = ChatWindow(self.user_data, self.db)
            if self.background_path:
                self.chat_window.set_background(self.background_path)
            self.chat_window.back_button.clicked.connect(self.close_chat_and_return)
            self.chat_window.show()
            self.hide()
        else:
            print("Нет данных пользователя")
    
    def close_chat_and_return(self):
        """Закрывает чат и возвращается в главное окно"""
        if self.chat_window:
            self.chat_window.close()
            self.chat_window = None
        self.show()
    
    def open_users_window(self):
        """Открывает окно со списком пользователей"""
        if self.users_window is None or not self.users_window.isVisible():
            self.users_window = UsersWindow(self.db, self)
            # Передаем pixmap, а не путь
            if hasattr(self, 'background_pixmap') and self.background_pixmap and not self.background_pixmap.isNull():
                self.users_window.set_background_pixmap(self.background_pixmap)
            self.users_window.show()
        else:
            self.users_window.raise_()
            self.users_window.activateWindow()


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
            self.db = Database(password='12345')
        except Exception as e:
            StyledMessageBox.critical(None, "Ошибка", f"Ошибка подключения: {e}")
            sys.exit(1)
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Вход")
        self.setFixedSize(400, 350)
        
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
        grid_layout.addWidget(login_label, 0, 0)
        grid_layout.addWidget(self.login_input, 0, 1)
        
        password_label = QLabel("Пароль:")
        password_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.password_input = QLineEdit()
        self.password_input.setObjectName("password_field")
        self.password_input.setEchoMode(QLineEdit.Password)
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
    
    def login(self):
        login = self.login_input.text().strip()
        password = self.password_input.text().strip()
        
        self.login_input.setProperty('class', '')
        self.login_input.style().unpolish(self.login_input)
        self.login_input.style().polish(self.login_input)
        
        self.password_input.setProperty('class', '')
        self.password_input.style().unpolish(self.password_input)
        self.password_input.style().polish(self.password_input)
        
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
    
    def open_registration(self):
        if not self.registration_window:
            self.registration_window = RegistrationForm(self, self.db)
        self.hide()
        self.registration_window.show()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    login_window = LoginWindow()
    login_window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()