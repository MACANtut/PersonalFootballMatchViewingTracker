import sys
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QPushButton, QTextEdit)
from PySide6.QtCore import Qt

class RulesWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_rules_from_file()
        
    def initUI(self):
        self.setWindowTitle("Правила")
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
            QTextEdit {
                background-color: #ffffff;
                border: 2px solid #9bb89b;
                border-radius: 5px;
                padding: 15px;
                color: #1e3a2e;
                font-size: 14px;
                selection-background-color: #7fa07f;
            }
            QTextEdit:focus {
                border-color: #4d7a4d;
                background-color: #f8fff8;
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
            QPushButton#exitButton {
                background-color: #8f9e8f;
            }
            QPushButton#exitButton:hover {
                background-color: #748774;
            }
        """)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(25)
        main_layout.setContentsMargins(40, 30, 40, 30)
        
        title_label = QLabel("ПРАВИЛА")
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
        
        self.rules_text = QTextEdit()
        self.rules_text.setReadOnly(True)
        self.rules_text.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        main_layout.addWidget(self.rules_text)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.exit_button = QPushButton("Выход")
        self.exit_button.setObjectName("exitButton")
        self.exit_button.clicked.connect(self.close)
        
        button_layout.addWidget(self.exit_button)
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
    def load_rules_from_file(self):
        file_path = "rules.txt"
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                rules_text = file.read()
                self.rules_text.setPlainText(rules_text)
        except FileNotFoundError:
            self.rules_text.setPlainText("Файл rules.txt не найден")
        except Exception as e:
            self.rules_text.setPlainText(f"Ошибка загрузки правил: {str(e)}")

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    rules_window = RulesWindow()
    rules_window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()