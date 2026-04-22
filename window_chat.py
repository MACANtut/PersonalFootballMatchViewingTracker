# window_chat.py
import sys
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                               QTextEdit, QScrollArea, QFrame, QLabel, QPushButton,
                               QMessageBox, QSizePolicy)
from PySide6.QtCore import Qt, QTimer, QEvent
from PySide6.QtGui import QPixmap, QPalette, QBrush, QFont
from database import Database
import os


class MessageBubble(QWidget):
    def __init__(self, message_data, is_own_message=False):
        super().__init__()
        self.message_data = message_data
        self.is_own_message = is_own_message
        self.initUI()

    def initUI(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 2, 0, 2)
        main_layout.setSpacing(0)

        message_container = QFrame()
        message_container.setObjectName("messageContainer")

        container_layout = QVBoxLayout(message_container)
        container_layout.setSpacing(4)
        container_layout.setContentsMargins(12, 8, 12, 8)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        sender_name = QLabel(f"{self.message_data['first_name']} {self.message_data['last_name']}")
        sender_name.setStyleSheet("""
            QLabel {
                color: #2c4c3b;
                font-weight: bold;
                font-size: 11px;
                background-color: transparent;
                padding: 0px;
            }
        """)

        time_str = self.message_data['sent_at'].strftime("%H:%M") if hasattr(self.message_data['sent_at'], 'strftime') else str(self.message_data['sent_at'])
        time_label = QLabel(time_str)
        time_label.setStyleSheet("""
            QLabel {
                color: #8f9e8f;
                font-size: 10px;
                background-color: transparent;
                padding: 0px;
            }
        """)

        header_layout.addWidget(sender_name)
        header_layout.addStretch()
        header_layout.addWidget(time_label)

        message_text = QLabel(self.message_data['message'])
        message_text.setWordWrap(True)
        message_text.setStyleSheet("""
            QLabel {
                background-color: transparent;
                padding: 4px 0px;
                color: #1e3a2e;
                font-size: 12px;
            }
        """)

        container_layout.addLayout(header_layout)
        container_layout.addWidget(message_text)

        if self.is_own_message:
            message_container.setStyleSheet("""
                QFrame#messageContainer {
                    background-color: #d4e8d4;
                    border: 1px solid #9bb89b;
                    border-radius: 12px;
                    max-width: 400px;
                }
            """)
            main_layout.addStretch()
            main_layout.addWidget(message_container)
        else:
            message_container.setStyleSheet("""
                QFrame#messageContainer {
                    background-color: #ffffff;
                    border: 1px solid #9bb89b;
                    border-radius: 12px;
                    max-width: 400px;
                }
            """)
            main_layout.addWidget(message_container)
            main_layout.addStretch()

        message_container.setMaximumWidth(450)
        self.setFixedHeight(message_container.sizeHint().height())


class ChatWindow(QWidget):
    def __init__(self, user_data=None, db=None):
        super().__init__()
        self.user_data = user_data
        self.db = db if db else Database()
        self.background_path = None
        self.setWindowTitle("Чат")
        self.setMinimumSize(500, 600)

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

    def _setup_message_box(self, msg_box, text):
        lines = text.split('\n')
        max_line_length = max(len(line) for line in lines) if lines else len(text)
        width = min(max_line_length * 8 + 80, 500)
        height = len(lines) * 25 + 80

        msg_box.setMinimumWidth(width)
        msg_box.setMaximumWidth(min(width + 50, 600))
        msg_box.setMinimumHeight(height)
        msg_box.setMaximumHeight(min(height + 50, 500))

        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #e8f0e8;
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
        """)
        msg_box.addButton("ОК", QMessageBox.AcceptRole)

    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        self.content_frame = QFrame()
        self.content_frame.setObjectName("contentFrame")
        self.content_frame.setStyleSheet("""
            QFrame#contentFrame {
                background-color: #e8f0e8;
                border-radius: 10px;
            }
        """)
        self.content_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        content_layout = QVBoxLayout(self.content_frame)
        content_layout.setSpacing(15)
        content_layout.setContentsMargins(15, 15, 15, 15)

        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(10)

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
        top_layout.addWidget(title_label, 1)

        self.rules_button = QPushButton("!")
        self.rules_button.setObjectName("rulesButton")
        self.rules_button.setFixedSize(40, 40)
        self.rules_button.setCursor(Qt.PointingHandCursor)
        self.rules_button.setToolTip("Правила чата")
        self.rules_button.setStyleSheet("""
            QPushButton#rulesButton {
                background-color: #6b8f6b;
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton#rulesButton:hover {
                background-color: #527352;
            }
            QPushButton#rulesButton:pressed {
                background-color: #3e5a3e;
            }
        """)
        self.rules_button.clicked.connect(self.show_rules_tooltip)

        top_layout.addWidget(self.rules_button)
        content_layout.addLayout(top_layout)

        self.messages_widget = QWidget()
        self.messages_widget.setObjectName("messagesWidget")
        self.messages_widget.setStyleSheet("""
            QWidget#messagesWidget {
                background-color: #f0f5f0;
                border: 2px solid #9bb89b;
                border-radius: 8px;
            }
        """)

        self.messages_layout = QVBoxLayout(self.messages_widget)
        self.messages_layout.setSpacing(8)
        self.messages_layout.setContentsMargins(10, 10, 10, 10)
        self.messages_layout.addStretch()

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.messages_widget)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameStyle(QFrame.NoFrame)
        self.scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
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

    def load_rules_from_file(self):
        rules_file_path = "rules.txt"
        try:
            with open(rules_file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            return "Файл rules.txt не найден.\nПожалуйста, обратитесь к администратору."
        except Exception:
            return "Ошибка загрузки правил"

    def show_rules_tooltip(self):
        rules_text = self.load_rules_from_file()

        rules_dialog = QWidget(self)
        rules_dialog.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        rules_dialog.setAttribute(Qt.WA_DeleteOnClose)

        layout = QVBoxLayout(rules_dialog)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        title_label = QLabel("📜 ПРАВИЛА ЧАТА")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: #1e4a2e;
                font-size: 16px;
                font-weight: bold;
                padding: 8px;
                background-color: rgba(150, 180, 150, 0.3);
                border-radius: 8px;
            }
        """)
        layout.addWidget(title_label)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumSize(500, 400)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 2px solid #9bb89b;
                border-radius: 8px;
                background-color: #ffffff;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #d0e0d0;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #6b8f6b;
                border-radius: 4px;
                min-height: 20px;
            }
        """)

        rules_text_widget = QLabel(rules_text)
        rules_text_widget.setWordWrap(True)
        rules_text_widget.setAlignment(Qt.AlignLeft)
        rules_text_widget.setTextFormat(Qt.PlainText)
        rules_text_widget.setStyleSheet("""
            QLabel {
                color: #2c4c3b;
                font-size: 11px;
                padding: 10px;
                background-color: #ffffff;
                font-family: monospace;
            }
        """)

        scroll_area.setWidget(rules_text_widget)
        scroll_area.setMinimumWidth(450)
        scroll_area.setMinimumHeight(350)
        layout.addWidget(scroll_area)

        close_button = QPushButton("Понятно, спасибо!")
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #6b8f6b;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 20px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #527352;
            }
        """)
        close_button.clicked.connect(rules_dialog.close)
        layout.addWidget(close_button)

        button_pos = self.rules_button.mapToGlobal(self.rules_button.rect().bottomRight())
        rules_dialog.move(button_pos.x() - rules_dialog.sizeHint().width(), button_pos.y())

        rules_dialog.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                border: 2px solid #6b8f6b;
                border-radius: 10px;
            }
        """)

        rules_dialog.show()

    def set_background(self, image_path):
        try:
            self.background_path = image_path
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                self.content_frame.setStyleSheet("""
                    QFrame#contentFrame {
                        background-color: rgba(232, 240, 232, 140);
                        border-radius: 10px;
                    }
                """)
                self.messages_widget.setStyleSheet("""
                    QWidget#messagesWidget {
                        background-color: rgba(240, 245, 240, 180);
                        border: 2px solid rgba(107, 143, 107, 160);
                        border-radius: 8px;
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
                self.rules_button.setStyleSheet("""
                    QPushButton#rulesButton {
                        background-color: rgba(107, 143, 107, 200);
                        color: white;
                        border: none;
                        border-radius: 20px;
                        font-size: 20px;
                        font-weight: bold;
                    }
                    QPushButton#rulesButton:hover {
                        background-color: rgba(82, 115, 82, 230);
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

                palette = self.palette()
                scaled_pixmap = pixmap.scaled(
                    self.size(),
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation
                )
                palette.setBrush(QPalette.Window, QBrush(scaled_pixmap))
                self.setPalette(palette)
        except Exception:
            pass

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

            while self.messages_layout.count() > 1:
                item = self.messages_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            for msg in messages:
                is_own = (msg['user_id'] == self.user_data['id'] if self.user_data else False)
                message_bubble = MessageBubble(msg, is_own)
                self.messages_layout.insertWidget(self.messages_layout.count() - 1, message_bubble)

            QTimer.singleShot(100, self.scroll_to_bottom)

        except Exception:
            pass

    def scroll_to_bottom(self):
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )

    def send_message(self):
        message = self.message_input.toPlainText().strip()

        if not message:
            return

        if not self.user_data:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Ошибка")
            msg_box.setText("Не удалось определить пользователя")
            msg_box.setIcon(QMessageBox.Warning)
            self._setup_message_box(msg_box, "Не удалось определить пользователя")
            msg_box.exec()
            return

        success, result = self.db.save_message(self.user_data['id'], message)

        if success:
            self.message_input.clear()
            self.load_messages()
        else:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Ошибка")
            msg_box.setText("Не удалось отправить сообщение")
            msg_box.setIcon(QMessageBox.Warning)
            self._setup_message_box(msg_box, "Не удалось отправить сообщение")
            msg_box.exec()

    def closeEvent(self, event):
        self.update_timer.stop()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    db = Database()
    test_user = db.get_user_by_id(1)

    chat_window = ChatWindow(test_user, db)
    chat_window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()