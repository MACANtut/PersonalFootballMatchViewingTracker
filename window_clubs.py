# window_clubs.py - исправленная версия с кэшированием и AddClubDialog
import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QLabel, QScrollArea, 
                               QFrame, QDialog, QLineEdit, QFileDialog,
                               QMessageBox, QComboBox, QProgressBar)
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QPixmap, QFont, QPainter, QPalette, QBrush, QIcon
import requests
from io import BytesIO
import os

from database import Database
from image_cache import image_cache


class AddClubDialog(QDialog):
    """Диалог добавления нового клуба"""
    def __init__(self, league_id, league_name, db, parent=None):
        super().__init__(parent)
        self.league_id = league_id
        self.league_name = league_name
        self.db = db
        self.setWindowTitle(f"Добавить клуб в лигу {league_name}")
        self.setFixedSize(500, 350)
        self.setModal(True)
        self.initUI()
    
    def initUI(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #e8f0e8;
            }
            QLabel {
                color: #2c4c3b;
                font-weight: bold;
                font-size: 12px;
            }
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
            QPushButton {
                background-color: #6b8f6b;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 20px;
                font-weight: bold;
                font-size: 12px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #527352;
            }
            QPushButton#cancelButton {
                background-color: #8f9e8f;
            }
            QPushButton#cancelButton:hover {
                background-color: #748774;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 25, 30, 25)
        
        # Заголовок
        title = QLabel(f"Добавление клуба в лигу: {self.league_name}")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 14px; 
            font-weight: bold; 
            padding: 10px;
            color: #1e4a2e;
            background-color: rgba(150, 180, 150, 0.3);
            border-radius: 8px;
        """)
        layout.addWidget(title)
        
        # Название клуба
        name_layout = QHBoxLayout()
        name_label = QLabel("Название клуба:")
        name_label.setFixedWidth(120)
        name_layout.addWidget(name_label)
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Введите название клуба")
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)
        
        # URL логотипа
        logo_layout = QHBoxLayout()
        logo_label = QLabel("URL логотипа:")
        logo_label.setFixedWidth(120)
        logo_layout.addWidget(logo_label)
        
        self.logo_edit = QLineEdit()
        self.logo_edit.setPlaceholderText("https://example.com/logo.png")
        logo_layout.addWidget(self.logo_edit)
        layout.addLayout(logo_layout)
        
        layout.addStretch()
        
        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Отмена")
        cancel_btn.setObjectName("cancelButton")
        cancel_btn.clicked.connect(self.reject)
        
        add_btn = QPushButton("Добавить")
        add_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(add_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
    
    def get_club_data(self):
        """Возвращает данные о клубе"""
        return {
            'name': self.name_edit.text().strip(),
            'logo_url': self.logo_edit.text().strip(),
            'league_id': self.league_id
        }


class ImageLoader:
    """Класс для загрузки изображений по URL (синхронный, для фоновых задач)"""
    
    @staticmethod
    def load_image_from_url_sync(url):
        """Синхронная загрузка изображения (использовать осторожно)"""
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


class ClubWidget(QWidget):
    def __init__(self, club_data, parent=None):
        super().__init__(parent)
        self.club_data = club_data
        self.club_id = club_data['id']
        self.club_name = club_data['name']
        self.logo_url = club_data['emblem_url']
        self.image_loaded = False
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # Эмблема клуба
        self.logo_label = QLabel()
        self.logo_label.setFixedSize(30, 30)
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setStyleSheet("""
            QLabel {
                border: 1px solid #9bb89b;
                border-radius: 3px;
                background-color: white;
                color: #000000;
            }
        """)
        self.logo_label.setText("⚽")
        layout.addWidget(self.logo_label)
        
        # Название клуба
        self.name_label = QLabel(self.club_name)
        self.name_label.setFont(QFont("Arial", 11))
        self.name_label.setStyleSheet("color: #2c4c3b; background-color: transparent;")
        layout.addWidget(self.name_label)
        
        layout.addStretch()
        
        # Кнопка для удаления
        self.delete_button = QPushButton()
        self.delete_button.setFixedSize(30, 30)
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: #ff4444;
                border: none;
                border-radius: 5px;
                padding: 0px;
                margin: 0px;
            }
            QPushButton:hover {
                background-color: #cc0000;
            }
            QPushButton::menu-indicator {
                image: none;
            }
        """)
        self.delete_button.setToolTip("Удалить клуб")
        layout.addWidget(self.delete_button)
        
        self.delete_button.setText("✖")
        
        # Асинхронно загружаем логотип
        if self.logo_url:
            self.load_logo_async()
    
    def load_logo_async(self):
        """Асинхронная загрузка логотипа"""
        self.logo_label.setText("...")
        
        def on_image_loaded(pixmap):
            if pixmap and not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(28, 28, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.logo_label.setPixmap(scaled_pixmap)
                self.logo_label.setText("")
                self.image_loaded = True
            else:
                self.logo_label.setText("⚽")
        
        image_cache.get_image(self.logo_url, on_image_loaded)


class LeagueWidget(QWidget):
    def __init__(self, league_data, db, parent=None):
        super().__init__(parent)
        self.league_id = league_data['id']
        self.league_name = league_data['name']
        self.league_logo_path = league_data['logo_path']
        self.db = db
        self.is_expanded = True
        self.clubs = []
        self.loading = False
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Верхняя панель
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Логотип лиги
        self.logo_label = QLabel()
        self.logo_label.setFixedSize(40, 40)
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setStyleSheet("""
            QLabel {
                border: 2px solid #9bb89b;
                background-color: #ffffff;
                border-radius: 5px;
            }
        """)
        self.load_league_logo()
        header_layout.addWidget(self.logo_label)
        
        # Название лиги
        self.name_label = QLabel(self.league_name)
        self.name_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setStyleSheet("color: #2c4c3b;")
        header_layout.addWidget(self.name_label, 1)
        
        # Кнопка для сворачивания/разворачивания
        self.expand_button = QPushButton()
        self.expand_button.setFixedSize(30, 30)
        self.expand_button.setCheckable(True)
        self.expand_button.setChecked(True)
        self.expand_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                border: none;
                border-radius: 5px;
                padding: 0px;
                margin: 0px;
                color: white;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.expand_button.setToolTip("Свернуть/развернуть список клубов")
        self.expand_button.clicked.connect(self.toggle_clubs)
        header_layout.addWidget(self.expand_button)
        
        # Кнопка для добавления клуба
        self.add_button = QPushButton()
        self.add_button.setFixedSize(30, 30)
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                border: none;
                border-radius: 5px;
                padding: 0px;
                margin: 0px;
                color: white;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.add_button.setToolTip("Добавить новый клуб")
        self.add_button.clicked.connect(self.add_club)
        header_layout.addWidget(self.add_button)
        
        main_layout.addWidget(header_widget)
        
        # Рамка для списка клубов
        self.clubs_frame = QFrame()
        self.clubs_frame.setStyleSheet("""
            QFrame {
                background-color: #d0e0d0;
                border: 2px solid #9bb89b;
                border-radius: 8px;
            }
        """)
        clubs_layout = QVBoxLayout(self.clubs_frame)
        clubs_layout.setContentsMargins(10, 10, 10, 10)
        clubs_layout.setSpacing(8)
        
        # Заголовок
        title_label = QLabel("Список команд данной лиги")
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #2c4c3b; background-color: transparent;")
        clubs_layout.addWidget(title_label)
        
        # Индикатор загрузки
        self.loading_label = QLabel("Загрузка клубов...")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setStyleSheet("color: #6b8f6b; padding: 10px;")
        self.loading_label.setVisible(False)
        clubs_layout.addWidget(self.loading_label)
        
        # Контейнер для клубов
        self.clubs_container = QWidget()
        self.clubs_layout = QVBoxLayout(self.clubs_container)
        self.clubs_layout.setSpacing(5)
        self.clubs_layout.setContentsMargins(10, 5, 10, 5)
        self.clubs_layout.addStretch()
        
        clubs_layout.addWidget(self.clubs_container)
        main_layout.addWidget(self.clubs_frame)
        
        # Устанавливаем текст на кнопки
        self.expand_button.setText("▼")
        self.add_button.setText("+")
        
        # Загружаем клубы из БД
        self.load_clubs()
    
    def load_league_logo(self):
        """Загружает логотип лиги из локального файла"""
        if self.league_logo_path and os.path.exists(self.league_logo_path):
            pixmap = QPixmap(self.league_logo_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(36, 36, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.logo_label.setPixmap(scaled_pixmap)
                self.logo_label.setText("")
                return
        
        # Если файл не найден или не загрузился, показываем иконку по умолчанию
        self.logo_label.setText("🏆")
        self.logo_label.setStyleSheet("""
            QLabel {
                border: 2px solid #9bb89b;
                background-color: #ffffff;
                border-radius: 5px;
                font-size: 24px;
            }
        """)
    
    def load_clubs(self):
        """Загружает клубы из базы данных"""
        self.loading = True
        self.loading_label.setVisible(True)
        self.clubs_container.setVisible(False)
        
        # Используем QTimer для асинхронной загрузки
        QTimer.singleShot(10, self._load_clubs_async)
    
    def _load_clubs_async(self):
        """Асинхронная загрузка клубов"""
        self.clubs = self.db.get_clubs_by_league(self.league_id)
        self.update_clubs_display()
        self.loading = False
        self.loading_label.setVisible(False)
        self.clubs_container.setVisible(True)
    
    def update_clubs_display(self):
        """Обновляет отображение клубов"""
        # Очищаем контейнер
        self.clear_layout(self.clubs_layout)
        
        # Добавляем клубы
        for club in self.clubs:
            club_widget = ClubWidget(club)
            club_widget.delete_button.clicked.connect(
                lambda checked, cid=club['id'], name=club['name']: self.delete_club(cid, name)
            )
            self.clubs_layout.addWidget(club_widget)
        
        self.clubs_layout.addStretch()
    
    def delete_club(self, club_id, club_name):
        """Удаляет клуб из БД"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Подтверждение удаления")
        msg_box.setText(f'Вы уверены, что хотите удалить клуб "{club_name}"?')
        msg_box.setIcon(QMessageBox.Question)
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
        msg_box.exec()
        
        if msg_box.clickedButton() == yes_button:
            success, message = self.db.delete_club(club_id)
            if success:
                self.load_clubs()
                success_box = QMessageBox(self)
                success_box.setWindowTitle("Успешно")
                success_box.setText(f'Клуб "{club_name}" успешно удален')
                success_box.setIcon(QMessageBox.Information)
                success_box.setStyleSheet("""
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
                        min-width: 80px;
                    }
                    QPushButton:hover {
                        background-color: #527352;
                    }
                """)
                success_box.addButton("ОК", QMessageBox.AcceptRole)
                success_box.exec()
            else:
                error_box = QMessageBox(self)
                error_box.setWindowTitle("Ошибка")
                error_box.setText(f"Не удалось удалить клуб: {message}")
                error_box.setIcon(QMessageBox.Critical)
                error_box.setStyleSheet("""
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
                        min-width: 80px;
                    }
                    QPushButton:hover {
                        background-color: #527352;
                    }
                """)
                error_box.addButton("ОК", QMessageBox.AcceptRole)
                error_box.exec()
    
    def toggle_clubs(self):
        self.is_expanded = self.expand_button.isChecked()
        if self.is_expanded:
            self.clubs_frame.show()
            self.expand_button.setText("▼")
        else:
            self.clubs_frame.hide()
            self.expand_button.setText("▶")
    
    def add_club(self):
        """Открывает диалог добавления клуба"""
        dialog = AddClubDialog(self.league_id, self.league_name, self.db, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            club_data = dialog.get_club_data()
            
            success, club_id, message = self.db.add_club(
                club_data["name"],
                club_data["logo_url"],
                club_data["league_id"]
            )
            
            if success:
                self.load_clubs()
                success_box = QMessageBox(self)
                success_box.setWindowTitle("Успешно")
                success_box.setText(f'Клуб "{club_data["name"]}" успешно добавлен в лигу "{self.league_name}"!')
                success_box.setIcon(QMessageBox.Information)
                success_box.setStyleSheet("""
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
                        min-width: 80px;
                    }
                    QPushButton:hover {
                        background-color: #527352;
                    }
                """)
                success_box.addButton("ОК", QMessageBox.AcceptRole)
                success_box.exec()
            else:
                error_box = QMessageBox(self)
                error_box.setWindowTitle("Ошибка")
                error_box.setText(f"Не удалось добавить клуб: {message}")
                error_box.setIcon(QMessageBox.Critical)
                error_box.setStyleSheet("""
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
                        min-width: 80px;
                    }
                    QPushButton:hover {
                        background-color: #527352;
                    }
                """)
                error_box.addButton("ОК", QMessageBox.AcceptRole)
                error_box.exec()
    
    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()


class ClubsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.background_pixmap = None
        self.setWindowTitle("Футбольные лиги")
        self.setMinimumSize(600, 525)
        self.loading_complete = False
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #e8f0e8;
            }
            QScrollArea {
                background-color: transparent;
                border: none;
            }
        """)
        
        central_widget = QWidget()
        central_widget.setStyleSheet("background-color: transparent;")
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        self.content_frame = QFrame()
        self.content_frame.setObjectName("contentFrame")
        self.content_frame.setStyleSheet("""
            QFrame#contentFrame {
                background-color: rgba(240, 245, 240, 200);
                border: 2px solid rgba(155, 184, 155, 160);
                border-radius: 10px;
            }
        """)
        
        content_layout = QVBoxLayout(self.content_frame)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)
        
        # Заголовок
        title_label = QLabel("Клубы")
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
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
        
        # Индикатор загрузки
        self.loading_label = QLabel("Загрузка данных...")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setStyleSheet("color: #6b8f6b; font-size: 14px; padding: 20px;")
        content_layout.addWidget(self.loading_label)
        
        # Скролл-область
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameStyle(QFrame.Shape.NoFrame)
        scroll.setVisible(False)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
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
        content_layout.addWidget(scroll)
        
        # Контейнер для лиг
        leagues_container = QWidget()
        leagues_container.setStyleSheet("background-color: transparent;")
        self.leagues_layout = QVBoxLayout(leagues_container)
        self.leagues_layout.setSpacing(15)
        self.leagues_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll.setWidget(leagues_container)
        
        main_layout.addWidget(self.content_frame)
        
        self.setAutoFillBackground(True)
        
        # Загружаем лиги асинхронно
        QTimer.singleShot(10, self.load_leagues_async)
    
    def load_leagues_async(self):
        """Асинхронная загрузка лиг"""
        leagues = self.db.get_all_leagues()
        
        for league_data in leagues:
            league_widget = LeagueWidget(league_data, self.db)
            self.leagues_layout.addWidget(league_widget)
        
        self.leagues_layout.addStretch()
        
        # Скрываем индикатор загрузки и показываем содержимое
        self.loading_label.setVisible(False)
        scroll = self.findChild(QScrollArea)
        if scroll:
            scroll.setVisible(True)
    
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = ClubsWindow()
    window.show()
    sys.exit(app.exec())