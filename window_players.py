from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                               QLabel, QPushButton, QFrame, QTableWidget,
                               QTableWidgetItem, QHeaderView, QLineEdit,
                               QWidget, QFileDialog, QMessageBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QFont, QPainter


class PhotoViewerDialog(QDialog):
    """Диалог для просмотра фотографии игрока"""
    def __init__(self, photo_path, player_name, parent=None):
        super().__init__(parent)
        self.photo_path = photo_path
        self.player_name = player_name
        self.setWindowTitle(f"Фото: {player_name}")
        self.setModal(True)
        self.initUI()
        
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
        
        # Загружаем и отображаем фото
        pixmap = QPixmap(self.photo_path)
        if not pixmap.isNull():
            # Масштабируем изображение до меньшего размера
            scaled_pixmap = pixmap.scaled(
                300, 300,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            
            photo_label = QLabel()
            photo_label.setPixmap(scaled_pixmap)
            photo_label.setAlignment(Qt.AlignCenter)
            photo_layout.addWidget(photo_label)
        else:
            error_label = QLabel("Не удалось загрузить изображение")
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setStyleSheet("color: #d46b6b; font-size: 14px; padding: 30px;")
            photo_layout.addWidget(error_label)
        
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


class DateLineEdit(QLineEdit):
    """Кастомное поле для ввода даты с маской"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("ДД.ММ.ГГГГ")
        self.setMaxLength(10)
        
        # Устанавливаем маску ввода
        self.setInputMask("00.00.0000")
        
        # Устанавливаем такой же стиль как у других полей
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
    clicked = Signal(str, str)  # photo_path, player_name
    
    def __init__(self, photo_path, player_name, parent=None):
        super().__init__(parent)
        self.photo_path = photo_path
        self.player_name = player_name
        self.setup_ui()
        
    def setup_ui(self):
        self.setText("Фото")
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
            self.clicked.emit(self.photo_path, self.player_name)


class AddPlayerDialog(QDialog):
    def __init__(self, background_pixmap=None, parent=None):
        super().__init__(parent)
        self.photo_path = None
        self.background_pixmap = background_pixmap
        self.setWindowTitle("Добавление игрока")
        self.setFixedSize(500, 600)
        self.setModal(True)
        self.initUI()
        
    def initUI(self):
        # Основной стиль окна
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
        
        # Поле Дата рождения (с маской ввода)
        birth_layout = QHBoxLayout()
        birth_label = QLabel("Дата рождения:")
        birth_label.setFixedWidth(120)
        birth_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        birth_label.setStyleSheet("color: #2c4c3b; font-weight: bold; font-size: 12px;")
        self.birth_input = DateLineEdit()
        birth_layout.addWidget(birth_label)
        birth_layout.addWidget(self.birth_input)
        form_layout.addLayout(birth_layout)
        
        # Поле Клуб
        club_layout = QHBoxLayout()
        club_label = QLabel("Клуб:")
        club_label.setFixedWidth(120)
        club_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        club_label.setStyleSheet("color: #2c4c3b; font-weight: bold; font-size: 12px;")
        self.club_input = QLineEdit()
        self.club_input.setPlaceholderText("Введите название клуба")
        self.club_input.setStyleSheet("""
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
        club_layout.addWidget(club_label)
        club_layout.addWidget(self.club_input)
        form_layout.addLayout(club_layout)
        
        # Поле Фотография
        photo_layout = QHBoxLayout()
        photo_label = QLabel("Фотография игрока:")
        photo_label.setFixedWidth(120)
        photo_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        photo_label.setStyleSheet("color: #2c4c3b; font-weight: bold; font-size: 12px;")
        
        self.photo_path_edit = QLineEdit()
        self.photo_path_edit.setReadOnly(True)
        self.photo_path_edit.setPlaceholderText("Выберите фотографию")
        self.photo_path_edit.setStyleSheet("""
            QLineEdit {
                background-color: #f0f5f0;
                border: 2px solid #9bb89b;
                border-radius: 5px;
                padding: 8px;
                color: #1e3a2e;
                font-size: 12px;
            }
        """)
        
        browse_button = QPushButton("Обзор...")
        browse_button.setFixedWidth(80)
        browse_button.setStyleSheet("""
            QPushButton {
                background-color: #6b8f6b;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #527352;
            }
        """)
        browse_button.clicked.connect(self.browse_photo)
        
        photo_layout.addWidget(photo_label)
        photo_layout.addWidget(self.photo_path_edit)
        photo_layout.addWidget(browse_button)
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
        
        # Применяем фон, если он есть
        if self.background_pixmap:
            self.apply_background()
    
    def paintEvent(self, event):
        """Рисование фона"""
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
        """Применяет фон к элементам окна"""
        if self.background_pixmap and not self.background_pixmap.isNull():
            # Делаем контентный фрейм полупрозрачным
            self.content_frame.setStyleSheet("""
                QFrame#contentFrame {
                    background-color: rgba(240, 245, 240, 200);
                    border: 2px solid rgba(155, 184, 155, 160);
                    border-radius: 10px;
                }
            """)
            
            # Делаем поля ввода полупрозрачными
            edit_style = """
                QLineEdit {
                    background-color: rgba(255, 255, 255, 220);
                    border: 2px solid rgba(155, 184, 155, 160);
                    border-radius: 5px;
                    padding: 8px;
                    color: #1e3a2e;
                    font-size: 12px;
                }
                QLineEdit:focus {
                    border-color: rgba(77, 122, 77, 200);
                    background-color: rgba(248, 255, 248, 230);
                }
            """
            
            self.name_input.setStyleSheet(edit_style)
            self.surname_input.setStyleSheet(edit_style)
            self.birth_input.setStyleSheet(edit_style)
            self.club_input.setStyleSheet(edit_style)
            
            self.photo_path_edit.setStyleSheet("""
                QLineEdit {
                    background-color: rgba(240, 245, 240, 200);
                    border: 2px solid rgba(155, 184, 155, 160);
                    border-radius: 5px;
                    padding: 8px;
                    color: #1e3a2e;
                    font-size: 12px;
                }
            """)
            
            # Делаем кнопки полупрозрачными
            browse_button = self.findChild(QPushButton, "")
            if browse_button and browse_button.text() == "Обзор...":
                browse_button.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(107, 143, 107, 220);
                        color: white;
                        border: none;
                        border-radius: 5px;
                        padding: 8px;
                        font-weight: bold;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background-color: rgba(82, 115, 82, 240);
                    }
                """)
    
    def resizeEvent(self, event):
        """Обновляет фон при изменении размера"""
        if self.background_pixmap and not self.background_pixmap.isNull():
            self.update()
        super().resizeEvent(event)
    
    def browse_photo(self):
        file, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите фотографию игрока",
            "",
            "Изображения (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file:
            self.photo_path = file
            self.photo_path_edit.setText(file)
    
    def get_player_data(self):
        """Возвращает данные игрока из полей ввода"""
        return {
            'name': self.name_input.text().strip(),
            'surname': self.surname_input.text().strip(),
            'birth_date': self.birth_input.text().strip(),
            'club': self.club_input.text().strip(),
            'photo_path': self.photo_path
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
        
        if not self.club_input.text().strip():
            return False, "Клуб", "Поле 'Клуб' обязательно для заполнения!"
        
        return True, None, None
    
    def accept(self):
        """Переопределяем accept для валидации перед закрытием"""
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
        self.background_pixmap = None
        self.players_data = []  # Список игроков
        self.filtered_players = []  # Отфильтрованный список
        
        self.setWindowTitle("Игроки")
        self.setFixedSize(1000, 600)
        self.setModal(True)
        self.initUI()
        
    def initUI(self):
        # Основной стиль окна
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
        content_layout.setSpacing(15)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # Верхняя панель с кнопкой назад и заголовком
        top_layout = QHBoxLayout()
        top_layout.setSpacing(15)
        
        # Увеличенная кнопка назад
        self.back_button = QPushButton(" ⇦")
        self.back_button.setObjectName("backButton")
        self.back_button.setFixedSize(50, 50)
        back_font = QFont()
        back_font.setBold(True)
        back_font.setPointSize(30)
        self.back_button.setFont(back_font)
        self.back_button.clicked.connect(self.close)
        self.back_button.setStyleSheet("""
            QPushButton#backButton {
                background-color: #8f9e8f;
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 30px;
                font-weight: bold;
                padding: 0px;
                qproperty-alignment: AlignCenter;
            }
            QPushButton#backButton:hover {
                background-color: #748774;
            }
        """)
        top_layout.addWidget(self.back_button)
        
        # Заголовок
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
        top_layout.addWidget(title_label)
        
        # Правый отступ для центрирования заголовка
        right_spacer = QWidget()
        right_spacer.setFixedSize(50, 50)
        right_spacer.setStyleSheet("background-color: transparent;")
        top_layout.addWidget(right_spacer)
        
        content_layout.addLayout(top_layout)
        
        # Поисковая строка
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
        
        # Таблица игроков
        self.players_table = QTableWidget()
        self.players_table.setColumnCount(5)
        self.players_table.setHorizontalHeaderLabels([
            "Имя", "Фамилия", "Дата рождения", "Клуб", "Фото"
        ])
        
        # Настройка ширины колонок
        header = self.players_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        # Увеличиваем ширину колонки Фото, чтобы текст полностью помещался
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        header.resizeSection(4, 130)  # Устанавливаем фиксированную ширину 130 пикселей
        
        # Увеличиваем высоту строк
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
        
        # Нижняя панель
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(15)
        
        # Статистика
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
        
        # Кнопка добавления игрока (только для администратора)
        if self.is_admin:
            self.add_button = QPushButton("Добавить игрока")
            self.add_button.setObjectName("addButton")
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
        
        # Обновляем таблицу
        self.update_table()
    
    def paintEvent(self, event):
        """Рисование фона"""
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
        """Устанавливает фоновое изображение"""
        if pixmap and not pixmap.isNull():
            self.background_pixmap = pixmap
            
            # Делаем контентный фрейм полупрозрачным
            self.content_frame.setStyleSheet("""
                QFrame#contentFrame {
                    background-color: rgba(240, 245, 240, 200);
                    border: 2px solid rgba(155, 184, 155, 160);
                    border-radius: 10px;
                }
            """)
            
            # Делаем таблицу полупрозрачной
            self.players_table.setStyleSheet("""
                QTableWidget {
                    background-color: rgba(255, 255, 255, 220);
                    border: 2px solid rgba(155, 184, 155, 160);
                    border-radius: 5px;
                    color: #1e3a2e;
                    font-size: 12px;
                    gridline-color: rgba(208, 224, 208, 160);
                }
                QTableWidget::item:selected {
                    background-color: rgba(212, 232, 212, 200);
                }
                QHeaderView::section {
                    background-color: rgba(107, 143, 107, 200);
                }
                QScrollBar:vertical {
                    background-color: rgba(208, 224, 208, 140);
                }
                QScrollBar::handle:vertical {
                    background-color: rgba(107, 143, 107, 180);
                }
            """)
            
            # Делаем поисковую строку полупрозрачной
            self.search_input.setStyleSheet("""
                QLineEdit {
                    background-color: rgba(255, 255, 255, 220);
                    border: 2px solid rgba(155, 184, 155, 160);
                    border-radius: 5px;
                    padding: 10px 15px;
                    color: #1e3a2e;
                    font-size: 12px;
                }
                QLineEdit:focus {
                    border-color: rgba(77, 122, 77, 200);
                    background-color: rgba(248, 255, 248, 230);
                }
            """)
            
            # Делаем кнопку назад полупрозрачной
            self.back_button.setStyleSheet("""
                QPushButton#backButton {
                    background-color: rgba(143, 158, 143, 220);
                    color: white;
                    border: none;
                    border-radius: 25px;
                    font-size: 30px;
                    font-weight: bold;
                    padding: 0px;
                    qproperty-alignment: AlignCenter;
                }
                QPushButton#backButton:hover {
                    background-color: rgba(116, 135, 116, 240);
                }
            """)
            
            # Делаем статистику полупрозрачной
            self.stats_label.setStyleSheet("""
                QLabel {
                    color: #2c4c3b;
                    font-weight: bold;
                    font-size: 12px;
                    background-color: rgba(255, 255, 255, 220);
                    padding: 8px 15px;
                    border: 2px solid rgba(155, 184, 155, 160);
                    border-radius: 5px;
                }
            """)
            
            # Делаем кнопку добавления полупрозрачной
            if self.is_admin:
                self.add_button.setStyleSheet("""
                    QPushButton#addButton {
                        background-color: rgba(33, 150, 243, 220);
                        color: white;
                        border: none;
                        border-radius: 5px;
                        padding: 10px 20px;
                        font-weight: bold;
                        font-size: 12px;
                    }
                    QPushButton#addButton:hover {
                        background-color: rgba(25, 118, 210, 240);
                    }
                """)
            
            self.update()
    
    def resizeEvent(self, event):
        """Обновляет фон при изменении размера"""
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
                if (search_text in player['name'].lower() or
                    search_text in player['surname'].lower() or
                    search_text in player['club'].lower()):
                    self.filtered_players.append(player)
        
        self.update_table()
    
    def show_photo(self, photo_path, player_name):
        """Показывает фотографию игрока"""
        if photo_path:
            dialog = PhotoViewerDialog(photo_path, player_name, self)
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
        self.players_table.setColumnCount(5)
        
        for row, player in enumerate(self.filtered_players):
            # Имя
            name_item = QTableWidgetItem(player['name'])
            name_item.setTextAlignment(Qt.AlignCenter)
            self.players_table.setItem(row, 0, name_item)
            
            # Фамилия
            surname_item = QTableWidgetItem(player['surname'])
            surname_item.setTextAlignment(Qt.AlignCenter)
            self.players_table.setItem(row, 1, surname_item)
            
            # Дата рождения
            birth_item = QTableWidgetItem(player['birth_date'])
            birth_item.setTextAlignment(Qt.AlignCenter)
            self.players_table.setItem(row, 2, birth_item)
            
            # Клуб
            club_item = QTableWidgetItem(player['club'])
            club_item.setTextAlignment(Qt.AlignCenter)
            self.players_table.setItem(row, 3, club_item)
            
            # Кнопка для просмотра фото
            if player.get('has_photo', False):
                photo_button = PhotoButton(
                    player.get('photo_path', ''),
                    f"{player['name']} {player['surname']}",
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
        dialog = AddPlayerDialog(self.background_pixmap, self)
        
        if dialog.exec() == QDialog.Accepted:
            player_data = dialog.get_player_data()
            
            # Добавляем нового игрока в список
            new_player = {
                'name': player_data['name'],
                'surname': player_data['surname'],
                'birth_date': player_data['birth_date'],
                'club': player_data['club'],
                'has_photo': bool(player_data['photo_path']),
                'photo_path': player_data['photo_path'] if player_data['photo_path'] else None
            }
            
            self.players_data.append(new_player)
            self.filter_players()  # Обновляем отображение
            
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Успех")
            msg_box.setText(f"Игрок {player_data['name']} {player_data['surname']} успешно добавлен!")
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