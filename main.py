import os
import sys

sys.dont_write_bytecode = True

postgres_path = r"C:\Program Files\PostgreSQL\17\bin"
if os.path.exists(postgres_path):
    os.environ["PATH"] = postgres_path + os.pathsep + os.environ["PATH"]

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QLabel, QFrame,
                               QGridLayout, QLineEdit, QMessageBox)
from PySide6.QtCore import Qt
from database import Database

class MainWindow(QMainWindow):
    def __init__(self, user_data=None):
        super().__init__()
        self.user_data = user_data
        self.setWindowTitle("Персональный трекер футбольных матчей")
        self.setFixedSize(900, 600)
        
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
            QFrame#rightPanel {
                background-color: #e8f0e8;
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
        
        avatar = QLabel("👤")
        avatar.setObjectName("avatar")
        avatar.setFixedSize(80, 80)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setCursor(Qt.PointingHandCursor)
        avatar.mousePressEvent = self.avatar_clicked
        left_layout.addWidget(avatar, 0, Qt.AlignHCenter)
        
        left_layout.addSpacing(20)
        
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
        
        rules_button = QPushButton("Правила")
        rules_button.setEnabled(False)
        rules_button.setFixedHeight(40)
        rules_button.setStyleSheet("padding-left: 15px;")
        left_layout.addWidget(rules_button)
        
        left_layout.addSpacing(10)
        
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
        
        right_panel = QFrame()
        right_panel.setObjectName("rightPanel")
        
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(20, 20, 20, 20)
        
        top_bar = QHBoxLayout()
        top_bar.addStretch()
        
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
        
        events_title = QLabel("Ваши события")
        events_title.setObjectName("eventsTitle")
        events_title.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(events_title)
        
        right_layout.addSpacing(20)
        
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
        
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel, 1)
    
    def avatar_clicked(self, event):
        print("Переход в профиль (заглушка)")

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
            
            QMessageBox.warning(self, "Ошибка регистрации", 
                              f"Поле '{empty_field}' обязательно для заполнения!")
            return
        
        username = self.fields['Логин'].text().strip()
        if self.db.check_username_exists(username):
            QMessageBox.warning(self, "Ошибка регистрации", 
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
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Успешная регистрация")
            msg_box.setText(f"Добро пожаловать, {self.fields['Имя'].text().strip()} {self.fields['Фамилия'].text().strip()}!")
            msg_box.setIcon(QMessageBox.Information)
            ok_button = msg_box.addButton("ОК", QMessageBox.AcceptRole)
            msg_box.exec()
            
            if msg_box.clickedButton() == ok_button:
                for field in self.fields.values():
                    field.clear()
                    field.setProperty('class', '')
                    field.style().unpolish(field)
                    field.style().polish(field)
                
                self.hide()
                self.login_window.show()
        else:
            QMessageBox.critical(self, "Ошибка регистрации", message)
    
    def cancel_registration(self):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Подтверждение")
        msg_box.setText("Вы уверены, что хотите отменить регистрацию?")
        msg_box.setIcon(QMessageBox.Question)
        
        yes_button = msg_box.addButton("Да", QMessageBox.YesRole)
        no_button = msg_box.addButton("Нет", QMessageBox.NoRole)
        msg_box.setDefaultButton(no_button)
        msg_box.exec()
        
        if msg_box.clickedButton() == yes_button:
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
            QMessageBox.critical(None, "Ошибка", f"Ошибка подключения: {e}")
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
            
            QMessageBox.warning(self, "Ошибка входа", "Заполните все поля!")
            return
        
        success, user_data, message = self.db.login_user(login, password)
        
        if success:
            self.login_input.clear()
            self.password_input.clear()
            self.hide()
            
            self.main_window = MainWindow(user_data)
            self.main_window.show()
        else:
            QMessageBox.warning(self, "Ошибка входа", message)
    
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