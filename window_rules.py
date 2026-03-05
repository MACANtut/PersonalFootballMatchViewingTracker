import sys
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QPushButton, QTextEdit, QFrame)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QPalette, QBrush


class RulesWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.background_path = None
        self.initUI()
        self.load_rules_from_file()
        
    def initUI(self):
        self.setWindowTitle("Правила")
        self.setFixedSize(450, 500)
        
        # Основной стиль окна (светлая тема по умолчанию)
        self.setStyleSheet("""
            QWidget {
                background-color: #e8f0e8;
            }
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        self.content_frame = QFrame()
        self.content_frame.setObjectName("contentFrame")
        self.content_frame.setStyleSheet("""
            QFrame#contentFrame {
                background-color: #e8f0e8;
                border-radius: 10px;
            }
        """)
        
        content_layout = QVBoxLayout(self.content_frame)
        content_layout.setSpacing(25)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
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
        content_layout.addWidget(title_label)
        
        self.rules_text = QTextEdit()
        self.rules_text.setReadOnly(True)
        self.rules_text.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.rules_text.setStyleSheet("""
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
        """)
        content_layout.addWidget(self.rules_text)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.exit_button = QPushButton("Выход")
        self.exit_button.setObjectName("exitButton")
        self.exit_button.setStyleSheet("""
            QPushButton#exitButton {
                background-color: #8f9e8f;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
                min-width: 120px;
            }
            QPushButton#exitButton:hover {
                background-color: #748774;
            }
        """)
        self.exit_button.clicked.connect(self.close)
        
        button_layout.addWidget(self.exit_button)
        button_layout.addStretch()
        
        content_layout.addLayout(button_layout)
        
        main_layout.addWidget(self.content_frame)
        
        self.setAutoFillBackground(True)
    
    def set_background(self, image_path):
        """Устанавливает фоновое изображение (изменяет стиль на полупрозрачный)"""
        try:
            self.background_path = image_path
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                # Меняем стиль на полупрозрачный при наличии фона
                self.content_frame.setStyleSheet("""
                    QFrame#contentFrame {
                        background-color: rgba(232, 240, 232, 160);
                        border-radius: 10px;
                    }
                """)
                self.rules_text.setStyleSheet("""
                    QTextEdit {
                        background-color: rgba(255, 255, 255, 220);
                        border: 2px solid rgba(107, 143, 107, 180);
                        border-radius: 5px;
                        padding: 15px;
                        color: #1e3a2e;
                        font-size: 14px;
                        selection-background-color: rgba(127, 160, 127, 180);
                    }
                    QTextEdit:focus {
                        border-color: rgba(77, 122, 77, 200);
                        background-color: rgba(248, 255, 248, 230);
                    }
                """)
                self.exit_button.setStyleSheet("""
                    QPushButton#exitButton {
                        background-color: rgba(143, 158, 143, 220);
                        color: white;
                        border: none;
                        border-radius: 5px;
                        padding: 10px 20px;
                        font-weight: bold;
                        font-size: 12px;
                        min-width: 120px;
                    }
                    QPushButton#exitButton:hover {
                        background-color: rgba(116, 135, 116, 240);
                    }
                """)
                
                # Устанавливаем фон
                palette = self.palette()
                scaled_pixmap = pixmap.scaled(
                    self.size(),
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation
                )
                palette.setBrush(QPalette.Window, QBrush(scaled_pixmap))
                self.setPalette(palette)
        except Exception as e:
            print(f"Ошибка установки фона: {e}")
    
    def resizeEvent(self, event):
        if self.background_path:
            self.set_background(self.background_path)
        super().resizeEvent(event)
    
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