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
        self.setFixedSize(700, 500)
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
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # Верхняя панель с заголовком и кнопкой назад
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
        
        title_label = QLabel("Список пользователей")
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
        
        right_spacer = QWidget()
        right_spacer.setFixedSize(50, 50)
        right_spacer.setStyleSheet("background-color: transparent;")
        top_layout.addWidget(right_spacer)
        
        content_layout.addLayout(top_layout)
        
        # Таблица пользователей
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(4)
        self.users_table.setHorizontalHeaderLabels(["Имя", "Фамилия", "Логин", "Действия"])
        self.users_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.users_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.users_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.users_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.users_table.verticalHeader().setVisible(False)
        self.users_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.users_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.users_table.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                border: 2px solid #9bb89b;
                border-radius: 5px;
                color: #1e3a2e;
                font-size: 12px;
                gridline-color: #d0e0d0;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #d4e8d4;
                color: #1e3a2e;
            }
            QHeaderView::section {
                background-color: #6b8f6b;
                color: white;
                font-weight: bold;
                padding: 8px;
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
        
        content_layout.addWidget(self.users_table)
        
        # Статистика
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        self.total_users_label = QLabel("Всего пользователей: 0")
        self.total_users_label.setStyleSheet("""
            QLabel {
                color: #2c4c3b;
                font-weight: bold;
                font-size: 12px;
                background-color: rgba(255, 255, 255, 0.9);
                padding: 8px 15px;
                border: 2px solid #9bb89b;
                border-radius: 5px;
            }
        """)
        stats_layout.addWidget(self.total_users_label)
        
        stats_layout.addStretch()
        
        content_layout.addLayout(stats_layout)
        
        main_layout.addWidget(self.content_frame)
        
        self.setAutoFillBackground(True)
    
    def paintEvent(self, event):
        """Переопределяем paintEvent для рисования фона"""
        if self.background_pixmap and not self.background_pixmap.isNull():
            painter = QPainter(self)
            # Масштабируем изображение под размер окна
            scaled_pixmap = self.background_pixmap.scaled(
                self.size(),
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )
            # Центрируем изображение
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
                
                # Делаем фрейм полупрозрачным
                self.content_frame.setStyleSheet("""
                    QFrame#contentFrame {
                        background-color: rgba(232, 240, 232, 180);
                        border-radius: 10px;
                    }
                """)
                
                # Делаем таблицу полупрозрачной
                self.users_table.setStyleSheet("""
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
                        color: #1e3a2e;
                    }
                    QHeaderView::section {
                        background-color: rgba(107, 143, 107, 200);
                        color: white;
                        font-weight: bold;
                        padding: 8px;
                        border: none;
                        font-size: 12px;
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
                self.total_users_label.setStyleSheet("""
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
                
                self.update()  # Перерисовываем окно
        except Exception as e:
            print(f"Ошибка установки фона: {e}")
    
    def set_background_pixmap(self, pixmap):
        """Устанавливает фоновое изображение из QPixmap"""
        if pixmap and not pixmap.isNull():
            self.background_pixmap = pixmap
            
            # Делаем фрейм полупрозрачным
            self.content_frame.setStyleSheet("""
                QFrame#contentFrame {
                    background-color: rgba(232, 240, 232, 180);
                    border-radius: 10px;
                }
            """)
            
            # Делаем таблицу полупрозрачной
            self.users_table.setStyleSheet("""
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
                    color: #1e3a2e;
                }
                QHeaderView::section {
                    background-color: rgba(107, 143, 107, 200);
                    color: white;
                    font-weight: bold;
                    padding: 8px;
                    border: none;
                    font-size: 12px;
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
            self.total_users_label.setStyleSheet("""
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
            
            self.update()  # Перерисовываем окно
    
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
            
            with self.db.conn.cursor() as cur:
                # Получаем всех пользователей с их данными
                cur.execute("""
                    SELECT c.id, c.username, p.first_name, p.last_name
                    FROM credentials c
                    JOIN user_profiles p ON c.id = p.id
                    ORDER BY p.last_name, p.first_name
                """)
                users = cur.fetchall()
                
                self.users_table.setRowCount(len(users))
                
                for row, user in enumerate(users):
                    user_id, username, first_name, last_name = user
                    
                    # Имя
                    name_item = QTableWidgetItem(first_name)
                    name_item.setData(Qt.UserRole, user_id)
                    self.users_table.setItem(row, 0, name_item)
                    
                    # Фамилия
                    self.users_table.setItem(row, 1, QTableWidgetItem(last_name))
                    
                    # Логин
                    self.users_table.setItem(row, 2, QTableWidgetItem(username))
                    
                    # Кнопки действий
                    actions_widget = QWidget()
                    actions_layout = QHBoxLayout(actions_widget)
                    actions_layout.setContentsMargins(5, 2, 5, 2)
                    actions_layout.setSpacing(5)
                    
                    block_btn = QPushButton("Заблокировать")
                    block_btn.setObjectName("blockButton")
                    block_btn.setFixedSize(100, 25)
                    block_btn.setStyleSheet("""
                        QPushButton#blockButton {
                            background-color: #d46b6b;
                            color: white;
                            border: none;
                            border-radius: 3px;
                            font-size: 11px;
                            font-weight: bold;
                            padding: 5px;
                        }
                        QPushButton#blockButton:hover {
                            background-color: #b85a5a;
                        }
                        QPushButton#blockButton:pressed {
                            background-color: #9e4a4a;
                        }
                    """)
                    block_btn.clicked.connect(lambda checked, uid=user_id, name=first_name: self.block_user(uid, name))
                    
                    unblock_btn = QPushButton("Разблокировать")
                    unblock_btn.setObjectName("unblockButton")
                    unblock_btn.setFixedSize(100, 25)
                    unblock_btn.setStyleSheet("""
                        QPushButton#unblockButton {
                            background-color: #6b8f6b;
                            color: white;
                            border: none;
                            border-radius: 3px;
                            font-size: 11px;
                            font-weight: bold;
                            padding: 5px;
                        }
                        QPushButton#unblockButton:hover {
                            background-color: #527352;
                        }
                        QPushButton#unblockButton:pressed {
                            background-color: #3e5a3e;
                        }
                    """)
                    unblock_btn.clicked.connect(lambda checked, uid=user_id, name=first_name: self.unblock_user(uid, name))
                    
                    actions_layout.addWidget(block_btn)
                    actions_layout.addWidget(unblock_btn)
                    actions_layout.setAlignment(Qt.AlignCenter)
                    
                    self.users_table.setCellWidget(row, 3, actions_widget)
                
                self.total_users_label.setText(f"Всего пользователей: {len(users)}")
                
        except Exception as e:
            print(f"Ошибка загрузки пользователей: {e}")
            self.users_table.setRowCount(1)
            self.users_table.setItem(0, 0, QTableWidgetItem("Ошибка загрузки данных"))
    
    def block_user(self, user_id, user_name):
        """Блокирует пользователя"""
        reply = QMessageBox.question(
            self, 
            "Подтверждение блокировки",
            f"Вы уверены, что хотите заблокировать пользователя {user_name}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            QMessageBox.information(
                self,
                "Блокировка пользователя",
                f"Пользователь {user_name} заблокирован.\n(Функция в разработке)"
            )
    
    def unblock_user(self, user_id, user_name):
        """Разблокирует пользователя"""
        reply = QMessageBox.question(
            self, 
            "Подтверждение разблокировки",
            f"Вы уверены, что хотите разблокировать пользователя {user_name}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            QMessageBox.information(
                self,
                "Разблокировка пользователя",
                f"Пользователь {user_name} разблокирован.\n(Функция в разработке)"
            )