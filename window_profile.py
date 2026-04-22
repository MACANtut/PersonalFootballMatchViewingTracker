# window_profile.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                               QLabel, QPushButton, QFileDialog,
                               QFrame, QMessageBox, QWidget, QComboBox,
                               QScrollArea, QGridLayout)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QPainter, QPainterPath, QFont
import os


class AchievementWidget(QFrame):
    def __init__(self, achievement_data, parent=None):
        super().__init__(parent)
        self.achievement = achievement_data
        self.initUI()

    def initUI(self):
        self.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 2px solid #9bb89b;
                border-radius: 10px;
                margin: 5px;
            }
            QLabel {
                color: #2c4c3b;
            }
            QLabel#nameLabel {
                font-weight: bold;
                font-size: 12px;
                color: #1e4a2e;
            }
            QLabel#descLabel {
                font-size: 10px;
                color: #6b8f6b;
                font-style: italic;
            }
            QLabel#dateLabel {
                font-size: 9px;
                color: #8f9e8f;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(12)

        self.image_label = QLabel()
        self.image_label.setFixedSize(50, 50)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #f0f5f0;
                border: 1px solid #9bb89b;
                border-radius: 8px;
            }
        """)
        self.load_achievement_image()
        layout.addWidget(self.image_label)

        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(3)

        name_label = QLabel(self.achievement['name'])
        name_label.setObjectName("nameLabel")
        info_layout.addWidget(name_label)

        desc_label = QLabel(self.achievement['description'])
        desc_label.setObjectName("descLabel")
        info_layout.addWidget(desc_label)

        if self.achievement.get('earned_at'):
            date_str = self.achievement['earned_at'].strftime("%d.%m.%Y") if hasattr(self.achievement['earned_at'], 'strftime') else str(self.achievement['earned_at'])
            date_label = QLabel(f"Получено: {date_str}")
            date_label.setObjectName("dateLabel")
            info_layout.addWidget(date_label)

        layout.addWidget(info_widget, 1)

    def load_achievement_image(self):
        """Загрузка изображения достижения"""
        image_path = self.achievement.get('image_path', '')
        
        # Пробуем разные варианты пути к изображению
        possible_paths = [
            image_path,  # прямой путь
            os.path.join(os.path.dirname(os.path.abspath(__file__)), image_path),  # относительно текущего файла
        ]
        
        # Если путь начинается с "Эмблемы/", пробуем разные варианты
        if image_path and 'Эмблемы' in image_path:
            possible_paths.append(image_path.replace('Эмблемы/', 'Эмблемы\\'))
            possible_paths.append(os.path.join('Эмблемы', os.path.basename(image_path)))
        
        loaded = False
        for path in possible_paths:
            if path and os.path.exists(path):
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(45, 45, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.image_label.setPixmap(scaled_pixmap)
                    self.image_label.setText("")
                    loaded = True
                    break
        
        if not loaded:
            # Если изображение не загрузилось, показываем эмодзи
            self.image_label.setText("🏆")
            self.image_label.setStyleSheet("""
                QLabel {
                    background-color: #f0f5f0;
                    border: 1px solid #9bb89b;
                    border-radius: 8px;
                    font-size: 24px;
                }
            """)


class ProfileWindow(QDialog):
    avatar_updated = Signal(object)

    def __init__(self, user_data=None, db=None, parent=None):
        super().__init__(parent)
        self.user_data = user_data
        self.db = db
        self.background_path = None
        self.background_pixmap = None
        self.avatar_pixmap = None
        self.saved_avatar_path = None
        self.saved_background_path = None
        self.schedule_window = None
        self.setWindowTitle("Профиль")
        self.setFixedSize(750, 650)
        self.setModal(True)
        self.initUI()
        self.load_user_data()
        self.load_clubs()
        self.load_achievements()
        self.load_saved_images()

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

    def load_saved_images(self):
        if self.user_data and self.db:
            avatar_path = self.db.get_user_avatar_path(self.user_data['id'])
            if avatar_path and os.path.exists(avatar_path):
                pixmap = QPixmap(avatar_path)
                if not pixmap.isNull():
                    self.avatar_pixmap = self.create_circular_avatar(pixmap)
                    self.avatar_label.setPixmap(self.avatar_pixmap)
                    self.avatar_label.setText("")
                    self.saved_avatar_path = avatar_path

            background_path = self.db.get_user_background_path(self.user_data['id'])
            if background_path and os.path.exists(background_path):
                pixmap = QPixmap(background_path)
                if not pixmap.isNull():
                    self.background_pixmap = pixmap
                    self.background_path = background_path
                    self.saved_background_path = background_path
                    self.apply_background_style()

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
            QLabel#achievementsTitle {
                color: #1e4a2e;
                font-size: 16px;
                font-weight: bold;
                padding: 5px 10px;
                margin-top: 10px;
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
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
                font-size: 12px;
                min-width: 140px;
            }
            QPushButton#changeClubButton:hover {
                background-color: #527352;
            }
            QPushButton#saveClubButton {
                background-color: #6b8f6b;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
                font-size: 12px;
                min-width: 100px;
            }
            QPushButton#saveClubButton:hover {
                background-color: #527352;
            }
            QPushButton#cancelClubButton {
                background-color: #8f9e8f;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
                font-size: 12px;
                min-width: 100px;
            }
            QPushButton#cancelClubButton:hover {
                background-color: #748774;
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
            QFrame#achievementsFrame {
                background-color: #ffffff;
                border: 2px solid #9bb89b;
                border-radius: 8px;
                margin-top: 10px;
            }
            QLabel#fieldLabel {
                font-weight: bold;
                min-width: 100px;
            }
            QLabel#valueLabel {
                color: #1e3a2e;
            }
            QComboBox {
                background-color: #ffffff;
                border: 2px solid #9bb89b;
                border-radius: 5px;
                padding: 6px;
                padding-right: 25px;
                color: #1e3a2e;
                font-size: 12px;
                min-height: 30px;
            }
            QComboBox:hover {
                border-color: #6b8f6b;
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
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-top: 8px solid #527352;
                margin-top: -2px;
                margin-right: 2px;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                border: 2px solid #9bb89b;
                border-radius: 5px;
                outline: none;
                padding: 4px;
            }
            QComboBox QAbstractItemView::item {
                padding: 8px;
                background-color: #ffffff;
                color: #1e3a2e;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #c3d9c3;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #6b8f6b;
                color: white;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
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
        content_layout.setSpacing(15)
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

        info_frame = QFrame()
        info_frame.setObjectName("infoFrame")

        info_layout = QVBoxLayout(info_frame)
        info_layout.setSpacing(12)
        info_layout.setContentsMargins(20, 15, 20, 15)
        info_layout.setAlignment(Qt.AlignLeft)

        login_layout = QHBoxLayout()
        login_layout.setSpacing(10)
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
        club_layout.setSpacing(10)
        club_layout.setAlignment(Qt.AlignLeft)

        club_label = QLabel("Любимый клуб:")
        club_label.setObjectName("fieldLabel")
        club_layout.addWidget(club_label)

        self.club_value = QLabel()
        self.club_value.setObjectName("valueLabel")
        club_layout.addWidget(self.club_value)
        club_layout.addStretch()
        info_layout.addLayout(club_layout)

        self.club_edit_layout = QHBoxLayout()
        self.club_edit_layout.setSpacing(10)
        self.club_edit_layout.setAlignment(Qt.AlignLeft)

        self.club_combo = QComboBox()
        self.club_combo.setMinimumWidth(200)
        self.club_combo.setVisible(False)

        self.save_club_button = QPushButton("Сохранить")
        self.save_club_button.setObjectName("saveClubButton")
        self.save_club_button.setVisible(False)
        self.save_club_button.clicked.connect(self.save_club)

        self.cancel_club_button = QPushButton("Отмена")
        self.cancel_club_button.setObjectName("cancelClubButton")
        self.cancel_club_button.setVisible(False)
        self.cancel_club_button.clicked.connect(self.cancel_club_edit)

        self.club_edit_layout.addWidget(self.club_combo)
        self.club_edit_layout.addWidget(self.save_club_button)
        self.club_edit_layout.addWidget(self.cancel_club_button)

        info_layout.addLayout(self.club_edit_layout)

        change_club_layout = QHBoxLayout()
        change_club_layout.setAlignment(Qt.AlignLeft)

        self.change_club_button = QPushButton("Сменить любимый клуб")
        self.change_club_button.setObjectName("changeClubButton")
        self.change_club_button.clicked.connect(self.show_club_edit)
        change_club_layout.addWidget(self.change_club_button)
        info_layout.addLayout(change_club_layout)

        reg_date_layout = QHBoxLayout()
        reg_date_layout.setSpacing(10)
        reg_date_layout.setAlignment(Qt.AlignLeft)

        reg_date_label = QLabel("Дата регистрации:")
        reg_date_label.setObjectName("fieldLabel")
        reg_date_layout.addWidget(reg_date_label)

        self.reg_date_value = QLabel()
        self.reg_date_value.setObjectName("valueLabel")
        reg_date_layout.addWidget(self.reg_date_value)
        reg_date_layout.addStretch()
        info_layout.addLayout(reg_date_layout)

        right_layout.addWidget(info_frame)
        top_content_layout.addWidget(right_widget, 1)

        content_layout.addLayout(top_content_layout)

        achievements_title = QLabel("🏆 Мои достижения")
        achievements_title.setObjectName("achievementsTitle")
        content_layout.addWidget(achievements_title)

        achievements_frame = QFrame()
        achievements_frame.setObjectName("achievementsFrame")
        achievements_layout = QVBoxLayout(achievements_frame)
        achievements_layout.setContentsMargins(10, 10, 10, 10)
        achievements_layout.setSpacing(5)

        self.achievements_scroll = QScrollArea()
        self.achievements_scroll.setWidgetResizable(True)
        self.achievements_scroll.setMaximumHeight(200)
        self.achievements_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        self.achievements_container = QWidget()
        self.achievements_container.setStyleSheet("background-color: transparent;")
        self.achievements_grid_layout = QGridLayout(self.achievements_container)
        self.achievements_grid_layout.setSpacing(5)
        self.achievements_grid_layout.setContentsMargins(5, 5, 5, 5)

        self.achievements_scroll.setWidget(self.achievements_container)
        achievements_layout.addWidget(self.achievements_scroll)

        content_layout.addWidget(achievements_frame)

        self.schedule_button = QPushButton("Просмотр графика матчей")
        self.schedule_button.setObjectName("scheduleButton")
        self.schedule_button.clicked.connect(self.show_schedule_window)
        content_layout.addWidget(self.schedule_button)

        main_layout.addWidget(self.content_frame)

        self.setAutoFillBackground(True)

    def load_achievements(self):
        if not self.db or not self.user_data:
            return

        user_achievements = self.db.get_user_achievements(self.user_data['id'])

        self.clear_layout(self.achievements_grid_layout)

        if not user_achievements:
            empty_label = QLabel("У вас пока нет достижений.\nДобавляйте события, чтобы получать награды!")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("""
                QLabel {
                    color: #8f9e8f;
                    font-size: 12px;
                    font-style: italic;
                    padding: 20px;
                }
            """)
            self.achievements_grid_layout.addWidget(empty_label, 0, 0)
        else:
            for i, achievement in enumerate(user_achievements):
                row = i // 2
                col = i % 2
                ach_widget = AchievementWidget(achievement)
                self.achievements_grid_layout.addWidget(ach_widget, row, col)

        self.achievements_grid_layout.setRowStretch(self.achievements_grid_layout.rowCount(), 1)

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def load_clubs(self):
        if self.db:
            clubs = self.db.get_all_clubs_for_select()
            self.club_combo.clear()
            self.club_combo.addItem("-- Не выбран --", None)
            for club in clubs:
                self.club_combo.addItem(club['name'], club['id'])

    def show_club_edit(self):
        self.club_value.setVisible(False)
        self.change_club_button.setVisible(False)
        self.club_combo.setVisible(True)
        self.save_club_button.setVisible(True)
        self.cancel_club_button.setVisible(True)

        current_club = self.user_data.get('favorite_club', '')
        if current_club:
            index = self.club_combo.findText(current_club)
            if index >= 0:
                self.club_combo.setCurrentIndex(index)

    def cancel_club_edit(self):
        self.club_value.setVisible(True)
        self.change_club_button.setVisible(True)
        self.club_combo.setVisible(False)
        self.save_club_button.setVisible(False)
        self.cancel_club_button.setVisible(False)

    def save_club(self):
        club_name = self.club_combo.currentText()
        club_id = self.club_combo.currentData()

        if club_id is None:
            club_name = ""

        try:
            with self.db.conn.cursor() as cur:
                cur.execute("""
                    UPDATE user_profiles
                    SET favorite_club = %s
                    WHERE id = %s
                """, (club_name, self.user_data['id']))
                self.db.conn.commit()

                self.user_data['favorite_club'] = club_name
                self.club_value.setText(club_name if club_name else "Не указан")

                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("Успех")
                msg_box.setText("Любимый клуб успешно изменен!")
                msg_box.setIcon(QMessageBox.Information)
                self._setup_message_box(msg_box, "Любимый клуб успешно изменен!")
                msg_box.exec()

        except Exception as e:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Ошибка")
            msg_box.setText(f"Не удалось сохранить изменения: {e}")
            msg_box.setIcon(QMessageBox.Critical)
            self._setup_message_box(msg_box, f"Не удалось сохранить изменения: {e}")
            msg_box.exec()

        self.cancel_club_edit()

    def show_schedule_window(self):
        from window_schedule import ScheduleWindow

        self.hide()

        self.schedule_window = ScheduleWindow(self.user_data, self.db, self)
        self.schedule_window.back_to_profile.connect(self.show_profile)
        self.schedule_window.show()

    def show_profile(self):
        self.load_achievements()
        self.show()

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

    def set_avatar(self, avatar_pixmap):
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
                except Exception:
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
                except Exception:
                    self.reg_date_value.setText("Ошибка загрузки")

    def set_background(self, image_path):
        try:
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                self.background_pixmap = pixmap
                self.background_path = image_path
                self.apply_background_style()
                self.update()
        except Exception:
            pass

    def set_background_pixmap(self, pixmap):
        if pixmap and not pixmap.isNull():
            self.background_pixmap = pixmap
            self.apply_background_style()
            self.update()

    def apply_background_style(self):
        if self.background_pixmap and not self.background_pixmap.isNull():
            self.content_frame.setStyleSheet("""
                QFrame#contentFrame {
                    background-color: rgba(240, 245, 240, 200);
                    border: 2px solid rgba(155, 184, 155, 160);
                    border-radius: 10px;
                }
            """)

            for child in self.content_frame.findChildren(QFrame):
                if child.objectName() == "infoFrame":
                    child.setStyleSheet("""
                        QFrame#infoFrame {
                            background-color: rgba(255, 255, 255, 220);
                            border: 2px solid rgba(155, 184, 155, 160);
                            border-radius: 8px;
                        }
                    """)
                elif child.objectName() == "achievementsFrame":
                    child.setStyleSheet("""
                        QFrame#achievementsFrame {
                            background-color: rgba(255, 255, 255, 220);
                            border: 2px solid rgba(155, 184, 155, 160);
                            border-radius: 8px;
                        }
                    """)

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
                    border-radius: 5px;
                    padding: 8px 15px;
                    font-weight: bold;
                    font-size: 12px;
                    min-width: 140px;
                }
                QPushButton#changeClubButton:hover {
                    background-color: rgba(82, 115, 82, 240);
                }
            """)

            self.save_club_button.setStyleSheet("""
                QPushButton#saveClubButton {
                    background-color: rgba(107, 143, 107, 220);
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 8px 15px;
                    font-weight: bold;
                    font-size: 12px;
                    min-width: 100px;
                }
                QPushButton#saveClubButton:hover {
                    background-color: rgba(82, 115, 82, 240);
                }
            """)

            self.cancel_club_button.setStyleSheet("""
                QPushButton#cancelClubButton {
                    background-color: rgba(143, 158, 143, 220);
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 8px 15px;
                    font-weight: bold;
                    font-size: 12px;
                    min-width: 100px;
                }
                QPushButton#cancelClubButton:hover {
                    background-color: rgba(116, 135, 116, 240);
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

    def resizeEvent(self, event):
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
                success, relative_path = self.db.update_user_avatar(self.user_data['id'], file)

                if success:
                    self.avatar_pixmap = self.create_circular_avatar(pixmap)
                    self.avatar_label.setPixmap(self.avatar_pixmap)
                    self.avatar_label.setText("")

                    self.avatar_updated.emit(self.avatar_pixmap)

                    msg_box = QMessageBox(self)
                    msg_box.setWindowTitle("Успех")
                    msg_box.setText("Аватар успешно обновлен!")
                    msg_box.setIcon(QMessageBox.Information)
                    self._setup_message_box(msg_box, "Аватар успешно обновлен!")
                    msg_box.exec()
                else:
                    msg_box = QMessageBox(self)
                    msg_box.setWindowTitle("Ошибка")
                    msg_box.setText("Не удалось сохранить аватар!")
                    msg_box.setIcon(QMessageBox.Critical)
                    self._setup_message_box(msg_box, "Не удалось сохранить аватар!")
                    msg_box.exec()

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