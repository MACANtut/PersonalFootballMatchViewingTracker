# window_players.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                               QLabel, QPushButton, QFrame, QTableWidget,
                               QTableWidgetItem, QHeaderView, QLineEdit,
                               QWidget, QFileDialog, QMessageBox, QComboBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QFont, QPainter
import requests
from io import BytesIO

from database import Database


class ImageLoader:
    """Класс для загрузки изображений по URL"""
    
    @staticmethod
    def load_image_from_url(url):
        """Загружает изображение по URL и возвращает QPixmap"""
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
        except Exception as e:
            print(f"Ошибка загрузки изображения: {e}")
            return None


class PhotoViewerDialog(QDialog):
    """Диалог для просмотра фотографии игрока"""
    def __init__(self, photo_url, player_name, parent=None):
        super().__init__(parent)
        self.photo_url = photo_url
        self.player_name = player_name
        self.setWindowTitle(f"Фото: {player_name}")
        self.setModal(True)
        self.initUI()
        self.load_photo()
        
    def initUI(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #e8f0e8;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Контейнер для фото
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
        
        # Метка для фото
        self.photo_label = QLabel()
        self.photo_label.setAlignment(Qt.AlignCenter)
        self.photo_label.setMinimumSize(300, 300)
        self.photo_label.setText("Загрузка изображения...")
        photo_layout.addWidget(self.photo_label)
        
        layout.addWidget(photo_frame)
        
        # Кнопка закрытия
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
        
        # Устанавливаем фиксированный размер окна
        self.setFixedSize(350, 400)
    
    def load_photo(self):
        """Загружает фото по URL"""
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
    """Кастомное поле для ввода даты с маской"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("ДД.ММ.ГГГГ")
        self.setMaxLength(10)
        
        # Устанавливаем маску ввода
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


class PhotoButton(QLabel):
    """Кнопка-надпись для просмотра фото"""
    clicked = Signal(str, str)  # photo_url, player_name
    
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
        self.setFixedSize(600, 620)
        self.setModal(True)
        self.initUI()
        
    def initUI(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #e8f0e8;
            }
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Контентный фрейм
        self.content_frame = QFrame()
        self.content_frame.setObjectName("contentFrame")
        self.content_frame.setStyleSheet("""
            QFrame#contentFrame {
                background-color: #f0f5f0;
                border: 2px solid #9bb89b;
                border-radius: 10px;
            }
        """)
        
        content_layout = QVBoxLayout(self.content_frame)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(30, 30, 30, 30)
        
        # Заголовок
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
        
        # Форма
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)
        
        # Поле Имя
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
        
        # Поле Фамилия
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
        
        # Поле Дата рождения
        birth_layout = QHBoxLayout()
        birth_label = QLabel("Дата рождения:")
        birth_label.setFixedWidth(120)
        birth_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        birth_label.setStyleSheet("color: #2c4c3b; font-weight: bold; font-size: 12px;")
        self.birth_input = DateLineEdit()
        birth_layout.addWidget(birth_label)
        birth_layout.addWidget(self.birth_input)
        form_layout.addLayout(birth_layout)
        
        # Поле Клуб - выпадающий список с белым фоном
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
        
        # Загружаем список клубов
        clubs = self.db.get_all_clubs_for_select()
        self.club_combo.addItem("-- Выберите клуб --", None)
        for club in clubs:
            display_text = f"{club['name']} ({club['league_name']})" if club['league_name'] != 'Без лиги' else club['name']
            self.club_combo.addItem(display_text, club['id'])
        
        club_layout.addWidget(club_label)
        club_layout.addWidget(self.club_combo)
        form_layout.addLayout(club_layout)
        
        # Поле URL фотографии
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
        
        # Кнопки
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
        """Возвращает данные игрока из полей ввода"""
        club_id = self.club_combo.currentData()
        return {
            'first_name': self.name_input.text().strip(),
            'last_name': self.surname_input.text().strip(),
            'birth_date': self.birth_input.text().strip(),
            'club_id': club_id if club_id else None,
            'photo_url': self.photo_url_edit.text().strip()
        }
    
    def validate_fields(self):
        """Проверяет заполнение обязательных полей"""
        if not self.name_input.text().strip():
            return False, "Имя", "Поле 'Имя' обязательно для заполнения!"
        
        if not self.surname_input.text().strip():
            return False, "Фамилия", "Поле 'Фамилия' обязательно для заполнения!"
        
        birth_date = self.birth_input.text().strip()
        if not birth_date or '_' in birth_date:
            return False, "Дата рождения", "Поле 'Дата рождения' обязательно для заполнения!"
        
        # Проверяем формат даты
        try:
            day, month, year = birth_date.split('.')
            if len(day) != 2 or len(month) != 2 or len(year) != 4:
                return False, "Дата рождения", "Неверный формат даты! Используйте ДД.ММ.ГГГГ"
        except:
            return False, "Дата рождения", "Неверный формат даты! Используйте ДД.ММ.ГГГГ"
        
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
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #e8f0e8;
                }
                QMessageBox QLabel {
                    color: #2c4c3b;
                    font-weight: bold;
                    font-size: 12px;
                    min-width: 250px;
                    padding: 15px;
                }
                QPushButton {
                    background-color: #6b8f6b;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 8px 25px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #527352;
                }
            """)
            ok_button = msg_box.addButton("ОК", QMessageBox.AcceptRole)
            msg_box.exec()
            return
        super().accept()


class PlayersWindow(QDialog):
    def __init__(self, is_admin=False, parent=None):
        super().__init__(parent)
        self.is_admin = is_admin
        self.db = Database()
        self.background_pixmap = None
        self.players_data = []
        self.filtered_players = []
        
        self.setWindowTitle("Игроки")
        self.setFixedSize(1000, 600)
        self.setModal(True)
        self.initUI()
        self.load_players()
        
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
        self.players_table.setColumnCount(5)
        self.players_table.setHorizontalHeaderLabels([
            "Имя", "Фамилия", "Дата рождения", "Клуб", "Фото"
        ])
        
        header = self.players_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        header.resizeSection(4, 100)
        
        self.players_table.verticalHeader().setDefaultSectionSize(50)
        self.players_table.verticalHeader().setVisible(False)
        
        self.players_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.players_table.setEditTriggers(QTableWidget.NoEditTriggers)
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
        
        if self.is_admin:
            self.add_button = QPushButton("Добавить игрока")
            self.add_button.setObjectName("addButton")
            self.add_button.setFixedWidth(150)
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
        """Загружает игроков из базы данных"""
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
        """Фильтрация игроков по поисковому запросу"""
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
        """Показывает фотографию игрока"""
        if photo_url:
            dialog = PhotoViewerDialog(photo_url, player_name, self)
            dialog.exec()
        else:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Информация")
            msg_box.setText(f"У игрока {player_name} нет фотографии")
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #e8f0e8;
                }
                QMessageBox QLabel {
                    color: #2c4c3b;
                    font-weight: bold;
                    font-size: 12px;
                    min-width: 250px;
                    padding: 15px;
                }
                QPushButton {
                    background-color: #6b8f6b;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 8px 25px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #527352;
                }
            """)
            ok_button = msg_box.addButton("ОК", QMessageBox.AcceptRole)
            msg_box.exec()
    
    def update_table(self):
        """Обновляет таблицу с отфильтрованными игроками"""
        self.players_table.setRowCount(len(self.filtered_players))
        
        for row, player in enumerate(self.filtered_players):
            # Имя
            name_item = QTableWidgetItem(player['first_name'])
            name_item.setTextAlignment(Qt.AlignCenter)
            self.players_table.setItem(row, 0, name_item)
            
            # Фамилия
            surname_item = QTableWidgetItem(player['last_name'])
            surname_item.setTextAlignment(Qt.AlignCenter)
            self.players_table.setItem(row, 1, surname_item)
            
            # Дата рождения
            birth_item = QTableWidgetItem(player['birth_date'])
            birth_item.setTextAlignment(Qt.AlignCenter)
            self.players_table.setItem(row, 2, birth_item)
            
            # Клуб
            club_item = QTableWidgetItem(player['club_name'])
            club_item.setTextAlignment(Qt.AlignCenter)
            self.players_table.setItem(row, 3, club_item)
            
            # Кнопка для просмотра фото
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
        
        self.stats_label.setText(f"Всего игроков: {len(self.filtered_players)}")
    
    def add_player(self):
        """Открывает диалог добавления нового игрока"""
        dialog = AddPlayerDialog(self.db, self.background_pixmap, self)
        
        if dialog.exec() == QDialog.Accepted:
            player_data = dialog.get_player_data()
            
            # Преобразуем дату из формата ДД.ММ.ГГГГ в ГГГГ-ММ-ДД
            birth_date_str = player_data['birth_date']
            try:
                day, month, year = birth_date_str.split('.')
                birth_date_formatted = f"{year}-{month}-{day}"
            except:
                birth_date_formatted = birth_date_str
            
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
                msg_box.setStyleSheet("""
                    QMessageBox {
                        background-color: #e8f0e8;
                    }
                    QMessageBox QLabel {
                        color: #2c4c3b;
                        font-weight: bold;
                        font-size: 12px;
                        min-width: 250px;
                        padding: 15px;
                    }
                    QPushButton {
                        background-color: #6b8f6b;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        padding: 8px 25px;
                        font-weight: bold;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background-color: #527352;
                    }
                """)
                ok_button = msg_box.addButton("ОК", QMessageBox.AcceptRole)
                msg_box.exec()
            else:
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("Ошибка")
                msg_box.setText(f"Не удалось добавить игрока: {message}")
                msg_box.setIcon(QMessageBox.Critical)
                msg_box.setStyleSheet("""
                    QMessageBox {
                        background-color: #e8f0e8;
                    }
                    QMessageBox QLabel {
                        color: #2c4c3b;
                        font-weight: bold;
                        font-size: 12px;
                        min-width: 250px;
                        padding: 15px;
                    }
                    QPushButton {
                        background-color: #6b8f6b;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        padding: 8px 25px;
                        font-weight: bold;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background-color: #527352;
                    }
                """)
                ok_button = msg_box.addButton("ОК", QMessageBox.AcceptRole)
                msg_box.exec()