import sys
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                               QTextEdit, QScrollArea, QFrame, QLabel, QPushButton)
from PySide6.QtCore import Qt

class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Чат")
        self.setMinimumSize(500, 600)
        self.setStyleSheet("""
            QWidget {
                background-color: #e8f0e8;
            }
            QPushButton {
                background-color: #6b8f6b;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #527352;
            }
            QPushButton:pressed {
                background-color: #3e5a3e;
            }
            QPushButton#backButton {
                background-color: #8f9e8f;
                min-width: 50px;
                max-width: 50px;
                min-height: 50px;
                max-height: 50px;
                padding: 5px;
                border-radius: 25px;
                font-size: 40px;
                font-weight: bold;
            }
            QPushButton#backButton:hover {
                background-color: #748774;
            }
            QTextEdit {
                background-color: #ffffff;
                border: 2px solid #9bb89b;
                border-radius: 5px;
                padding: 8px;
                color: #1e3a2e;
                font-size: 12px;
                selection-background-color: #7fa07f;
            }
            QTextEdit:focus {
                border-color: #4d7a4d;
                background-color: #f8fff8;
            }
            QFrame#chatArea {
                background-color: #f0f5f0;
                border: 2px solid #9bb89b;
                border-radius: 5px;
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
            QLabel {
                color: #2c4c3b;
                font-weight: bold;
                font-size: 18px;
            }
        """)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)
        
        self.back_button = QPushButton("⇦")
        self.back_button.setObjectName("backButton")
        top_layout.addWidget(self.back_button)
        
        title_label = QLabel("Чат")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: #1e4a2e;
                font-size: 20px;
                font-weight: bold;
                padding: 8px 20px;
                background-color: rgba(150, 180, 150, 0.3);
                border-radius: 8px;
            }
        """)
        top_layout.addWidget(title_label)
        
        right_spacer = QWidget()
        right_spacer.setFixedSize(50, 50)
        right_spacer.setStyleSheet("background-color: transparent;")
        top_layout.addWidget(right_spacer)
        
        main_layout.addLayout(top_layout)
        
        self.chat_frame = QFrame()
        self.chat_frame.setObjectName("chatArea")
        self.chat_frame.setFrameStyle(QFrame.NoFrame)
        
        chat_layout = QVBoxLayout(self.chat_frame)
        chat_layout.setSpacing(10)
        chat_layout.setContentsMargins(15, 15, 15, 15)
        chat_layout.addStretch()
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.chat_frame)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameStyle(QFrame.NoFrame)
        main_layout.addWidget(self.scroll_area)
        
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(10)
        
        self.message_input = QTextEdit()
        self.message_input.setMaximumHeight(80)
        self.message_input.installEventFilter(self)
        bottom_layout.addWidget(self.message_input)
        main_layout.addLayout(bottom_layout)
        
        self.setLayout(main_layout)
    
    def eventFilter(self, obj, event):
        if obj == self.message_input and event.type() == event.Type.KeyPress and event.key() in (Qt.Key_Return, Qt.Key_Enter) and not (event.modifiers() & Qt.ShiftModifier):
            self.send_message()
            return True
        return super().eventFilter(obj, event)
    
    def send_message(self):
        message = self.message_input.toPlainText().strip()
        if message:
            print(f"Отправлено сообщение: {message}")
            self.message_input.clear()

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    chat_window = ChatWindow()
    chat_window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 