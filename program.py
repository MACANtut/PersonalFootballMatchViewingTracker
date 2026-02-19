import sys
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                               QGridLayout, QLabel, QLineEdit, 
                               QPushButton, QMessageBox)
from PySide6.QtCore import Qt

class RegistrationForm(QWidget):
    def __init__(self, login_window):
        super().__init__()
        self.login_window = login_window
        self.initUI()
        
    def initUI(self):
        # Настройка окна
        self.setWindowTitle("Регистрация")
        self.setFixedSize(450, 500)
        
        # Установка зеленовато-бело-серой цветовой гаммы через CSS
        self.setStyleSheet("""
            QWidget {
                background-color: #e8f0e8;  /* Светлый зеленовато-серый фон */
            }
            QLabel {
                color: #2c4c3b;  /* Темно-зеленый текст */
                font-weight: bold;
                font-size: 12px;
            }
            QLineEdit {
                background-color: #ffffff;  /* Белый фон полей */
                border: 2px solid #9bb89b;  /* Зеленовато-серый бордер */
                border-radius: 5px;
                padding: 8px;
                color: #1e3a2e;
                font-size: 12px;
                selection-background-color: #7fa07f;
            }
            QLineEdit:focus {
                border-color: #4d7a4d;  /* Более темный зеленый при фокусе */
                background-color: #f8fff8;
            }
            QLineEdit.error {
                border: 2px solid #d46b6b;  /* Красный для ошибок */
                background-color: #fff0f0;
            }
            QPushButton {
                background-color: #6b8f6b;  /* Зеленый для кнопок */
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #527352;  /* Темнее при наведении */
            }
            QPushButton:pressed {
                background-color: #3e5a3e;
            }
            QPushButton#cancelButton {
                background-color: #8f9e8f;  /* Серо-зеленый для кнопки отмены */
            }
            QPushButton#cancelButton:hover {
                background-color: #748774;
            }
            QPushButton#registerButton {
                background-color: #2196F3;  /* Синий для кнопки регистрации */
            }
            QPushButton#registerButton:hover {
                background-color: #1976D2;
            }
        """)
        
        # Основной вертикальный layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(25)
        main_layout.setContentsMargins(40, 30, 40, 30)
        
        # Заголовок
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
        
        # Сетка для полей ввода
        grid_layout = QGridLayout()
        grid_layout.setVerticalSpacing(15)
        grid_layout.setHorizontalSpacing(15)
        grid_layout.setColumnStretch(1, 1)
        
        # Поля ввода
        self.fields = {}
        field_names = ['Имя', 'Фамилия', 'Логин', 'Пароль', 'Любимый клуб']
        
        for i, name in enumerate(field_names):
            label = QLabel(name + ":")
            label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            line_edit = QLineEdit()
            line_edit.setObjectName(f"field_{name}")
            
            # Для поля пароля устанавливаем режим ввода пароля
            if name == 'Пароль':
                line_edit.setEchoMode(QLineEdit.Password)
            
            # Для поля "Любимый клуб" добавляем подсказку, что необязательно
            if name == 'Любимый клуб':
                line_edit.setPlaceholderText("необязательно")
            
            grid_layout.addWidget(label, i, 0)
            grid_layout.addWidget(line_edit, i, 1)
            
            self.fields[name] = line_edit
        
        main_layout.addLayout(grid_layout)
        
        # Добавляем немного пространства
        main_layout.addStretch()
        
        # Кнопки
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
        """Проверка заполнения обязательных полей (1-4)"""
        required_fields = ['Имя', 'Фамилия', 'Логин', 'Пароль']
        
        # Сначала удаляем класс ошибки у всех полей
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
        """Обработка регистрации"""
        is_valid, empty_field = self.validate_fields()
        
        if not is_valid:
            # Подсветка пустого поля
            empty_widget = self.fields[empty_field]
            empty_widget.setProperty('class', 'error')
            empty_widget.style().unpolish(empty_widget)
            empty_widget.style().polish(empty_widget)
            
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Ошибка регистрации")
            msg_box.setText(f"Поле '{empty_field}' обязательно для заполнения!")
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.button(QMessageBox.Ok).setText("OK")
            msg_box.exec()
            return
        
        # Сбор данных
        user_data = {
            'Имя': self.fields['Имя'].text().strip(),
            'Фамилия': self.fields['Фамилия'].text().strip(),
            'Логин': self.fields['Логин'].text().strip(),
            'Пароль': self.fields['Пароль'].text().strip(),
            'Любимый клуб': self.fields['Любимый клуб'].text().strip()
        }
        
        # Формируем сообщение об успешной регистрации
        club_info = f"Любимый клуб: {user_data['Любимый клуб']}" if user_data['Любимый клуб'] else "Любимый клуб: не указан"
        
        # Успешная регистрация
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Успешная регистрация")
        msg_box.setText(f"Добро пожаловать, {user_data['Имя']} {user_data['Фамилия']}!\n\n"
                       f"Логин: {user_data['Логин']}\n"
                       f"{club_info}")
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.button(QMessageBox.Ok).setText("OK")
        msg_box.exec()
        
        # Очистка полей
        for field in self.fields.values():
            field.clear()
            
        # Сбрасываем класс ошибки
        for field in self.fields.values():
            field.setProperty('class', '')
            field.style().unpolish(field)
            field.style().polish(field)
    
    def cancel_registration(self):
        """Отмена регистрации и возврат в окно входа"""
        # Создаем кастомное окно подтверждения с русскими кнопками
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Подтверждение")
        msg_box.setText("Вы уверены, что хотите отменить регистрацию?")
        msg_box.setIcon(QMessageBox.Question)
        
        # Создаем кнопки с русскими надписями
        yes_button = msg_box.addButton("Да", QMessageBox.YesRole)
        no_button = msg_box.addButton("Нет", QMessageBox.NoRole)
        
        # Устанавливаем кнопку "Нет" как кнопку по умолчанию
        msg_box.setDefaultButton(no_button)
        
        # Показываем окно и получаем результат
        msg_box.exec()
        
        # Проверяем, какая кнопка была нажата
        if msg_box.clickedButton() == yes_button:
            self.hide()
            self.login_window.show()

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.registration_window = None
        self.initUI()
        
    def initUI(self):
        # Настройка окна
        self.setWindowTitle("Вход")
        self.setFixedSize(400, 350)
        
        # Установка зеленовато-бело-серой цветовой гаммы через CSS (в том же стиле)
        self.setStyleSheet("""
            QWidget {
                background-color: #e8f0e8;  /* Светлый зеленовато-серый фон */
            }
            QLabel {
                color: #2c4c3b;  /* Темно-зеленый текст */
                font-weight: bold;
                font-size: 12px;
            }
            QLineEdit {
                background-color: #ffffff;  /* Белый фон полей */
                border: 2px solid #9bb89b;  /* Зеленовато-серый бордер */
                border-radius: 5px;
                padding: 8px;
                color: #1e3a2e;
                font-size: 12px;
                selection-background-color: #7fa07f;
            }
            QLineEdit:focus {
                border-color: #4d7a4d;  /* Более темный зеленый при фокусе */
                background-color: #f8fff8;
            }
            QLineEdit.error {
                border: 2px solid #d46b6b;  /* Красный для ошибок */
                background-color: #fff0f0;
            }
            QPushButton {
                background-color: #6b8f6b;  /* Зеленый для кнопок */
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #527352;  /* Темнее при наведении */
            }
            QPushButton:pressed {
                background-color: #3e5a3e;
            }
            QPushButton#registerButton {
                background-color: #2196F3;  /* Синий для кнопки регистрации */
            }
            QPushButton#registerButton:hover {
                background-color: #1976D2;
            }
            QPushButton#loginButton {
                background-color: #6b8f6b;  /* Зеленый для кнопки входа */
            }
        """)
        
        # Основной вертикальный layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(25)
        main_layout.setContentsMargins(40, 30, 40, 30)
        
        # Заголовок
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
        
        # Сетка для полей ввода
        grid_layout = QGridLayout()
        grid_layout.setVerticalSpacing(15)
        grid_layout.setHorizontalSpacing(15)
        grid_layout.setColumnStretch(1, 1)
        
        # Поле логина
        login_label = QLabel("Логин:")
        login_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.login_input = QLineEdit()
        self.login_input.setObjectName("login_field")
        grid_layout.addWidget(login_label, 0, 0)
        grid_layout.addWidget(self.login_input, 0, 1)
        
        # Поле пароля
        password_label = QLabel("Пароль:")
        password_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.password_input = QLineEdit()
        self.password_input.setObjectName("password_field")
        self.password_input.setEchoMode(QLineEdit.Password)
        grid_layout.addWidget(password_label, 1, 0)
        grid_layout.addWidget(self.password_input, 1, 1)
        
        main_layout.addLayout(grid_layout)
        
        # Добавляем немного пространства
        main_layout.addStretch()
        
        # Кнопки
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
        """Заглушка для входа"""
        login = self.login_input.text()
        password = self.password_input.text()
        
        # Сначала удаляем класс ошибки у полей
        self.login_input.setProperty('class', '')
        self.login_input.style().unpolish(self.login_input)
        self.login_input.style().polish(self.login_input)
        
        self.password_input.setProperty('class', '')
        self.password_input.style().unpolish(self.password_input)
        self.password_input.style().polish(self.password_input)
        
        if not login or not password:
            # Подсвечиваем пустые поля
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
        
        # Создаем кастомное окно с русскими кнопками
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Вход")
        msg_box.setText(f"Попытка входа: логин={login}, пароль={'*' * len(password)}")
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.button(QMessageBox.Ok).setText("OK")
        msg_box.exec()
    
    def open_registration(self):
        """Открытие окна регистрации"""
        if not self.registration_window:
            self.registration_window = RegistrationForm(self)
        self.hide()
        self.registration_window.show()

def main():
    app = QApplication(sys.argv)
    
    # Устанавливаем стиль Fusion для более современного вида
    app.setStyle('Fusion')
    
    login_window = LoginWindow()
    login_window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()