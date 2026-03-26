import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QLabel, QScrollArea, 
                               QFrame, QDialog, QLineEdit, QFileDialog,
                               QMessageBox, QComboBox)
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QPixmap, QFont, QPainter, QPalette, QBrush, QIcon
import requests
from io import BytesIO
import os

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


class AddClubDialog(QDialog):
    def __init__(self, league_id, league_name, db, parent=None):
        super().__init__(parent)
        self.league_id = league_id
        self.league_name = league_name
        self.db = db
        self.logo_url = None
        self.setWindowTitle(f"Добавление клуба в {league_name}")
        self.setFixedSize(500, 550)
        self.initUI()
        
    def initUI(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #e8f0e8;
            }
            QLabel {
                color: #2c4c3b;
            }
            QLineEdit, QComboBox {
                padding: 8px;
                border: 2px solid #9bb89b;
                border-radius: 5px;
                font-size: 12px;
                background-color: white;
                color: #000000;
            }
            QLineEdit:focus, QComboBox:focus {
                border-color: #6b8f6b;
            }
            QPushButton {
                border: none;
                border-radius: 5px;
                font-size: 12px;
                font-weight: bold;
                padding: 8px 15px;
                color: white;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок
        title_label = QLabel("Добавление нового клуба")
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #1e4a2e;")
        layout.addWidget(title_label)
        
        league_title = QLabel(self.league_name)
        league_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        league_title.setStyleSheet("""
            color: #1e4a2e; 
            padding: 10px; 
            background-color: #d0e0d0; 
            border: 2px solid #9bb89b;
            border-radius: 8px;
        """)
        league_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(league_title)
        
        # Поле для названия клуба
        name_layout = QVBoxLayout()
        name_label = QLabel("Название клуба:")
        name_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        name_layout.addWidget(name_label)
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Введите название клуба")
        self.name_edit.textChanged.connect(self.check_fields)
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)
        
        # Поле для URL эмблемы
        url_layout = QVBoxLayout()
        url_label = QLabel("URL эмблемы клуба:")
        url_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        url_layout.addWidget(url_label)
        
        url_input_layout = QHBoxLayout()
        
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("Вставьте ссылку на изображение (https://...)")
        self.url_edit.textChanged.connect(self.on_url_changed)
        url_input_layout.addWidget(self.url_edit)
        
        self.load_btn = QPushButton("Загрузить")
        self.load_btn.setFixedSize(100, 35)
        self.load_btn.setStyleSheet("""
            QPushButton {
                background-color: #6b8f6b;
                color: white;
            }
            QPushButton:hover {
                background-color: #527352;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.load_btn.clicked.connect(self.load_image_from_url)
        self.load_btn.setEnabled(False)
        url_input_layout.addWidget(self.load_btn)
        
        url_layout.addLayout(url_input_layout)
        layout.addLayout(url_layout)
        
        # Предпросмотр эмблемы
        preview_container = QWidget()
        preview_layout = QVBoxLayout(preview_container)
        preview_layout.setAlignment(Qt.AlignCenter)
        
        preview_title = QLabel("Предпросмотр:")
        preview_title.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        preview_layout.addWidget(preview_title)
        
        self.preview_label = QLabel()
        self.preview_label.setFixedSize(120, 120)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("""
            QLabel {
                border: 2px solid #9bb89b;
                border-radius: 10px;
                background-color: #ffffff;
                padding: 5px;
                color: #000000;
            }
        """)
        self.preview_label.setText("Введите URL и\nнажмите Загрузить")
        preview_layout.addWidget(self.preview_label)
        
        layout.addWidget(preview_container)
        
        # Индикатор загрузки
        self.loading_label = QLabel("")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setStyleSheet("color: #6b8f6b; font-size: 10px;")
        layout.addWidget(self.loading_label)
        
        layout.addStretch()
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        buttons_layout.setAlignment(Qt.AlignCenter)
        
        self.add_btn = QPushButton("Добавить")
        self.add_btn.setFixedSize(130, 40)
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.add_btn.clicked.connect(self.accept)
        self.add_btn.setEnabled(False)
        buttons_layout.addWidget(self.add_btn)
        
        cancel_btn = QPushButton("Отменить")
        cancel_btn.setFixedSize(130, 40)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
    
    def on_url_changed(self):
        url = self.url_edit.text().strip()
        is_valid_url = url.startswith(('http://', 'https://'))
        self.load_btn.setEnabled(is_valid_url)
        self.check_fields()
    
    def load_image_from_url(self):
        url = self.url_edit.text().strip()
        if not url:
            return
        
        self.loading_label.setText("Загрузка изображения...")
        self.load_btn.setEnabled(False)
        self.preview_label.setText("Загрузка...")
        self.preview_label.setPixmap(QPixmap())
        
        QTimer.singleShot(100, self._perform_image_load)
    
    def _perform_image_load(self):
        url = self.url_edit.text().strip()
        pixmap = ImageLoader.load_image_from_url(url)
        
        if pixmap and not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(116, 116, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.preview_label.setPixmap(scaled_pixmap)
            self.preview_label.setText("")
            self.logo_url = url
            self.loading_label.setText("✓ Изображение загружено")
            self.loading_label.setStyleSheet("color: #4CAF50; font-size: 10px;")
        else:
            self.preview_label.setText("Ошибка загрузки\nизображения")
            self.preview_label.setPixmap(QPixmap())
            self.logo_url = None
            self.loading_label.setText("✗ Ошибка загрузки")
            self.loading_label.setStyleSheet("color: #f44336; font-size: 10px;")
        
        self.load_btn.setEnabled(True)
        self.check_fields()
    
    def check_fields(self):
        is_valid = bool(self.name_edit.text().strip()) and bool(self.logo_url)
        self.add_btn.setEnabled(is_valid)
    
    def get_club_data(self):
        return {
            "name": self.name_edit.text().strip(),
            "logo_url": self.logo_url,
            "league_id": self.league_id
        }
    
    def accept(self):
        super().accept()


class ClubWidget(QWidget):
    def __init__(self, club_data, parent=None):
        super().__init__(parent)
        self.club_data = club_data
        self.club_id = club_data['id']
        self.club_name = club_data['name']
        self.logo_url = club_data['emblem_url']
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # Эмблема клуба
        self.logo_label = QLabel()
        self.logo_label.setFixedSize(25, 25)
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setStyleSheet("""
            QLabel {
                border: 1px solid #9bb89b;
                border-radius: 3px;
                background-color: white;
                color: #000000;
            }
        """)
        
        if self.logo_url:
            self.load_logo(self.logo_url)
        else:
            self.logo_label.setText("⚽")
        
        layout.addWidget(self.logo_label)
        
        # Название клуба
        self.name_label = QLabel(self.club_name)
        self.name_label.setFont(QFont("Arial", 11))
        self.name_label.setStyleSheet("color: #2c4c3b; background-color: transparent;")
        layout.addWidget(self.name_label)
        
        layout.addStretch()
        
        # Красная кнопка с крестиком для удаления
        self.delete_button = QPushButton()
        self.delete_button.setFixedSize(30, 30)
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: #ff4444;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #cc0000;
            }
        """)
        self.delete_button.setToolTip("Удалить клуб")
        layout.addWidget(self.delete_button)
    
    def load_logo(self, url):
        self.logo_label.setText("...")
        
        def on_image_loaded(pixmap):
            if pixmap and not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(23, 23, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.logo_label.setPixmap(scaled_pixmap)
                self.logo_label.setText("")
            else:
                self.logo_label.setText("⚽")
        
        QTimer.singleShot(100, lambda: self._load_logo_async(url, on_image_loaded))
    
    def _load_logo_async(self, url, callback):
        pixmap = ImageLoader.load_image_from_url(url)
        callback(pixmap)
    
    def set_button_icon(self, pixmap):
        """Устанавливает иконку на кнопку удаления"""
        if pixmap and not pixmap.isNull():
            icon_pixmap = pixmap.scaled(25, 25, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.delete_button.setIcon(QIcon(icon_pixmap))
            self.delete_button.setIconSize(QSize(25, 25))
            self.delete_button.setText("")
        else:
            self.delete_button.setText("✖")


class LeagueWidget(QWidget):
    def __init__(self, league_data, db, parent=None):
        super().__init__(parent)
        self.league_id = league_data['id']
        self.league_name = league_data['name']
        self.league_logo = league_data['logo_path']
        self.db = db
        self.is_expanded = True
        self.clubs = []
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Верхняя панель
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Логотип лиги
        self.logo_label = QLabel()
        pixmap = QPixmap(self.league_logo)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.logo_label.setPixmap(pixmap)
            self.logo_label.setFixedSize(40, 40)
        else:
            self.logo_label.setText("🏆")
            self.logo_label.setFixedSize(40, 40)
            self.logo_label.setStyleSheet("border: 2px solid #9bb89b; background-color: #ffffff; color: #2c4c3b; font-size: 20px;")
        self.logo_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(self.logo_label)
        
        # Название лиги
        self.name_label = QLabel(self.league_name)
        self.name_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setStyleSheet("color: #2c4c3b;")
        header_layout.addWidget(self.name_label, 1)
        
        # Зеленая кнопка для сворачивания/разворачивания
        self.expand_button = QPushButton()
        self.expand_button.setFixedSize(30, 30)
        self.expand_button.setCheckable(True)
        self.expand_button.setChecked(True)
        self.expand_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.expand_button.setToolTip("Свернуть/развернуть список клубов")
        self.expand_button.clicked.connect(self.toggle_clubs)
        header_layout.addWidget(self.expand_button)
        
        # Синяя кнопка для добавления клуба
        self.add_button = QPushButton()
        self.add_button.setFixedSize(30, 30)
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
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
        
        # Контейнер для клубов
        self.clubs_container = QWidget()
        self.clubs_layout = QVBoxLayout(self.clubs_container)
        self.clubs_layout.setSpacing(5)
        self.clubs_layout.setContentsMargins(10, 5, 10, 5)
        self.clubs_layout.addStretch()
        
        clubs_layout.addWidget(self.clubs_container)
        main_layout.addWidget(self.clubs_frame)
        
        # Устанавливаем стандартные символы на кнопки
        self.set_default_button_icons()
        
        # Загружаем клубы из БД
        self.load_clubs()
    
    def set_default_button_icons(self):
        """Устанавливает стандартные символы на кнопки"""
        self.expand_button.setText("▼")
        self.add_button.setText("+")
    
    def set_button_icon(self, button, icon_pixmap):
        """Устанавливает иконку на кнопку"""
        if icon_pixmap and not icon_pixmap.isNull():
            scaled_pixmap = icon_pixmap.scaled(25, 25, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            button.setIcon(QIcon(scaled_pixmap))
            button.setIconSize(QSize(25, 25))
            button.setText("")
        else:
            # Если иконка не загружена, показываем стандартный символ
            if button == self.expand_button:
                button.setText("▼" if self.is_expanded else "▶")
            elif button == self.add_button:
                button.setText("+")
    
    def load_custom_icon(self, button_type):
        """Загружает пользовательскую иконку для кнопки"""
        file, _ = QFileDialog.getOpenFileName(
            self,
            f"Выберите изображение для кнопки",
            "",
            "Изображения (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file:
            pixmap = QPixmap(file)
            if not pixmap.isNull():
                if button_type == "expand":
                    self.set_button_icon(self.expand_button, pixmap)
                    # Сохраняем настройку
                    if hasattr(self.parent(), 'save_button_icon'):
                        self.parent().save_button_icon("expand", file)
                elif button_type == "add":
                    self.set_button_icon(self.add_button, pixmap)
                    if hasattr(self.parent(), 'save_button_icon'):
                        self.parent().save_button_icon("add", file)
    
    def contextMenuEvent(self, event):
        """Контекстное меню для смены иконок"""
        from PySide6.QtWidgets import QMenu
        
        # Определяем, на какую кнопку нажали
        button = self.childAt(event.pos())
        
        if button == self.expand_button:
            menu = QMenu(self)
            change_icon_action = menu.addAction("Сменить иконку для кнопки 'Свернуть/Развернуть'")
            reset_action = menu.addAction("Сбросить иконку")
            
            action = menu.exec(event.globalPos())
            
            if action == change_icon_action:
                self.load_custom_icon("expand")
            elif action == reset_action:
                self.expand_button.setText("▼" if self.is_expanded else "▶")
                self.expand_button.setIcon(QIcon())
                if hasattr(self.parent(), 'reset_button_icon'):
                    self.parent().reset_button_icon("expand")
        
        elif button == self.add_button:
            menu = QMenu(self)
            change_icon_action = menu.addAction("Сменить иконку для кнопки 'Добавить'")
            reset_action = menu.addAction("Сбросить иконку")
            
            action = menu.exec(event.globalPos())
            
            if action == change_icon_action:
                self.load_custom_icon("add")
            elif action == reset_action:
                self.add_button.setText("+")
                self.add_button.setIcon(QIcon())
                if hasattr(self.parent(), 'reset_button_icon'):
                    self.parent().reset_button_icon("add")
    
    def load_clubs(self):
        """Загружает клубы из базы данных"""
        self.clubs = self.db.get_clubs_by_league(self.league_id)
        self.update_clubs_display()
    
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
            
            # Добавляем контекстное меню для кнопки удаления
            club_widget.delete_button.setContextMenuPolicy(Qt.CustomContextMenu)
            club_widget.delete_button.customContextMenuRequested.connect(
                lambda pos, w=club_widget: self.show_delete_button_menu(w)
            )
            
            self.clubs_layout.addWidget(club_widget)
        
        self.clubs_layout.addStretch()
    
    def show_delete_button_menu(self, club_widget):
        """Показывает контекстное меню для кнопки удаления"""
        from PySide6.QtWidgets import QMenu
        
        menu = QMenu(self)
        change_icon_action = menu.addAction("Сменить иконку для кнопки 'Удалить'")
        reset_action = menu.addAction("Сбросить иконку")
        
        action = menu.exec(QCursor.pos())
        
        if action == change_icon_action:
            file, _ = QFileDialog.getOpenFileName(
                self,
                "Выберите изображение для кнопки удаления",
                "",
                "Изображения (*.png *.jpg *.jpeg *.bmp *.gif)"
            )
            if file:
                pixmap = QPixmap(file)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(25, 25, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    club_widget.delete_button.setIcon(QIcon(scaled_pixmap))
                    club_widget.delete_button.setIconSize(QSize(25, 25))
                    club_widget.delete_button.setText("")
                    # Сохраняем настройку для конкретного клуба
                    if hasattr(self, 'save_club_button_icon'):
                        self.save_club_button_icon(club_widget.club_id, file)
        elif action == reset_action:
            club_widget.delete_button.setText("✖")
            club_widget.delete_button.setIcon(QIcon())
            if hasattr(self, 'reset_club_button_icon'):
                self.reset_club_button_icon(club_widget.club_id)
    
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
            if not self.expand_button.icon().isNull():
                # Если есть иконка, оставляем её
                pass
            else:
                self.expand_button.setText("▼")
        else:
            self.clubs_frame.hide()
            if not self.expand_button.icon().isNull():
                # Если есть иконка, оставляем её
                pass
            else:
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
        
        # Скролл-область
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameStyle(QFrame.Shape.NoFrame)
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
        
        # Загружаем лиги из БД
        self.load_leagues()
        
        main_layout.addWidget(self.content_frame)
        
        self.setAutoFillBackground(True)
    
    def load_leagues(self):
        """Загружает лиги из базы данных"""
        leagues = self.db.get_all_leagues()
        
        for league_data in leagues:
            league_widget = LeagueWidget(league_data, self.db)
            self.leagues_layout.addWidget(league_widget)
        
        self.leagues_layout.addStretch()
    
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