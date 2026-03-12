# window_profile.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                               QLabel, QPushButton, QFileDialog,
                               QFrame, QMessageBox, QWidget)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QPalette, QBrush, QPainter, QPainterPath, QFont


class ProfileWindow(QDialog):
    avatar_updated = Signal(object)
    
    def __init__(self, user_data=None, db=None, parent=None):
        super().__init__(parent)
        self.user_data = user_data
        self.db = db
        self.background_path = None
        self.background_pixmap = None
        self.avatar_pixmap = None
        self.setWindowTitle("Профиль")
        self.setFixedSize(500, 500)
        self.setModal(True)
        self.initUI()
        self.load_user_data()
        
    def initUI(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #e8f0e8;
            }
            QFrame#contentFrame {
                background-color: #f0f5f0;
                border: 2px solid #9bb89b;
                border-radius: 10px;
            }
            QLabel {
                color: #2c4c3b;
                font-size: 12px;
            }
            QLabel#avatar {
                background-color: #ffffff;
                border: 3px solid #6b8f6b;
                border-radius: 40px;
                color: #2c4c3b;
                min-width: 80px;
                min-height: 80px;
                max-width: 80px;
                max-height: 80px;
            }
            QLabel#avatar:hover {
                background-color: #f0f8f0;
                border-color: #527352;
            }
            QLabel#titleLabel {
                color: #1e4a2e;
                font-size: 20px;
                font-weight: bold;
                padding: 8px 20px;
                background-color: rgba(150, 180, 150, 0.3);
                border-radius: 8px;
            }
            QLabel#achievementBox {
                background-color: #e8f0e8;
                border: 2px dashed #9bb89b;
                border-radius: 5px;
                padding: 10px;
                color: #8f9e8f;
                font-style: italic;
                font-size: 11px;
            }
            QPushButton#backButton {
                background-color: #8f9e8f;
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 28px;
                font-weight: bold;
                padding: 0px;
                min-width: 40px;
                min-height: 40px;
                max-width: 40px;
                max-height: 40px;
            }
            QPushButton#backButton:hover {
                background-color: #748774;
            }
            QPushButton#changeClubButton {
                background-color: #6b8f6b;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 15px;
                font-weight: bold;
                font-size: 11px;
                min-width: 140px;
            }
            QPushButton#changeClubButton:hover {
                background-color: #527352;
            }
            QPushButton#scheduleButton {
                background-color: #6b8f6b;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
                font-size: 14px;
                min-height: 35px;
            }
            QPushButton#scheduleButton:hover {
                background-color: #527352;
            }
            QFrame#infoFrame {
                background-color: #ffffff;
                border: 2px solid #9bb89b;
                border-radius: 8px;
            }
            QLabel#fieldLabel {
                font-weight: bold;
                min-width: 100px;
            }
            QLabel#valueLabel {
                color: #1e3a2e;
            }
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)
        
        self.back_button = QPushButton(" ⇦")
        self.back_button.setObjectName("backButton")
        font = QFont()
        font.setBold(True)
        font.setPointSize(28)
        self.back_button.setFont(font)
        self.back_button.clicked.connect(self.close)
        top_layout.addWidget(self.back_button)
        
        title_label = QLabel("Профиль")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        top_layout.addWidget(title_label)
        
        right_spacer = QWidget()
        right_spacer.setFixedSize(40, 40)
        right_spacer.setStyleSheet("background-color: transparent;")
        top_layout.addWidget(right_spacer)
        
        main_layout.addLayout(top_layout)
        
        self.content_frame = QFrame()
        self.content_frame.setObjectName("contentFrame")
        
        content_layout = QVBoxLayout(self.content_frame)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(25, 25, 25, 25)
        
        top_content_layout = QHBoxLayout()
        top_content_layout.setSpacing(20)
        
        left_widget = QWidget()
        left_widget.setFixedWidth(100)
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setAlignment(Qt.AlignTop)
        
        self.avatar_label = QLabel()
        self.avatar_label.setObjectName("avatar")
        self.avatar_label.setFixedSize(80, 80)
        self.avatar_label.setAlignment(Qt.AlignCenter)
        self.avatar_label.setCursor(Qt.PointingHandCursor)
        self.avatar_label.setText("👤")
        self.avatar_label.mousePressEvent = self.load_avatar
        
        left_layout.addWidget(self.avatar_label)
        top_content_layout.addWidget(left_widget)
        
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(5)
        
        self.achievements_box = QLabel("Здесь будут отображаться достижения")
        self.achievements_box.setObjectName("achievementBox")
        self.achievements_box.setWordWrap(True)
        self.achievements_box.setFixedHeight(60)
        right_layout.addWidget(self.achievements_box)
        
        top_content_layout.addWidget(right_widget)
        content_layout.addLayout(top_content_layout)
        
        info_frame = QFrame()
        info_frame.setObjectName("infoFrame")
        
        info_layout = QVBoxLayout(info_frame)
        info_layout.setSpacing(15)
        info_layout.setContentsMargins(20, 20, 20, 20)
        info_layout.setAlignment(Qt.AlignLeft)
        
        login_layout = QHBoxLayout()
        login_layout.setSpacing(5)
        login_layout.setAlignment(Qt.AlignLeft)
        
        login_label = QLabel("Логин:")
        login_label.setObjectName("fieldLabel")
        login_layout.addWidget(login_label)
        
        self.login_value = QLabel()
        self.login_value.setObjectName("valueLabel")
        login_layout.addWidget(self.login_value)
        login_layout.addStretch()
        info_layout.addLayout(login_layout)
        
        club_layout = QHBoxLayout()
        club_layout.setSpacing(5)
        club_layout.setAlignment(Qt.AlignLeft)
        
        club_label = QLabel("Любимый клуб:")
        club_label.setObjectName("fieldLabel")
        club_layout.addWidget(club_label)
        
        self.club_value = QLabel()
        self.club_value.setObjectName("valueLabel")
        club_layout.addWidget(self.club_value)
        club_layout.addStretch()
        info_layout.addLayout(club_layout)
        
        change_club_layout = QHBoxLayout()
        change_club_layout.setAlignment(Qt.AlignLeft)
        change_club_layout.setContentsMargins(0, 0, 0, 0)
        
        self.change_club_button = QPushButton("Сменить любимый клуб")
        self.change_club_button.setObjectName("changeClubButton")
        self.change_club_button.clicked.connect(self.change_club)
        change_club_layout.addWidget(self.change_club_button)
        info_layout.addLayout(change_club_layout)
        
        reg_date_layout = QHBoxLayout()
        reg_date_layout.setSpacing(5)
        reg_date_layout.setAlignment(Qt.AlignLeft)
        
        reg_date_label = QLabel("Дата регистрации:")
        reg_date_label.setObjectName("fieldLabel")
        reg_date_layout.addWidget(reg_date_label)
        
        self.reg_date_value = QLabel()
        self.reg_date_value.setObjectName("valueLabel")
        reg_date_layout.addWidget(self.reg_date_value)
        reg_date_layout.addStretch()
        info_layout.addLayout(reg_date_layout)
        
        content_layout.addWidget(info_frame)
        
        self.schedule_button = QPushButton("Просмотр графика матчей")
        self.schedule_button.setObjectName("scheduleButton")
        self.schedule_button.clicked.connect(self.show_schedule_stub)
        content_layout.addWidget(self.schedule_button)
        
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
    
    def set_avatar(self, avatar_pixmap):
        """Устанавливает аватар из главного окна"""
        self.avatar_pixmap = avatar_pixmap
        self.avatar_label.setPixmap(self.avatar_pixmap)
        self.avatar_label.setText("")
    
    def load_user_data(self):
        if self.user_data and self.db:
            if self.db and hasattr(self.db, 'conn'):
                try:
                    with self.db.conn.cursor() as cur:
                        cur.execute("SELECT username FROM credentials WHERE id = %s", (self.user_data.get('id'),))
                        result = cur.fetchone()
                        if result:
                            self.login_value.setText(result[0])
                except Exception as e:
                    print(f"Ошибка получения логина: {e}")
                    self.login_value.setText("Ошибка загрузки")
            
            self.club_value.setText(self.user_data.get('favorite_club', 'Не указан'))
            
            if self.db and hasattr(self.db, 'conn'):
                try:
                    with self.db.conn.cursor() as cur:
                        cur.execute("SELECT created_at FROM user_profiles WHERE id = %s", (self.user_data.get('id'),))
                        result = cur.fetchone()
                        if result and result[0]:
                            self.reg_date_value.setText(result[0].strftime("%d.%m.%Y"))
                        else:
                            self.reg_date_value.setText("Не указана")
                except Exception as e:
                    print(f"Ошибка получения даты регистрации: {e}")
                    self.reg_date_value.setText("Ошибка загрузки")
    
    def set_background(self, image_path):
        """Устанавливает фоновое изображение по пути к файлу"""
        try:
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                self.background_pixmap = pixmap
                self.background_path = image_path
                
                # Делаем контентный фрейм полупрозрачным
                self.content_frame.setStyleSheet("""
                    QFrame#contentFrame {
                        background-color: rgba(240, 245, 240, 200);
                        border: 2px solid rgba(155, 184, 155, 160);
                        border-radius: 10px;
                    }
                """)
                
                # Делаем информационный фрейм полупрозрачным
                for child in self.content_frame.findChildren(QFrame):
                    if child.objectName() == "infoFrame":
                        child.setStyleSheet("""
                            QFrame#infoFrame {
                                background-color: rgba(255, 255, 255, 220);
                                border: 2px solid rgba(155, 184, 155, 160);
                                border-radius: 8px;
                            }
                        """)
                
                # Делаем кнопки полупрозрачными
                self.back_button.setStyleSheet("""
                    QPushButton#backButton {
                        background-color: rgba(143, 158, 143, 220);
                        color: white;
                        border: none;
                        border-radius: 20px;
                        font-size: 28px;
                        font-weight: bold;
                        padding: 0px;
                        min-width: 40px;
                        min-height: 40px;
                        max-width: 40px;
                        max-height: 40px;
                    }
                    QPushButton#backButton:hover {
                        background-color: rgba(116, 135, 116, 240);
                    }
                """)
                
                self.change_club_button.setStyleSheet("""
                    QPushButton#changeClubButton {
                        background-color: rgba(107, 143, 107, 220);
                        color: white;
                        border: none;
                        border-radius: 3px;
                        padding: 5px 15px;
                        font-weight: bold;
                        font-size: 11px;
                        min-width: 140px;
                    }
                    QPushButton#changeClubButton:hover {
                        background-color: rgba(82, 115, 82, 240);
                    }
                """)
                
                self.schedule_button.setStyleSheet("""
                    QPushButton#scheduleButton {
                        background-color: rgba(107, 143, 107, 220);
                        color: white;
                        border: none;
                        border-radius: 5px;
                        padding: 10px;
                        font-weight: bold;
                        font-size: 14px;
                        min-height: 35px;
                    }
                    QPushButton#scheduleButton:hover {
                        background-color: rgba(82, 115, 82, 240);
                    }
                """)
                
                # Делаем achievement box полупрозрачным
                self.achievements_box.setStyleSheet("""
                    QLabel#achievementBox {
                        background-color: rgba(232, 240, 232, 200);
                        border: 2px dashed rgba(155, 184, 155, 160);
                        border-radius: 5px;
                        padding: 10px;
                        color: #8f9e8f;
                        font-style: italic;
                        font-size: 11px;
                    }
                """)
                
                self.update()  # Перерисовываем окно
        except Exception as e:
            print(f"Ошибка установки фона: {e}")
    
    def set_background_pixmap(self, pixmap):
        """Устанавливает фоновое изображение из QPixmap"""
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
            
            # Делаем информационный фрейм полупрозрачным
            for child in self.content_frame.findChildren(QFrame):
                if child.objectName() == "infoFrame":
                    child.setStyleSheet("""
                        QFrame#infoFrame {
                            background-color: rgba(255, 255, 255, 220);
                            border: 2px solid rgba(155, 184, 155, 160);
                            border-radius: 8px;
                        }
                    """)
            
            # Делаем кнопки полупрозрачными
            self.back_button.setStyleSheet("""
                QPushButton#backButton {
                    background-color: rgba(143, 158, 143, 220);
                    color: white;
                    border: none;
                    border-radius: 20px;
                    font-size: 28px;
                    font-weight: bold;
                    padding: 0px;
                    min-width: 40px;
                    min-height: 40px;
                    max-width: 40px;
                    max-height: 40px;
                }
                QPushButton#backButton:hover {
                    background-color: rgba(116, 135, 116, 240);
                }
            """)
            
            self.change_club_button.setStyleSheet("""
                QPushButton#changeClubButton {
                    background-color: rgba(107, 143, 107, 220);
                    color: white;
                    border: none;
                    border-radius: 3px;
                    padding: 5px 15px;
                    font-weight: bold;
                    font-size: 11px;
                    min-width: 140px;
                }
                QPushButton#changeClubButton:hover {
                    background-color: rgba(82, 115, 82, 240);
                }
            """)
            
            self.schedule_button.setStyleSheet("""
                QPushButton#scheduleButton {
                    background-color: rgba(107, 143, 107, 220);
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 10px;
                    font-weight: bold;
                    font-size: 14px;
                    min-height: 35px;
                }
                QPushButton#scheduleButton:hover {
                    background-color: rgba(82, 115, 82, 240);
                }
            """)
            
            # Делаем achievement box полупрозрачным
            self.achievements_box.setStyleSheet("""
                QLabel#achievementBox {
                    background-color: rgba(232, 240, 232, 200);
                    border: 2px dashed rgba(155, 184, 155, 160);
                    border-radius: 5px;
                    padding: 10px;
                    color: #8f9e8f;
                    font-style: italic;
                    font-size: 11px;
                }
            """)
            
            self.update()  # Перерисовываем окно
    
    def resizeEvent(self, event):
        """Обновляет фон при изменении размера окна"""
        if self.background_pixmap and not self.background_pixmap.isNull():
            self.update()
        super().resizeEvent(event)
    
    def load_avatar(self, event):
        file, _ = QFileDialog.getOpenFileName(
            self, 
            "Выберите изображение для аватара", 
            "", 
            "Изображения (*.png *.jpg *.jpeg *.bmp)"
        )
        if file:
            pixmap = QPixmap(file)
            if not pixmap.isNull():
                self.avatar_pixmap = self.create_circular_avatar(pixmap)
                self.avatar_label.setPixmap(self.avatar_pixmap)
                self.avatar_label.setText("")
                self.avatar_updated.emit(self.avatar_pixmap)
    
    def create_circular_avatar(self, pixmap):
        size = min(pixmap.width(), pixmap.height())
        x_offset = (pixmap.width() - size) // 2
        y_offset = (pixmap.height() - size) // 2
        cropped = pixmap.copy(x_offset, y_offset, size, size)
        scaled = cropped.scaled(80, 80, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        
        circular_pixmap = QPixmap(80, 80)
        circular_pixmap.fill(Qt.transparent)
        
        painter = QPainter(circular_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addEllipse(0, 0, 80, 80)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, scaled)
        painter.end()
        
        return circular_pixmap
    
    def change_club(self):
        QMessageBox.information(self, "Смена клуба", "Функция смены любимого клуба будет доступна позже")
    
    def show_schedule_stub(self):
        QMessageBox.information(self, "График матчей", "Просмотр графика матчей будет доступен позже")