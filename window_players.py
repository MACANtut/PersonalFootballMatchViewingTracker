# window_players.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                               QLabel, QPushButton, QFrame, QTableWidget,
                               QTableWidgetItem, QHeaderView, QLineEdit,
                               QWidget, QFileDialog, QMessageBox, QComboBox,
                               QSizePolicy)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QFont, QPainter
import requests
from io import BytesIO
from datetime import datetime
from functools import partial
from database import Database


class ImageLoader:
    @staticmethod
    def load_image_from_url(url):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                image_data = BytesIO(response.content)
                pixmap = QPixmap()
                pixmap.loadFromData(image_data.getvalue())
                if not pixmap.isNull():
                    return pixmap
            return None
        except Exception:
            return None


class PhotoViewerDialog(QDialog):
    def __init__(self, photo_url, player_name, parent=None):
        super().__init__(parent)
        self.photo_url = photo_url
        self.player_name = player_name
        self.setWindowTitle(f"Фото: {player_name}")
        self.setModal(True)
        self.initUI()
        self.load_photo()

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
        self.setStyleSheet("""
            QDialog {
                background-color: #e8f0e8;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        photo_frame = QFrame()
        photo_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 2px solid #9bb89b;
                border-radius: 8px;
                padding: 5px;
            }
        """)

        photo_layout = QVBoxLayout(photo_frame)
        photo_layout.setContentsMargins(5, 5, 5, 5)

        self.photo_label = QLabel()
        self.photo_label.setAlignment(Qt.AlignCenter)
        self.photo_label.setMinimumSize(300, 300)
        self.photo_label.setText("Загрузка изображения...")
        photo_layout.addWidget(self.photo_label)

        layout.addWidget(photo_frame)

        close_button = QPushButton("Закрыть")
        close_button.setFixedWidth(160)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #6b8f6b;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
                margin: 0 auto;
            }
            QPushButton:hover {
                background-color: #527352;
            }
        """)
        close_button.clicked.connect(self.accept)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        button_layout.addStretch()

        layout.addLayout(button_layout)
        self.setFixedSize(350, 400)

    def load_photo(self):
        pixmap = ImageLoader.load_image_from_url(self.photo_url)

        if pixmap and not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(
                300, 300,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.photo_label.setPixmap(scaled_pixmap)
            self.photo_label.setText("")
        else:
            self.photo_label.setText("Не удалось загрузить изображение")
            self.photo_label.setStyleSheet("color: #d46b6b; font-size: 14px; padding: 30px;")


class DateLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("ДД.ММ.ГГГГ")
        self.setMaxLength(10)
        self.setInputMask("00.00.0000")

        self.setStyleSheet("""
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
        """)

    def get_valid_date(self):
        date_str = self.text().strip()
        if not date_str or '_' in date_str:
            return None

        try:
            day, month, year = date_str.split('.')
            if len(day) != 2 or len(month) != 2 or len(year) != 4:
                return None

            date_obj = datetime(int(year), int(month), int(day))
            return date_obj.strftime("%Y-%m-%d")
        except ValueError:
            return None
        except Exception:
            return None


class PhotoButton(QLabel):
    clicked = Signal(str, str)

    def __init__(self, photo_url, player_name, parent=None):
        super().__init__(parent)
        self.photo_url = photo_url
        self.player_name = player_name
        self.setup_ui()

    def setup_ui(self):
        self.setText("📷 Фото")
        self.setAlignment(Qt.AlignCenter)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QLabel {
                color: #2196F3;
                font-size: 11px;
                font-weight: bold;
                text-decoration: underline;
                padding: 5px;
                background-color: rgba(33, 150, 243, 0.1);
                border-radius: 3px;
            }
            QLabel:hover {
                color: #1976D2;
                background-color: rgba(33, 150, 243, 0.2);
            }
        """)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.photo_url, self.player_name)


class AddPlayerDialog(QDialog):
    def __init__(self, db, background_pixmap=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.photo_url = None
        self.background_pixmap = background_pixmap
        self.setWindowTitle("Добавление игрока")
        self.setMinimumSize(600, 620)
        self.resize(650, 650)
        self.setModal(True)
        self.initUI()

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
        self.setStyleSheet("""
            QDialog {
                background-color: #e8f0e8;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)

        self.content_frame = QFrame()
        self.content_frame.setObjectName("contentFrame")
        self.content_frame.setStyleSheet("""
            QFrame#contentFrame {
                background-color: #f0f5f0;
                border: 2px solid #9bb89b;
                border-radius: 10px;
            }
        """)
        self.content_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        content_layout = QVBoxLayout(self.content_frame)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(30, 30, 30, 30)

        title_label = QLabel("Добавление игрока")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: #1e4a2e;
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
                background-color: rgba(150, 180, 150, 0.3);
                border-radius: 8px;
            }
        """)
        content_layout.addWidget(title_label)

        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)

        name_layout = QHBoxLayout()
        name_label = QLabel("Имя:")
        name_label.setFixedWidth(120)
        name_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        name_label.setStyleSheet("color: #2c4c3b; font-weight: bold; font-size: 12px;")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Введите имя игрока")
        self.name_input.setStyleSheet("""
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
        """)
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        form_layout.addLayout(name_layout)

        surname_layout = QHBoxLayout()
        surname_label = QLabel("Фамилия:")
        surname_label.setFixedWidth(120)
        surname_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        surname_label.setStyleSheet("color: #2c4c3b; font-weight: bold; font-size: 12px;")
        self.surname_input = QLineEdit()
        self.surname_input.setPlaceholderText("Введите фамилию игрока")
        self.surname_input.setStyleSheet("""
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
        """)
        surname_layout.addWidget(surname_label)
        surname_layout.addWidget(self.surname_input)
        form_layout.addLayout(surname_layout)

        birth_layout = QHBoxLayout()
        birth_label = QLabel("Дата рождения:")
        birth_label.setFixedWidth(120)
        birth_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        birth_label.setStyleSheet("color: #2c4c3b; font-weight: bold; font-size: 12px;")
        self.birth_input = DateLineEdit()
        birth_layout.addWidget(birth_label)
        birth_layout.addWidget(self.birth_input)
        form_layout.addLayout(birth_layout)

        club_layout = QHBoxLayout()
        club_label = QLabel("Клуб:")
        club_label.setFixedWidth(120)
        club_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        club_label.setStyleSheet("color: #2c4c3b; font-weight: bold; font-size: 12px;")

        self.club_combo = QComboBox()
        self.club_combo.setStyleSheet("""
            QComboBox {
                background-color: #ffffff;
                border: 2px solid #9bb89b;
                border-radius: 5px;
                padding: 8px;
                color: #1e3a2e;
                font-size: 12px;
                min-width: 280px;
            }
            QComboBox:hover {
                border-color: #6b8f6b;
            }
            QComboBox:focus {
                border-color: #4d7a4d;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
                border-left: 2px solid #9bb89b;
                border-top-right-radius: 5px;
                border-bottom-right-radius: 5px;
                background-color: #e8f0e8;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #527352;
                margin-right: 8px;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                border: 2px solid #9bb89b;
                border-radius: 5px;
                color: #1e3a2e;
                selection-background-color: #d4e8d4;
                selection-color: #1e3a2e;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                padding: 8px;
                background-color: #ffffff;
                color: #1e3a2e;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #e8f0e8;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #d4e8d4;
                color: #1e3a2e;
            }
        """)

        clubs = self.db.get_all_clubs_for_select()
        self.club_combo.addItem("-- Выберите клуб --", None)
        for club in clubs:
            display_text = f"{club['name']}"
            self.club_combo.addItem(display_text, club['id'])

        club_layout.addWidget(club_label)
        club_layout.addWidget(self.club_combo)
        form_layout.addLayout(club_layout)

        photo_layout = QHBoxLayout()
        photo_label = QLabel("URL фотографии:")
        photo_label.setFixedWidth(120)
        photo_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        photo_label.setStyleSheet("color: #2c4c3b; font-weight: bold; font-size: 12px;")

        self.photo_url_edit = QLineEdit()
        self.photo_url_edit.setPlaceholderText("https://example.com/photo.jpg")
        self.photo_url_edit.setStyleSheet("""
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
        """)

        photo_layout.addWidget(photo_label)
        photo_layout.addWidget(self.photo_url_edit)
        form_layout.addLayout(photo_layout)

        content_layout.addLayout(form_layout)
        content_layout.addStretch()

        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        cancel_button = QPushButton("Отменить добавление")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #8f9e8f;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
                min-width: 140px;
            }
            QPushButton:hover {
                background-color: #748774;
            }
        """)
        cancel_button.clicked.connect(self.reject)

        add_button = QPushButton("Добавить")
        add_button.setStyleSheet("""
            QPushButton {
                background-color: #6b8f6b;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #527352;
            }
        """)
        add_button.clicked.connect(self.accept)

        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(add_button)
        button_layout.addStretch()

        content_layout.addLayout(button_layout)

        main_layout.addWidget(self.content_frame)

        self.setAutoFillBackground(True)

        if self.background_pixmap:
            self.apply_background()

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

    def apply_background(self):
        if self.background_pixmap and not self.background_pixmap.isNull():
            self.content_frame.setStyleSheet("""
                QFrame#contentFrame {
                    background-color: rgba(240, 245, 240, 200);
                    border: 2px solid rgba(155, 184, 155, 160);
                    border-radius: 10px;
                }
            """)

    def resizeEvent(self, event):
        if self.background_pixmap and not self.background_pixmap.isNull():
            self.update()
        super().resizeEvent(event)

    def get_player_data(self):
        club_id = self.club_combo.currentData()
        return {
            'first_name': self.name_input.text().strip(),
            'last_name': self.surname_input.text().strip(),
            'birth_date': self.birth_input.text().strip(),
            'club_id': club_id if club_id else None,
            'photo_url': self.photo_url_edit.text().strip()
        }

    def validate_fields(self):
        if not self.name_input.text().strip():
            return False, "Имя", "Поле 'Имя' обязательно для заполнения!"

        if not self.surname_input.text().strip():
            return False, "Фамилия", "Поле 'Фамилия' обязательно для заполнения!"

        birth_date = self.birth_input.text().strip()
        if not birth_date or '_' in birth_date:
            return False, "Дата рождения", "Поле 'Дата рождения' обязательно для заполнения!"

        try:
            day, month, year = birth_date.split('.')
            if len(day) != 2 or len(month) != 2 or len(year) != 4:
                return False, "Дата рождения", "Введите корректную дату в формате ДД.ММ.ГГГГ"

            datetime(int(year), int(month), int(day))
        except ValueError:
            return False, "Дата рождения", "Введите корректную дату (например, 15.05.1990)"
        except Exception:
            return False, "Дата рождения", "Введите корректную дату"

        club_id = self.club_combo.currentData()
        if not club_id:
            return False, "Клуб", "Пожалуйста, выберите клуб из списка!"

        photo_url = self.photo_url_edit.text().strip()
        if not photo_url:
            return False, "Фото", "Поле 'URL фотографии' обязательно для заполнения!"

        if not photo_url.startswith(('http://', 'https://')):
            return False, "Фото", "URL фотографии должен начинаться с http:// или https://"

        return True, None, None

    def accept(self):
        is_valid, field_name, error_message = self.validate_fields()
        if not is_valid:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Ошибка")
            msg_box.setText(error_message)
            msg_box.setIcon(QMessageBox.Warning)
            self._setup_message_box(msg_box, error_message)
            msg_box.exec()
            return
        super().accept()


class PlayersWindow(QDialog):
    def __init__(self, is_admin=False, parent=None, user_data=None, db=None):
        super().__init__(parent)
        self.is_admin = is_admin
        self.db = db if db else Database()
        self.user_data = user_data
        self.background_pixmap = None
        self.players_data = []
        self.filtered_players = []

        self.setWindowTitle("Игроки")
        self.setMinimumSize(900, 550)
        self.resize(1000, 600)
        self.setModal(True)
        self.initUI()
        self.load_players()

    def _setup_message_box(self, msg_box, text, is_question=False):
        lines = text.split('\n')
        max_line_length = max(len(line) for line in lines) if lines else len(text)
        width = min(max_line_length * 8 + 80, 550)
        height = len(lines) * 25 + 100

        msg_box.setMinimumWidth(width)
        msg_box.setMaximumWidth(min(width + 50, 600))
        msg_box.setMinimumHeight(height)
        msg_box.setMaximumHeight(min(height + 50, 500))

        if is_question:
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
        else:
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
        self.setStyleSheet("""
            QDialog {
                background-color: #e8f0e8;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        self.content_frame = QFrame()
        self.content_frame.setObjectName("contentFrame")
        self.content_frame.setStyleSheet("""
            QFrame#contentFrame {
                background-color: #f0f5f0;
                border: 2px solid #9bb89b;
                border-radius: 10px;
            }
        """)
        self.content_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        content_layout = QVBoxLayout(self.content_frame)
        content_layout.setSpacing(15)
        content_layout.setContentsMargins(20, 20, 20, 20)

        title_label = QLabel("Игроки")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel#titleLabel {
                color: #1e4a2e;
                font-size: 20px;
                font-weight: bold;
                padding: 8px 20px;
                background-color: rgba(150, 180, 150, 0.3);
                border-radius: 8px;
            }
        """)
        content_layout.addWidget(title_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск игроков по имени, фамилии или клубу...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #ffffff;
                border: 2px solid #9bb89b;
                border-radius: 5px;
                padding: 10px 15px;
                color: #1e3a2e;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #4d7a4d;
                background-color: #f8fff8;
            }
        """)
        self.search_input.textChanged.connect(self.filter_players)
        content_layout.addWidget(self.search_input)

        self.players_table = QTableWidget()
        self.players_table.setColumnCount(6)
        self.players_table.setHorizontalHeaderLabels([
            "Имя", "Фамилия", "Дата рождения", "Клуб", "Фото", ""
        ])

        header = self.players_table.horizontalHeader()

        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        header.setSectionResizeMode(5, QHeaderView.Fixed)

        header.resizeSection(4, 80)
        header.resizeSection(5, 60)

        self.players_table.verticalHeader().setDefaultSectionSize(50)
        self.players_table.verticalHeader().setVisible(False)

        self.players_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.players_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.players_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.players_table.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                border: 2px solid #9bb89b;
                border-radius: 5px;
                color: #1e3a2e;
                font-size: 12px;
                gridline-color: #d0e0d0;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #d4e8d4;
                color: #1e3a2e;
            }
            QHeaderView::section {
                background-color: #6b8f6b;
                color: white;
                font-weight: bold;
                padding: 10px;
                border: none;
                font-size: 12px;
            }
            QHeaderView::section:horizontal {
                border-right: 1px solid #9bb89b;
            }
            QHeaderView::section:last {
                border-right: none;
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

        content_layout.addWidget(self.players_table)

        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(15)

        self.back_button = QPushButton("← Назад")
        self.back_button.setObjectName("backButton")
        self.back_button.setFixedWidth(120)
        self.back_button.setStyleSheet("""
            QPushButton#backButton {
                background-color: #8f9e8f;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton#backButton:hover {
                background-color: #748774;
            }
        """)
        self.back_button.clicked.connect(self.close)
        bottom_layout.addWidget(self.back_button)

        bottom_layout.addStretch()

        self.stats_label = QLabel("Всего игроков: 0")
        self.stats_label.setStyleSheet("""
            QLabel {
                color: #2c4c3b;
                font-weight: bold;
                font-size: 12px;
                background-color: #ffffff;
                padding: 8px 15px;
                border: 2px solid #9bb89b;
                border-radius: 5px;
            }
        """)
        bottom_layout.addWidget(self.stats_label)

        bottom_layout.addStretch()

        self.add_button = QPushButton("➕ Добавить игрока")
        self.add_button.setObjectName("addButton")
        self.add_button.setFixedWidth(160)
        self.add_button.setStyleSheet("""
            QPushButton#addButton {
                background-color: #6b8f6b;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton#addButton:hover {
                background-color: #527352;
            }
        """)
        self.add_button.clicked.connect(self.add_player)
        bottom_layout.addWidget(self.add_button)

        content_layout.addLayout(bottom_layout)

        main_layout.addWidget(self.content_frame)

        self.setAutoFillBackground(True)

    def load_players(self):
        self.players_data = self.db.get_all_players()
        self.filter_players()

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

    def set_background_pixmap(self, pixmap):
        if pixmap and not pixmap.isNull():
            self.background_pixmap = pixmap
            self.content_frame.setStyleSheet("""
                QFrame#contentFrame {
                    background-color: rgba(240, 245, 240, 200);
                    border: 2px solid rgba(155, 184, 155, 160);
                    border-radius: 10px;
                }
            """)
            self.update()

    def resizeEvent(self, event):
        if self.background_pixmap and not self.background_pixmap.isNull():
            self.update()
        super().resizeEvent(event)

    def filter_players(self):
        search_text = self.search_input.text().lower()

        if not search_text:
            self.filtered_players = self.players_data.copy()
        else:
            self.filtered_players = []
            for player in self.players_data:
                if (search_text in player['first_name'].lower() or
                    search_text in player['last_name'].lower() or
                    search_text in player['club_name'].lower()):
                    self.filtered_players.append(player)

        self.update_table()

    def show_photo(self, photo_url, player_name):
        if photo_url:
            dialog = PhotoViewerDialog(photo_url, player_name, self)
            dialog.exec()
        else:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Информация")
            msg_box.setText(f"У игрока {player_name} нет фотографии")
            msg_box.setIcon(QMessageBox.Information)
            self._setup_message_box(msg_box, f"У игрока {player_name} нет фотографии")
            msg_box.exec()

    def delete_player(self, player):
        player_name = f"{player['first_name']} {player['last_name']}"

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Подтверждение удаления")
        msg_box.setText(f'Вы уверены, что хотите удалить игрока "{player_name}"?')
        msg_box.setIcon(QMessageBox.Question)

        lines = f'Вы уверены, что хотите удалить игрока "{player_name}"?'.split('\n')
        max_line_length = max(len(line) for line in lines) if lines else len(f'Вы уверены, что хотите удалить игрока "{player_name}"?')
        width = min(max_line_length * 8 + 80, 550)
        height = len(lines) * 25 + 100

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

        yes_button = msg_box.addButton("Да", QMessageBox.YesRole)
        no_button = msg_box.addButton("Нет", QMessageBox.NoRole)
        no_button.setStyleSheet("""
            QPushButton {
                background-color: #8f9e8f;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 25px;
                font-weight: bold;
                font-size: 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #748774;
            }
        """)
        msg_box.setDefaultButton(no_button)
        msg_box.exec()

        if msg_box.clickedButton() == yes_button:
            success, message = self.db.delete_player(player['id'])
            if success:
                self.load_players()
                success_box = QMessageBox(self)
                success_box.setWindowTitle("Успешно")
                success_box.setText(f'Игрок "{player_name}" успешно удален')
                success_box.setIcon(QMessageBox.Information)
                self._setup_message_box(success_box, f'Игрок "{player_name}" успешно удален')
                success_box.exec()
            else:
                error_box = QMessageBox(self)
                error_box.setWindowTitle("Ошибка")
                error_box.setText(f"Не удалось удалить игрока: {message}")
                error_box.setIcon(QMessageBox.Critical)
                self._setup_message_box(error_box, f"Не удалось удалить игрока: {message}")
                error_box.exec()

    def update_table(self):
        self.players_table.setRowCount(len(self.filtered_players))

        for row, player in enumerate(self.filtered_players):
            name_item = QTableWidgetItem(player['first_name'])
            name_item.setTextAlignment(Qt.AlignCenter)
            self.players_table.setItem(row, 0, name_item)

            surname_item = QTableWidgetItem(player['last_name'])
            surname_item.setTextAlignment(Qt.AlignCenter)
            self.players_table.setItem(row, 1, surname_item)

            birth_item = QTableWidgetItem(player['birth_date'])
            birth_item.setTextAlignment(Qt.AlignCenter)
            self.players_table.setItem(row, 2, birth_item)

            club_item = QTableWidgetItem(player['club_name'])
            club_item.setTextAlignment(Qt.AlignCenter)
            self.players_table.setItem(row, 3, club_item)

            if player.get('photo_url'):
                photo_button = PhotoButton(
                    player['photo_url'],
                    f"{player['first_name']} {player['last_name']}",
                    self
                )
                photo_button.clicked.connect(self.show_photo)
                self.players_table.setCellWidget(row, 4, photo_button)
            else:
                no_photo_label = QLabel("Нет фото")
                no_photo_label.setAlignment(Qt.AlignCenter)
                no_photo_label.setStyleSheet("""
                    QLabel {
                        color: #8f9e8f;
                        font-size: 11px;
                        font-style: italic;
                        padding: 5px;
                    }
                """)
                self.players_table.setCellWidget(row, 4, no_photo_label)

            delete_button = QPushButton()
            delete_button.setFixedSize(32, 32)
            delete_button.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    border: none;
                    border-radius: 6px;
                    padding: 0px;
                    margin: 0px;
                    color: white;
                    font-weight: bold;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
                QPushButton:pressed {
                    background-color: #bd2130;
                }
            """)
            delete_button.setToolTip("Удалить игрока")
            delete_button.setText("✖")
            # ИСПРАВЛЕНО: убираем параметр checked
            delete_button.clicked.connect(partial(self.delete_player, player))

            button_container = QWidget()
            button_layout = QHBoxLayout(button_container)
            button_layout.setContentsMargins(0, 0, 0, 0)
            button_layout.setAlignment(Qt.AlignCenter)
            button_layout.addWidget(delete_button)
            self.players_table.setCellWidget(row, 5, button_container)

        self.stats_label.setText(f"Всего игроков: {len(self.filtered_players)}")

    def add_player(self):
        dialog = AddPlayerDialog(self.db, self.background_pixmap, self)

        if dialog.exec() == QDialog.Accepted:
            player_data = dialog.get_player_data()

            birth_date_str = player_data['birth_date']

            try:
                day, month, year = birth_date_str.split('.')
                if len(day) != 2 or len(month) != 2 or len(year) != 4:
                    msg_box = QMessageBox(self)
                    msg_box.setWindowTitle("Ошибка")
                    msg_box.setText("Введите корректную дату в формате ДД.ММ.ГГГГ")
                    msg_box.setIcon(QMessageBox.Warning)
                    self._setup_message_box(msg_box, "Введите корректную дату в формате ДД.ММ.ГГГГ")
                    msg_box.exec()
                    return

                datetime(int(year), int(month), int(day))
                birth_date_formatted = f"{year}-{month}-{day}"
            except ValueError:
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("Ошибка")
                msg_box.setText("Введите корректную дату (например, 15.05.1990)")
                msg_box.setIcon(QMessageBox.Warning)
                self._setup_message_box(msg_box, "Введите корректную дату (например, 15.05.1990)")
                msg_box.exec()
                return
            except Exception:
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("Ошибка")
                msg_box.setText("Введите корректную дату")
                msg_box.setIcon(QMessageBox.Warning)
                self._setup_message_box(msg_box, "Введите корректную дату")
                msg_box.exec()
                return

            success, player_id, message = self.db.add_player(
                first_name=player_data['first_name'],
                last_name=player_data['last_name'],
                birth_date=birth_date_formatted,
                club_id=player_data['club_id'],
                photo_url=player_data['photo_url']
            )

            if success:
                self.load_players()
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("Успех")
                msg_box.setText(f"Игрок {player_data['first_name']} {player_data['last_name']} успешно добавлен!")
                msg_box.setIcon(QMessageBox.Information)
                self._setup_message_box(msg_box, f"Игрок {player_data['first_name']} {player_data['last_name']} успешно добавлен!")
                msg_box.exec()
            else:
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("Ошибка")
                msg_box.setText(f"Не удалось добавить игрока: {message}")
                msg_box.setIcon(QMessageBox.Critical)
                self._setup_message_box(msg_box, f"Не удалось добавить игрока: {message}")
                msg_box.exec()