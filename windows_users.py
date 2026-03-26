# window_users.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                               QLabel, QPushButton, QFrame, QTableWidget,
                               QTableWidgetItem, QHeaderView, QMessageBox,
                               QWidget)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QPalette, QBrush, QFont, QPainter


class UsersWindow(QDialog):
    def __init__(self, db=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.background_path = None
        self.background_pixmap = None
        self.setWindowTitle("Список пользователей")
        self.setFixedSize(1100, 650)
        self.setModal(True)
        self.initUI()
        self.load_users()
        
    def initUI(self):
        # Основной стиль окна (светлая тема по умолчанию)
        self.setStyleSheet("""
            QDialog {
                background-color: #e8f0e8;
            }
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        
        self.content_frame = QFrame()
        self.content_frame.setObjectName("contentFrame")
        self.content_frame.setStyleSheet("""
            QFrame#contentFrame {
                background-color: #e8f0e8;
                border-radius: 10px;
            }
        """)
        
        content_layout = QVBoxLayout(self.content_frame)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(25, 25, 25, 25)
        
        # Заголовок
        title_label = QLabel("Управление пользователями")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setMinimumHeight(55)
        title_label.setStyleSheet("""
            QLabel#titleLabel {
                color: #1e4a2e;
                font-size: 24px;
                font-weight: bold;
                padding: 12px 20px;
                background-color: rgba(150, 180, 150, 0.3);
                border-radius: 8px;
            }
        """)
        content_layout.addWidget(title_label)
        
        # Таблица пользователей
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(5)
        self.users_table.setHorizontalHeaderLabels(["Имя", "Фамилия", "Логин", "Статус", "Действия"])
        
        # Настройка ширины колонок
        header = self.users_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.resizeSection(3, 120)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        header.resizeSection(4, 360)
        
        # Скрываем вертикальный заголовок
        self.users_table.verticalHeader().setVisible(False)
        
        # Устанавливаем фиксированную высоту строк
        self.users_table.verticalHeader().setDefaultSectionSize(70)
        self.users_table.verticalHeader().setMinimumSectionSize(70)
        
        self.users_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.users_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.users_table.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                border: 2px solid #9bb89b;
                border-radius: 8px;
                color: #1e3a2e;
                font-size: 13px;
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
                padding: 12px;
                border: none;
                font-size: 13px;
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
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #6b8f6b;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #527352;
            }
        """)
        
        content_layout.addWidget(self.users_table)
        
        # Нижняя панель с кнопкой назад и статистикой
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(20)
        
        # Кнопка назад
        self.back_button = QPushButton("← Назад")
        self.back_button.setObjectName("backButton")
        self.back_button.setFixedWidth(140)
        self.back_button.setFixedHeight(45)
        self.back_button.setStyleSheet("""
            QPushButton#backButton {
                background-color: #8f9e8f;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton#backButton:hover {
                background-color: #748774;
            }
        """)
        self.back_button.clicked.connect(self.close)
        bottom_layout.addWidget(self.back_button)
        
        bottom_layout.addStretch()
        
        # Статистика
        self.total_users_label = QLabel("Всего пользователей: 0")
        self.total_users_label.setFixedHeight(45)
        self.total_users_label.setStyleSheet("""
            QLabel {
                color: #2c4c3b;
                font-weight: bold;
                font-size: 14px;
                background-color: rgba(255, 255, 255, 0.9);
                padding: 10px 20px;
                border: 2px solid #9bb89b;
                border-radius: 6px;
            }
        """)
        bottom_layout.addWidget(self.total_users_label)
        
        bottom_layout.addStretch()
        
        # Правый отступ для симметрии
        right_spacer = QWidget()
        right_spacer.setFixedWidth(140)
        right_spacer.setStyleSheet("background-color: transparent;")
        bottom_layout.addWidget(right_spacer)
        
        content_layout.addLayout(bottom_layout)
        
        main_layout.addWidget(self.content_frame)
        
        self.setAutoFillBackground(True)
    
    def paintEvent(self, event):
        """Переопределяем paintEvent для рисования фона"""
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
    
    def set_background(self, image_path):
        """Устанавливает фоновое изображение по пути к файлу"""
        try:
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                self.background_pixmap = pixmap
                self.background_path = image_path
                
                self.content_frame.setStyleSheet("""
                    QFrame#contentFrame {
                        background-color: rgba(232, 240, 232, 180);
                        border-radius: 10px;
                    }
                """)
                
                self.users_table.setStyleSheet("""
                    QTableWidget {
                        background-color: rgba(255, 255, 255, 220);
                        border: 2px solid rgba(155, 184, 155, 160);
                        border-radius: 8px;
                        color: #1e3a2e;
                        font-size: 13px;
                        gridline-color: rgba(208, 224, 208, 160);
                    }
                    QTableWidget::item:selected {
                        background-color: rgba(212, 232, 212, 200);
                        color: #1e3a2e;
                    }
                    QHeaderView::section {
                        background-color: rgba(107, 143, 107, 200);
                        color: white;
                        font-weight: bold;
                        padding: 12px;
                        border: none;
                        font-size: 13px;
                    }
                    QScrollBar:vertical {
                        border: none;
                        background-color: rgba(208, 224, 208, 140);
                        width: 12px;
                        border-radius: 6px;
                    }
                    QScrollBar::handle:vertical {
                        background-color: rgba(107, 143, 107, 180);
                        border-radius: 6px;
                        min-height: 20px;
                    }
                """)
                
                self.back_button.setStyleSheet("""
                    QPushButton#backButton {
                        background-color: rgba(143, 158, 143, 220);
                        color: white;
                        border: none;
                        border-radius: 6px;
                        padding: 10px 20px;
                        font-weight: bold;
                        font-size: 14px;
                    }
                    QPushButton#backButton:hover {
                        background-color: rgba(116, 135, 116, 240);
                    }
                """)
                
                self.total_users_label.setStyleSheet("""
                    QLabel {
                        color: #2c4c3b;
                        font-weight: bold;
                        font-size: 14px;
                        background-color: rgba(255, 255, 255, 220);
                        padding: 10px 20px;
                        border: 2px solid rgba(155, 184, 155, 160);
                        border-radius: 6px;
                    }
                """)
                
                self.update()
        except Exception as e:
            print(f"Ошибка установки фона: {e}")
    
    def set_background_pixmap(self, pixmap):
        """Устанавливает фоновое изображение из QPixmap"""
        if pixmap and not pixmap.isNull():
            self.background_pixmap = pixmap
            
            self.content_frame.setStyleSheet("""
                QFrame#contentFrame {
                    background-color: rgba(232, 240, 232, 180);
                    border-radius: 10px;
                }
            """)
            
            self.users_table.setStyleSheet("""
                QTableWidget {
                    background-color: rgba(255, 255, 255, 220);
                    border: 2px solid rgba(155, 184, 155, 160);
                    border-radius: 8px;
                    color: #1e3a2e;
                    font-size: 13px;
                    gridline-color: rgba(208, 224, 208, 160);
                }
                QTableWidget::item:selected {
                    background-color: rgba(212, 232, 212, 200);
                    color: #1e3a2e;
                }
                QHeaderView::section {
                    background-color: rgba(107, 143, 107, 200);
                    color: white;
                    font-weight: bold;
                    padding: 12px;
                    border: none;
                    font-size: 13px;
                }
                QScrollBar:vertical {
                    border: none;
                    background-color: rgba(208, 224, 208, 140);
                    width: 12px;
                    border-radius: 6px;
                }
                QScrollBar::handle:vertical {
                    background-color: rgba(107, 143, 107, 180);
                    border-radius: 6px;
                    min-height: 20px;
                }
            """)
            
            self.back_button.setStyleSheet("""
                QPushButton#backButton {
                    background-color: rgba(143, 158, 143, 220);
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton#backButton:hover {
                    background-color: rgba(116, 135, 116, 240);
                }
            """)
            
            self.total_users_label.setStyleSheet("""
                QLabel {
                    color: #2c4c3b;
                    font-weight: bold;
                    font-size: 14px;
                    background-color: rgba(255, 255, 255, 220);
                    padding: 10px 20px;
                    border: 2px solid rgba(155, 184, 155, 160);
                    border-radius: 6px;
                }
            """)
            
            self.update()
    
    def resizeEvent(self, event):
        """Обновляет фон при изменении размера окна"""
        if self.background_pixmap and not self.background_pixmap.isNull():
            self.update()
        super().resizeEvent(event)
    
    def load_users(self):
        """Загружает список пользователей из базы данных"""
        try:
            if not self.db:
                return
            
            users = self.db.get_all_users()
            
            self.users_table.setRowCount(len(users))
            
            for row, user in enumerate(users):
                user_id = user['id']
                username = user['username']
                first_name = user['first_name']
                last_name = user['last_name']
                is_blocked = user['is_blocked']
                
                # Имя
                name_item = QTableWidgetItem(first_name)
                name_item.setData(Qt.UserRole, user_id)
                name_item.setTextAlignment(Qt.AlignCenter)
                self.users_table.setItem(row, 0, name_item)
                
                # Фамилия
                surname_item = QTableWidgetItem(last_name)
                surname_item.setTextAlignment(Qt.AlignCenter)
                self.users_table.setItem(row, 1, surname_item)
                
                # Логин
                login_item = QTableWidgetItem(username)
                login_item.setTextAlignment(Qt.AlignCenter)
                self.users_table.setItem(row, 2, login_item)
                
                # Статус
                status_text = "Заблокирован" if is_blocked else "Активен"
                status_color = "#d46b6b" if is_blocked else "#6b8f6b"
                
                # Устанавливаем цвет для ячейки статуса
                status_widget = QLabel(status_text)
                status_widget.setAlignment(Qt.AlignCenter)
                status_widget.setStyleSheet(f"""
                    QLabel {{
                        background-color: {status_color};
                        color: white;
                        border-radius: 4px;
                        padding: 6px;
                        font-weight: bold;
                        font-size: 12px;
                    }}
                """)
                self.users_table.setCellWidget(row, 3, status_widget)
                
                # Кнопки действий
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(10, 12, 10, 12)
                actions_layout.setSpacing(20)
                
                if is_blocked:
                    # Показываем только кнопку разблокировки
                    unblock_btn = QPushButton("Разблокировать")
                    unblock_btn.setObjectName("unblockButton")
                    unblock_btn.setFixedSize(150, 40)
                    unblock_btn.setStyleSheet("""
                        QPushButton#unblockButton {
                            background-color: #6b8f6b;
                            color: white;
                            border: none;
                            border-radius: 6px;
                            font-size: 13px;
                            font-weight: bold;
                        }
                        QPushButton#unblockButton:hover {
                            background-color: #527352;
                        }
                        QPushButton#unblockButton:pressed {
                            background-color: #3e5a3e;
                        }
                    """)
                    unblock_btn.clicked.connect(lambda checked, uid=user_id, name=first_name: self.unblock_user(uid, name))
                    actions_layout.addWidget(unblock_btn)
                else:
                    # Показываем только кнопку блокировки
                    block_btn = QPushButton("Заблокировать")
                    block_btn.setObjectName("blockButton")
                    block_btn.setFixedSize(150, 40)
                    block_btn.setStyleSheet("""
                        QPushButton#blockButton {
                            background-color: #d46b6b;
                            color: white;
                            border: none;
                            border-radius: 6px;
                            font-size: 13px;
                            font-weight: bold;
                        }
                        QPushButton#blockButton:hover {
                            background-color: #b85a5a;
                        }
                        QPushButton#blockButton:pressed {
                            background-color: #9e4a4a;
                        }
                    """)
                    block_btn.clicked.connect(lambda checked, uid=user_id, name=first_name: self.block_user(uid, name))
                    actions_layout.addWidget(block_btn)
                
                actions_layout.setAlignment(Qt.AlignCenter)
                self.users_table.setCellWidget(row, 4, actions_widget)
            
            self.total_users_label.setText(f"Всего пользователей: {len(users)}")
            
        except Exception as e:
            print(f"Ошибка загрузки пользователей: {e}")
            self.users_table.setRowCount(1)
            error_item = QTableWidgetItem("Ошибка загрузки данных")
            error_item.setTextAlignment(Qt.AlignCenter)
            self.users_table.setItem(0, 0, error_item)
    
    def block_user(self, user_id, user_name):
        """Блокирует пользователя"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Подтверждение блокировки")
        msg_box.setText(f"Вы уверены, что хотите заблокировать пользователя {user_name}?\n\nПосле блокировки пользователь не сможет войти в систему.")
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #e8f0e8;
            }
            QMessageBox QLabel {
                color: #2c4c3b;
                font-weight: bold;
                font-size: 12px;
                min-width: 300px;
                padding: 15px;
                color: #000000;
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
        
        # Создаем кнопки с русскими названиями
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
            success, message = self.db.block_user(user_id)
            
            if success:
                msg_success = QMessageBox(self)
                msg_success.setWindowTitle("Успешно")
                msg_success.setText(f"Пользователь {user_name} успешно заблокирован.")
                msg_success.setIcon(QMessageBox.Information)
                msg_success.setStyleSheet("""
                    QMessageBox {
                        background-color: #e8f0e8;
                    }
                    QMessageBox QLabel {
                        color: #2c4c3b;
                        font-weight: bold;
                        font-size: 12px;
                        min-width: 250px;
                        padding: 15px;
                        color: #000000;
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
                ok_button = msg_success.addButton("ОК", QMessageBox.AcceptRole)
                msg_success.exec()
                self.load_users()
            else:
                msg_error = QMessageBox(self)
                msg_error.setWindowTitle("Ошибка")
                msg_error.setText(f"Не удалось заблокировать пользователя: {message}")
                msg_error.setIcon(QMessageBox.Critical)
                msg_error.setStyleSheet("""
                    QMessageBox {
                        background-color: #e8f0e8;
                    }
                    QMessageBox QLabel {
                        color: #2c4c3b;
                        font-weight: bold;
                        font-size: 12px;
                        min-width: 250px;
                        padding: 15px;
                        color: #000000;
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
                ok_button = msg_error.addButton("ОК", QMessageBox.AcceptRole)
                msg_error.exec()
    
    def unblock_user(self, user_id, user_name):
        """Разблокирует пользователя"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Подтверждение разблокировки")
        msg_box.setText(f"Вы уверены, что хотите разблокировать пользователя {user_name}?\n\nПосле разблокировки пользователь сможет войти в систему.")
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #e8f0e8;
            }
            QMessageBox QLabel {
                color: #2c4c3b;
                font-weight: bold;
                font-size: 12px;
                min-width: 300px;
                padding: 15px;
                color: #000000;
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
        
        # Создаем кнопки с русскими названиями
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
            success, message = self.db.unblock_user(user_id)
            
            if success:
                msg_success = QMessageBox(self)
                msg_success.setWindowTitle("Успешно")
                msg_success.setText(f"Пользователь {user_name} успешно разблокирован.")
                msg_success.setIcon(QMessageBox.Information)
                msg_success.setStyleSheet("""
                    QMessageBox {
                        background-color: #e8f0e8;
                    }
                    QMessageBox QLabel {
                        color: #2c4c3b;
                        font-weight: bold;
                        font-size: 12px;
                        min-width: 250px;
                        padding: 15px;
                        color: #000000;
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
                ok_button = msg_success.addButton("ОК", QMessageBox.AcceptRole)
                msg_success.exec()
                self.load_users()
            else:
                msg_error = QMessageBox(self)
                msg_error.setWindowTitle("Ошибка")
                msg_error.setText(f"Не удалось разблокировать пользователя: {message}")
                msg_error.setIcon(QMessageBox.Critical)
                msg_error.setStyleSheet("""
                    QMessageBox {
                        background-color: #e8f0e8;
                    }
                    QMessageBox QLabel {
                        color: #2c4c3b;
                        font-weight: bold;
                        font-size: 12px;
                        min-width: 250px;
                        padding: 15px;
                        color: #000000;
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
                ok_button = msg_error.addButton("ОК", QMessageBox.AcceptRole)
                msg_error.exec()