import sys
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                               QTextEdit, QScrollArea, QFrame, QLabel, QPushButton,
                               QMessageBox)
from PySide6.QtCore import Qt, QTimer, QEvent
from PySide6.QtGui import QKeyEvent
from database import Database

class MessageBubble(QFrame):
    def __init__(self, message_data, is_own_message=False):
        super().__init__()
        self.message_data = message_data
        self.is_own_message = is_own_message
        self.initUI()
    
    def initUI(self):
        self.setFrameStyle(QFrame.NoFrame)
        self.setMaximumWidth(400)
        
        layout = QVBoxLayout()
        layout.setSpacing(2)
        layout.setContentsMargins(5, 5, 5, 5)
        
        header_layout = QHBoxLayout()
        
        sender_name = QLabel(f"{self.message_data['first_name']} {self.message_data['last_name']}")
        sender_name.setStyleSheet("""
            QLabel {
                color: #2c4c3b;
                font-weight: bold;
                font-size: 12px;
            }
        """)
        
        time_label = QLabel(self.message_data['sent_at'].strftime("%H:%M") if hasattr(self.message_data['sent_at'], 'strftime') else str(self.message_data['sent_at']))
        time_label.setStyleSheet("""
            QLabel {
                color: #6b8f6b;
                font-size: 10px;
            }
        """)
        
        header_layout.addWidget(sender_name)
        header_layout.addStretch()
        header_layout.addWidget(time_label)
        
        message_text = QLabel(self.message_data['message'])
        message_text.setWordWrap(True)
        message_text.setStyleSheet(f"""
            QLabel {{
                background-color: {'#d4e8d4' if self.is_own_message else '#ffffff'};
                border: 2px solid #9bb89b;
                border-radius: 10px;
                padding: 10px;
                color: #1e3a2e;
                font-size: 13px;
            }}
        """)
        
        layout.addLayout(header_layout)
        layout.addWidget(message_text)
        
        if self.is_own_message:
            layout.setAlignment(Qt.AlignRight)
        
        self.setLayout(layout)

class ChatWindow(QWidget):
    def __init__(self, user_data=None, db=None):
        super().__init__()
        self.user_data = user_data
        self.db = db if db else Database(password='12345')
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
        
        self.chat_layout = QVBoxLayout(self.chat_frame)
        self.chat_layout.setSpacing(10)
        self.chat_layout.setContentsMargins(15, 15, 15, 15)
        self.chat_layout.addStretch()
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.chat_frame)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameStyle(QFrame.NoFrame)
        main_layout.addWidget(self.scroll_area)
        
        self.message_input = QTextEdit()
        self.message_input.setMaximumHeight(80)
        self.message_input.setPlaceholderText("Введите сообщение")
        self.message_input.installEventFilter(self)
        main_layout.addWidget(self.message_input)
        
        self.setLayout(main_layout)
        
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.load_messages)
        self.update_timer.start(3000)
        
        self.load_messages()
    
    def eventFilter(self, obj, event):
        if obj == self.message_input and event.type() == QEvent.Type.KeyPress:
            key_event = event
            if key_event.key() in (Qt.Key_Return, Qt.Key_Enter) and not (key_event.modifiers() & Qt.ShiftModifier):
                self.send_message()
                return True
        return super().eventFilter(obj, event)
    
    def load_messages(self):
        try:
            messages = self.db.get_chat_messages(50)
            
            while self.chat_layout.count() > 1:
                item = self.chat_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
            for msg in messages:
                is_own = (msg['user_id'] == self.user_data['id'] if self.user_data else False)
                message_bubble = MessageBubble(msg, is_own)
                self.chat_layout.insertWidget(self.chat_layout.count() - 1, message_bubble)
            
            QTimer.singleShot(100, self.scroll_to_bottom)
            
        except Exception as e:
            print(f"Ошибка загрузки сообщений: {e}")
    
    def scroll_to_bottom(self):
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )
    
    def send_message(self):
        message = self.message_input.toPlainText().strip()
        
        if not message:
            return
        
        if not self.user_data:
            QMessageBox.warning(self, "Ошибка", "Не удалось определить пользователя")
            return
        
        success, result = self.db.save_message(self.user_data['id'], message)
        
        if success:
            self.message_input.clear()
            self.load_messages()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось отправить сообщение")
    
    def closeEvent(self, event):
        self.update_timer.stop()
        event.accept()

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    db = Database(password='12345')
    test_user = db.get_user_by_id(1)
    
    chat_window = ChatWindow(test_user, db)
    chat_window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()