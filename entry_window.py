

import sys
from PySide6.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, 
                               QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout)
from PySide6.QtCore import Qt

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Вход")
        self.setFixedSize(350, 300)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
            }
            QLineEdit {
                background-color: white;
                border: 1px solid #c0c0c0;
                border-radius: 3px;
                padding: 5px;
                font-size: 14px;
                min-height: 20px;
                color: black;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLabel {
                color: #333333;
                font-size: 14px;
            }
        """)
     
        title_label = QLabel("Вход")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-top: 30px; margin-bottom: 20px;")
       
        login_label = QLabel("Логин:")
        login_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.login_input = QLineEdit()
        self.login_input.setFixedWidth(200)
        
        password_label = QLabel("Пароль:")
        password_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedWidth(200)
       
        register_btn = QPushButton("Зарегистрироваться")
        register_btn.setStyleSheet("background-color: #2196F3; padding: 8px 16px;")
        register_btn.clicked.connect(self.register)
        
        login_btn = QPushButton("Войти")
        login_btn.clicked.connect(self.login)
       
        form_widget = QWidget()
        form_layout = QGridLayout(form_widget)
        form_layout.addWidget(login_label, 0, 0)
        form_layout.addWidget(self.login_input, 0, 1)
        form_layout.addWidget(password_label, 1, 0)
        form_layout.addWidget(self.password_input, 1, 1)
        form_layout.setHorizontalSpacing(15)
        form_layout.setVerticalSpacing(15)
        form_layout.setContentsMargins(0, 0, 0, 0)
     
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.addWidget(register_btn)
        buttons_layout.addWidget(login_btn)
        buttons_layout.setSpacing(15)
        buttons_layout.setAlignment(Qt.AlignCenter)
        buttons_layout.setContentsMargins(0, 20, 0, 0)
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(title_label)
        main_layout.addStretch(1)
        main_layout.addWidget(form_widget, 0, Qt.AlignCenter)
        main_layout.addStretch(1)
        main_layout.addWidget(buttons_widget, 0, Qt.AlignCenter)
        main_layout.addStretch(2)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(40, 10, 40, 30)
        
        self.setLayout(main_layout)
    
    def login(self):
        print(f"Попытка входа: логин={self.login_input.text()}, пароль={self.password_input.text()}")
    
    def register(self):
        print("Открыть окно регистрации")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())