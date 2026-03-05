import sys
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                               QTextEdit, QScrollArea, QFrame, QLabel, QPushButton,
                               QMessageBox)
from PySide6.QtCore import Qt, QTimer, QEvent
from PySide6.QtGui import QPixmap, QPalette, QBrush
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
        self.setStyleSheet("background-color: transparent;")
        
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
                background-color: transparent;
            }
        """)
        
        time_label = QLabel(self.message_data['sent_at'].strftime("%H:%M") if hasattr(self.message_data['sent_at'], 'strftime') else str(self.message_data['sent_at']))
        time_label.setStyleSheet("""
            QLabel {
                color: #6b8f6b;
                font-size: 10px;
                background-color: transparent;
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
        self.background_path = None
        self.setWindowTitle("Чат")
        self.setMinimumSize(500, 600)
        
        # Основной стиль окна (светлая тема по умолчанию)
        self.setStyleSheet("""
            QWidget {
                background-color: #e8f0e8;
            }
        """)
        
        self.initUI()
        
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.load_messages)
        self.update_timer.start(3000)
        
        self.load_messages()
    
    def initUI(self):
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
        content_layout.setSpacing(15)
        content_layout.setContentsMargins(15, 15, 15, 15)
        
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)
        
        self.back_button = QPushButton("⇦")
        self.back_button.setObjectName("backButton")
        self.back_button.setFixedSize(50, 50)
        self.back_button.setStyleSheet("""
            QPushButton#backButton {
                background-color: #8f9e8f;
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 40px;
                font-weight: bold;
                padding: 0px;
                qproperty-alignment: AlignCenter;
            }
            QPushButton#backButton:hover {
                background-color: #748774;
            }
        """)
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
        
        content_layout.addLayout(top_layout)
        
        self.chat_frame = QFrame()
        self.chat_frame.setObjectName("chatArea")
        self.chat_frame.setStyleSheet("""
            QFrame#chatArea {
                background-color: #f0f5f0;
                border: 2px solid #9bb89b;
                border-radius: 5px;
            }
        """)
        
        self.chat_layout = QVBoxLayout(self.chat_frame)
        self.chat_layout.setSpacing(10)
        self.chat_layout.setContentsMargins(15, 15, 15, 15)
        self.chat_layout.addStretch()
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.chat_frame)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameStyle(QFrame.NoFrame)
        self.scroll_area.setStyleSheet("""
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
        content_layout.addWidget(self.scroll_area)
        
        self.message_input = QTextEdit()
        self.message_input.setMaximumHeight(80)
        self.message_input.setPlaceholderText("Введите сообщение...")
        self.message_input.setStyleSheet("""
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
        """)
        self.message_input.installEventFilter(self)
        content_layout.addWidget(self.message_input)
        
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
                        background-color: rgba(232, 240, 232, 140);
                        border-radius: 10px;
                    }
                """)
                self.chat_frame.setStyleSheet("""
                    QFrame#chatArea {
                        background-color: rgba(240, 245, 240, 180);
                        border: 2px solid rgba(107, 143, 107, 160);
                        border-radius: 5px;
                    }
                """)
                self.message_input.setStyleSheet("""
                    QTextEdit {
                        background-color: rgba(255, 255, 255, 220);
                        border: 2px solid rgba(107, 143, 107, 160);
                        border-radius: 5px;
                        padding: 8px;
                        color: #1e3a2e;
                        font-size: 12px;
                        selection-background-color: rgba(127, 160, 127, 180);
                    }
                    QTextEdit:focus {
                        border-color: rgba(77, 122, 77, 200);
                        background-color: rgba(248, 255, 248, 230);
                    }
                """)
                self.back_button.setStyleSheet("""
                    QPushButton#backButton {
                        background-color: rgba(143, 158, 143, 220);
                        color: white;
                        border: none;
                        border-radius: 25px;
                        font-size: 40px;
                        font-weight: bold;
                        padding: 0px;
                        qproperty-alignment: AlignCenter;
                    }
                    QPushButton#backButton:hover {
                        background-color: rgba(116, 135, 116, 240);
                    }
                """)
                self.scroll_area.setStyleSheet("""
                    QScrollArea {
                        border: none;
                        background-color: transparent;
                    }
                    QScrollBar:vertical {
                        border: none;
                        background-color: rgba(208, 224, 208, 140);
                        width: 10px;
                        border-radius: 5px;
                    }
                    QScrollBar::handle:vertical {
                        background-color: rgba(107, 143, 107, 180);
                        border-radius: 5px;
                        min-height: 20px;
                    }
                    QScrollBar::handle:vertical:hover {
                        background-color: rgba(82, 115, 82, 220);
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