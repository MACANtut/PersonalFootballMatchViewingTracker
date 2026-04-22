# window_events.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QPushButton, QFrame, QScrollArea,
                               QSizePolicy, QDialog, QMessageBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPainter, QPixmap
from add_event_window import AddEventWindow
from image_cache import image_cache


class EventWidget(QFrame):
    event_clicked = Signal(int)

    def __init__(self, event_data, db=None, is_admin=False, parent=None):
        super().__init__(parent)
        self.event_data = event_data
        self.db = db
        self.is_admin = is_admin
        self.initUI()
        self.setCursor(Qt.PointingHandCursor)
        self.load_emblems()

    def initUI(self):
        self.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 2px solid #9bb89b;
                border-radius: 8px;
                margin: 2px 0px;
            }
            QFrame:hover {
                background-color: #f0f8f0;
                border-color: #6b8f6b;
            }
            QLabel {
                color: #2c4c3b;
                font-size: 12px;
                padding: 5px;
            }
            QLabel#teamLabel {
                font-weight: bold;
                font-size: 13px;
            }
            QLabel#scoreLabel {
                font-weight: bold;
                color: #1e4a2e;
                font-size: 14px;
            }
            QLabel#statusLabel {
                color: #6b8f6b;
                font-style: italic;
            }
            QLabel#dateLabel {
                color: #8f9e8f;
                font-size: 11px;
            }
            QLabel#userLabel {
                color: #527352;
                font-size: 11px;
                font-weight: bold;
                background-color: #e8f0e8;
                padding: 3px 8px;
                border-radius: 4px;
            }
            QLabel#commentLabel {
                color: #527352;
                font-size: 11px;
                font-style: italic;
                background-color: #f0f5f0;
                padding: 5px 8px;
                border-radius: 4px;
                margin-top: 3px;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 10, 15, 10)
        main_layout.setSpacing(5)

        top_layout = QHBoxLayout()
        top_layout.setSpacing(15)
        top_layout.setAlignment(Qt.AlignVCenter)

        self.team1_container = QWidget()
        team1_layout = QHBoxLayout(self.team1_container)
        team1_layout.setContentsMargins(0, 0, 0, 0)
        team1_layout.setSpacing(10)

        self.team1_emblem_label = QLabel()
        self.team1_emblem_label.setFixedSize(40, 40)
        self.team1_emblem_label.setAlignment(Qt.AlignCenter)
        self.team1_emblem_label.setStyleSheet("""
            QLabel {
                background-color: #f0f5f0;
                border: 1px solid #9bb89b;
                border-radius: 5px;
                padding: 2px;
            }
        """)
        self.team1_emblem_label.setText("⚽")
        team1_layout.addWidget(self.team1_emblem_label)

        self.team1_name_label = QLabel(self.event_data['team1'])
        self.team1_name_label.setObjectName("teamLabel")
        team1_layout.addWidget(self.team1_name_label)

        top_layout.addWidget(self.team1_container)

        vs_label = QLabel("-")
        vs_label.setStyleSheet("font-weight: bold; font-size: 16px; padding: 0 10px;")
        top_layout.addWidget(vs_label)

        self.team2_container = QWidget()
        team2_layout = QHBoxLayout(self.team2_container)
        team2_layout.setContentsMargins(0, 0, 0, 0)
        team2_layout.setSpacing(10)

        self.team2_emblem_label = QLabel()
        self.team2_emblem_label.setFixedSize(40, 40)
        self.team2_emblem_label.setAlignment(Qt.AlignCenter)
        self.team2_emblem_label.setStyleSheet("""
            QLabel {
                background-color: #f0f5f0;
                border: 1px solid #9bb89b;
                border-radius: 5px;
                padding: 2px;
            }
        """)
        self.team2_emblem_label.setText("⚽")
        team2_layout.addWidget(self.team2_emblem_label)

        self.team2_name_label = QLabel(self.event_data['team2'])
        self.team2_name_label.setObjectName("teamLabel")
        team2_layout.addWidget(self.team2_name_label)

        top_layout.addWidget(self.team2_container)

        score_text = f"{self.event_data['score1']}:{self.event_data['score2']}"
        if self.event_data['status'] == "Запланирован":
            score_text = "?:?"
        score_label = QLabel(score_text)
        score_label.setObjectName("scoreLabel")
        score_label.setMinimumWidth(60)
        score_label.setAlignment(Qt.AlignCenter)
        top_layout.addWidget(score_label)

        status_label = QLabel(self.event_data['status'])
        status_label.setObjectName("statusLabel")
        status_label.setMinimumWidth(100)
        top_layout.addWidget(status_label)

        top_layout.addStretch()

        if self.is_admin and self.event_data.get('username'):
            user_text = f"👤 {self.event_data['username']}"
            if self.event_data.get('first_name') or self.event_data.get('last_name'):
                name = f"{self.event_data.get('first_name', '')} {self.event_data.get('last_name', '')}".strip()
                if name:
                    user_text = f"👤 {name} (@{self.event_data['username']})"
            user_label = QLabel(user_text)
            user_label.setObjectName("userLabel")
            top_layout.addWidget(user_label)

        if self.event_data.get('created_at'):
            if hasattr(self.event_data['created_at'], 'strftime'):
                date_str = self.event_data['created_at'].strftime("%d.%m.%Y %H:%M")
            else:
                date_str = str(self.event_data['created_at'])[:16]
        else:
            date_str = "Дата не указана"
        date_label = QLabel(date_str)
        date_label.setObjectName("dateLabel")
        top_layout.addWidget(date_label)

        main_layout.addLayout(top_layout)

        if self.event_data.get('comment') and self.event_data['comment'].strip():
            comment_label = QLabel(f" 💬 {self.event_data['comment']}")
            comment_label.setObjectName("commentLabel")
            comment_label.setWordWrap(True)
            main_layout.addWidget(comment_label)

    def load_emblems(self):
        team1_emblem = self.event_data.get('team1_emblem')
        team2_emblem = self.event_data.get('team2_emblem')

        if team1_emblem:
            self.load_emblem_async(team1_emblem, self.team1_emblem_label)

        if team2_emblem:
            self.load_emblem_async(team2_emblem, self.team2_emblem_label)

    def load_emblem_async(self, url, label):
        label.setText("...")
        label.setStyleSheet("""
            QLabel {
                background-color: #f0f5f0;
                border: 1px solid #9bb89b;
                border-radius: 5px;
                padding: 2px;
                font-size: 12px;
            }
        """)

        def on_image_loaded(pixmap):
            if pixmap and not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(36, 36, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                label.setPixmap(scaled_pixmap)
                label.setText("")
                label.setStyleSheet("""
                    QLabel {
                        background-color: #f0f5f0;
                        border: 1px solid #9bb89b;
                        border-radius: 5px;
                        padding: 2px;
                    }
                """)
            else:
                label.setText("⚽")
                label.setStyleSheet("""
                    QLabel {
                        background-color: #f0f5f0;
                        border: 1px solid #9bb89b;
                        border-radius: 5px;
                        padding: 2px;
                        font-size: 20px;
                    }
                """)

        image_cache.get_image(url, on_image_loaded)

    def mouseDoubleClickEvent(self, event):
        event_id = self.event_data.get('id')
        if event_id:
            self.event_clicked.emit(event_id)
        super().mouseDoubleClickEvent(event)


class EventsWindow(QWidget):
    event_added = Signal()
    achievements_updated = Signal()

    def __init__(self, user_data=None, db=None, parent=None):
        super().__init__(parent)
        self.user_data = user_data
        self.db = db
        self.background_pixmap = None
        self._background_set = False  # Флаг, установлен ли фон
        self.events_list = []
        self.add_event_dialog = None
        self.main_window = None

        self.is_admin = (user_data and user_data.get('username') == 'admin')

        self.initUI()
        self.load_events()
        
        # Устанавливаем атрибуты для правильной работы с фоном
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setAutoFillBackground(False)
        self._background_set = False

    def initUI(self):
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
            QLabel#eventsTitle {
                color: #1e4a2e;
                font-size: 20px;
                font-weight: bold;
                padding: 8px 20px;
                background-color: rgba(150, 180, 150, 0.3);
                border-radius: 8px;
            }
            QLabel#hintLabel {
                color: #8f9e8f;
                font-size: 11px;
                font-style: italic;
                padding: 5px;
            }
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
            QPushButton#addEventButton {
                background-color: #6b8f6b;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 13px;
                min-width: 160px;
            }
            QPushButton#addEventButton:hover {
                background-color: #527352;
            }
            QLabel#adminStatsLabel {
                color: #1e4a2e;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
                background-color: rgba(107, 143, 107, 0.85);
                border-radius: 8px;
                border: 1px solid #6b8f6b;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(15)

        if self.is_admin:
            events_title = QLabel("📊 Статистика всех пользователей (Админ)")
        else:
            events_title = QLabel("Ваши события")
        events_title.setObjectName("eventsTitle")
        events_title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(events_title)

        hint_label = QLabel("💡 Дважды кликните по событию, чтобы изменить его")
        hint_label.setObjectName("hintLabel")
        hint_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(hint_label)

        if self.is_admin:
            self.admin_stats_label = QLabel("Загрузка статистики...")
            self.admin_stats_label.setObjectName("adminStatsLabel")
            self.admin_stats_label.setAlignment(Qt.AlignCenter)
            main_layout.addWidget(self.admin_stats_label)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameStyle(QFrame.NoFrame)
        scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.events_container = QWidget()
        self.events_container.setStyleSheet("background-color: transparent;")
        self.events_layout = QVBoxLayout(self.events_container)
        self.events_layout.setSpacing(8)
        self.events_layout.setContentsMargins(5, 5, 5, 5)
        self.events_layout.addStretch()

        scroll_area.setWidget(self.events_container)
        main_layout.addWidget(scroll_area)

        if not self.is_admin:
            button_container = QWidget()
            button_layout = QHBoxLayout(button_container)
            button_layout.setContentsMargins(0, 10, 0, 0)
            button_layout.addStretch()

            self.add_event_button = QPushButton("+ Добавить событие")
            self.add_event_button.setObjectName("addEventButton")
            self.add_event_button.clicked.connect(self.open_add_event_dialog)
            button_layout.addWidget(self.add_event_button)

            main_layout.addWidget(button_container)

    def set_background_pixmap(self, pixmap):
        """Установка фонового изображения - только если фон изменился"""
        if pixmap and not pixmap.isNull():
            # Проверяем, не установлен ли уже такой же фон
            if self._background_set and self.background_pixmap is not None:
                # Сравниваем по cacheKey (уникальный идентификатор QPixmap)
                if self.background_pixmap.cacheKey() == pixmap.cacheKey():
                    return  # Фон уже установлен, ничего не делаем
            
            self.background_pixmap = pixmap
            self._background_set = True
            # Принудительно перерисовываем виджет
            self.update()

    def paintEvent(self, event):
        """Отрисовка фона - один раз за кадр"""
        if self.background_pixmap and not self.background_pixmap.isNull():
            painter = QPainter(self)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)
            
            # Масштабируем изображение
            scaled_pixmap = self.background_pixmap.scaled(
                self.size(),
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )
            
            # Центрируем изображение
            x = (self.width() - scaled_pixmap.width()) // 2
            y = (self.height() - scaled_pixmap.height()) // 2
            
            # Рисуем фон (перезаписываем предыдущий, а не накладываем)
            painter.drawPixmap(x, y, scaled_pixmap)
            painter.end()
        else:
            # Если нет фона, используем стандартную отрисовку
            super().paintEvent(event)

    def showEvent(self, event):
        """При показе виджета перерисовываем фон"""
        super().showEvent(event)
        if self.background_pixmap and not self.background_pixmap.isNull():
            self.update()

    def resizeEvent(self, event):
        """При изменении размера перерисовываем фон"""
        super().resizeEvent(event)
        if self.background_pixmap and not self.background_pixmap.isNull():
            self.update()

    def load_events(self):
        if not self.db:
            return

        try:
            if self.is_admin:
                self.events_list = self.db.get_all_events_for_admin()
                self.update_admin_stats()
            else:
                if self.user_data and self.user_data.get('id'):
                    self.events_list = self.db.get_user_events(self.user_data['id'])

            self.update_events_display()
        except Exception:
            self.events_list = []

    def update_admin_stats(self):
        if not self.is_admin or not self.db:
            return

        total_events = len(self.events_list)

        unique_users = set()
        completed_matches = 0

        for event in self.events_list:
            if event.get('user_id'):
                unique_users.add(event['user_id'])
            if event.get('status') == 'Завершен':
                completed_matches += 1

        stats_text = f"📈 Всего матчей: {total_events} | 👥 Пользователей: {len(unique_users)} | ✅ Завершено: {completed_matches}"
        self.admin_stats_label.setText(stats_text)

    def update_events_display(self):
        # Очищаем контейнер
        while self.events_layout.count() > 1:
            item = self.events_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self.events_list:
            if self.is_admin:
                no_events_label = QLabel("В системе пока нет добавленных событий")
            else:
                no_events_label = QLabel("У вас пока нет добавленных событий")
            no_events_label.setAlignment(Qt.AlignCenter)
            no_events_label.setStyleSheet("""
                QLabel {
                    color: #8f9e8f;
                    font-size: 14px;
                    font-style: italic;
                    padding: 30px;
                    background-color: rgba(255, 255, 255, 0.7);
                    border: 2px dashed #9bb89b;
                    border-radius: 8px;
                }
            """)
            self.events_layout.insertWidget(0, no_events_label)
        else:
            for event in self.events_list:
                event_widget = EventWidget(event, self.db, self.is_admin)
                event_widget.event_clicked.connect(self.edit_event)
                self.events_layout.insertWidget(self.events_layout.count() - 1, event_widget)

    def edit_event(self, event_id):
        if not event_id:
            return

        event = self.db.get_event_by_id(event_id)
        if event:
            dialog = AddEventWindow(self, edit_mode=True, event_data=event)
            dialog.set_database(self.db)
            dialog.set_user_data(self.user_data)
            if hasattr(self, 'background_pixmap') and self.background_pixmap:
                dialog.set_background_pixmap(self.background_pixmap)
            dialog.event_saved.connect(self.on_event_saved)
            dialog.exec()

    def open_add_event_dialog(self):
        if self.is_admin:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Информация")
            msg_box.setText("Администратор может просматривать статистику всех пользователей, но для добавления событий используйте обычную учетную запись.")
            msg_box.setIcon(QMessageBox.Information)
            msg_box.exec()
            return

        self.add_event_dialog = AddEventWindow(self, edit_mode=False)
        self.add_event_dialog.set_user_data(self.user_data)
        self.add_event_dialog.set_database(self.db)
        self.add_event_dialog.event_saved.connect(self.on_event_saved)

        if self.background_pixmap:
            self.add_event_dialog.set_background_pixmap(self.background_pixmap)

        self.add_event_dialog.exec()

    def on_event_saved(self):
        self.load_events()
        self.achievements_updated.emit()
        self.update_achievements()

        if self.main_window:
            for child in self.main_window.children():
                if child.__class__.__name__ == 'ProfileWindow':
                    if hasattr(child, 'load_achievements'):
                        child.load_achievements()
                    break

    def update_achievements(self):
        if not self.is_admin and self.db and self.user_data:
            try:
                self.db.check_and_award_achievements(self.user_data['id'])
            except Exception:
                pass