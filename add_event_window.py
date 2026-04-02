# add_event_window.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                               QLabel, QPushButton, QLineEdit,
                               QTextEdit, QFrame, QWidget, QApplication,
                               QComboBox, QMessageBox, QSizePolicy, QScrollArea,
                               QListWidget, QListWidgetItem, QCompleter)
from PySide6.QtCore import Qt, QTimer, QStringListModel
from PySide6.QtGui import QFont, QPainter, QPixmap, QIntValidator
import sys


class CompleterLineEdit(QLineEdit):
    """Кастомное поле ввода с автоподсказками с помощью QCompleter"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._db = None
        self.completer = None
        self.all_clubs = []
        self.setPlaceholderText("Введите название команды")
        
    def set_db(self, db):
        """Устанавливает подключение к БД и загружает список клубов"""
        self._db = db
        if db:
            self.load_all_clubs()
    
    def load_all_clubs(self):
        """Загружает все клубы из БД"""
        try:
            clubs = self._db.get_all_clubs_for_select()
            self.all_clubs = [club['name'] for club in clubs]
            self.setup_completer()
            print(f"Загружено {len(self.all_clubs)} клубов для автоподсказок")
        except Exception as e:
            print(f"Ошибка загрузки клубов: {e}")
    
    def setup_completer(self):
        """Настраивает QCompleter для автоподсказок"""
        if not self.all_clubs:
            return
        
        # Создаем модель с данными
        self.model = QStringListModel()
        self.model.setStringList(self.all_clubs)
        
        # Создаем completer
        self.completer = QCompleter()
        self.completer.setModel(self.model)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchContains)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.completer.setMaxVisibleItems(10)
        
        # Настраиваем стиль выпадающего списка
        self.completer.popup().setStyleSheet("""
            QListView {
                background-color: #ffffff;
                border: 2px solid #9bb89b;
                border-radius: 5px;
                color: #1e3a2e;
                font-size: 12px;
                padding: 4px;
                outline: none;
            }
            QListView::item {
                padding: 8px;
                border-radius: 3px;
            }
            QListView::item:hover {
                background-color: #e8f0e8;
            }
            QListView::item:selected {
                background-color: #6b8f6b;
                color: white;
            }
        """)
        
        # Устанавливаем completer для поля ввода
        self.setCompleter(self.completer)


class AddEventWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Новое событие")
        self.setMinimumSize(500, 500)
        self.resize(500, 500)
        self.setModal(True)
        self.background_pixmap = None
        self.db = None
        self.user_data = None
        self.initUI()
        
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
            QLabel#titleLabel {
                color: #1e4a2e;
                font-size: 20px;
                font-weight: bold;
                padding: 8px 20px;
                background-color: rgba(150, 180, 150, 0.3);
                border-radius: 8px;
            }
            QLabel#fieldLabel {
                font-weight: bold;
                color: #2c4c3b;
                font-size: 12px;
                min-width: 100px;
            }
            QLineEdit, QTextEdit {
                background-color: #ffffff;
                border: 2px solid #9bb89b;
                border-radius: 5px;
                padding: 8px;
                color: #1e3a2e;
                font-size: 12px;
            }
            QLineEdit:focus, QTextEdit:focus {
                border-color: #6b8f6b;
                background-color: #f8fff8;
            }
            QLineEdit:disabled {
                background-color: #e0e8e0;
                border: 2px solid #c0d0c0;
                color: #8f9e8f;
            }
            QComboBox {
                background-color: #ffffff;
                border: 2px solid #9bb89b;
                border-radius: 5px;
                padding: 8px;
                padding-right: 25px;
                color: #000000;
                font-size: 12px;
                min-width: 150px;
            }
            QComboBox:hover {
                border-color: #6b8f6b;
            }
            QComboBox:focus {
                border-color: #4d7a4d;
            }
            QComboBox::drop-down {
                width: 25px;
                border-left: 2px solid #9bb89b;
                border-top-right-radius: 5px;
                border-bottom-right-radius: 5px;
                background-color: #e8f0e8;
            }
            QComboBox::down-arrow {
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-top: 8px solid #527352;
                margin-right: 2px;
            }
            QComboBox::down-arrow:on {
                border-top: 8px solid #3e5a3e;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff !important;
                border: 2px solid #9bb89b !important;
                border-radius: 5px !important;
                selection-background-color: #6b8f6b !important;
                selection-color: white !important;
                color: #000000 !important;
                outline: none !important;
                padding: 4px !important;
            }
            QComboBox QAbstractItemView::item {
                padding: 8px !important;
                background-color: #ffffff !important;
                color: #000000 !important;
                min-height: 25px !important;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #e8f0e8 !important;
                color: #000000 !important;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #6b8f6b !important;
                color: white !important;
            }
            QListView {
                background-color: #ffffff !important;
                border: 2px solid #9bb89b !important;
                border-radius: 5px !important;
                outline: none !important;
            }
            QListView::item {
                padding: 8px !important;
                background-color: #ffffff !important;
                color: #000000 !important;
                min-height: 25px !important;
            }
            QListView::item:hover {
                background-color: #e8f0e8 !important;
                color: #000000 !important;
            }
            QListView::item:selected {
                background-color: #6b8f6b !important;
                color: white !important;
            }
            QTextEdit {
                min-height: 70px;
                max-height: 70px;
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
            QPushButton#closeButton {
                background-color: #8f9e8f;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 20px;
                font-weight: bold;
                font-size: 13px;
                min-width: 80px;
            }
            QPushButton#closeButton:hover {
                background-color: #748774;
            }
            QPushButton#addButton {
                background-color: #6b8f6b;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 20px;
                font-weight: bold;
                font-size: 13px;
                min-width: 80px;
            }
            QPushButton#addButton:hover {
                background-color: #527352;
            }
            QFrame#infoFrame {
                background-color: #ffffff;
                border: 2px solid #9bb89b;
                border-radius: 8px;
            }
            QFrame#scoreFrame {
                background-color: #f8fff8;
                border: 2px solid #9bb89b;
                border-radius: 8px;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                width: 8px;
                border-radius: 4px;
                background-color: #d0e0d0;
            }
            QScrollBar::handle:vertical {
                background-color: #6b8f6b;
                border-radius: 4px;
                min-height: 20px;
            }
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 15, 20, 15)
        main_layout.setSpacing(5)
        
        # Верхняя панель
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)
        
        self.back_button = QPushButton(" ⇦")
        self.back_button.setObjectName("backButton")
        font = QFont()
        font.setBold(True)
        font.setPointSize(28)
        self.back_button.setFont(font)
        self.back_button.clicked.connect(self.reject)
        top_layout.addWidget(self.back_button)
        
        title_label = QLabel("Новое событие")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        top_layout.addWidget(title_label)
        
        right_spacer = QWidget()
        right_spacer.setFixedSize(40, 40)
        right_spacer.setStyleSheet("background-color: transparent;")
        top_layout.addWidget(right_spacer)
        
        main_layout.addLayout(top_layout)
        
        # Основной контент
        self.content_frame = QFrame()
        self.content_frame.setObjectName("contentFrame")
        self.content_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.content_frame.setMaximumHeight(520)
        
        content_layout = QVBoxLayout(self.content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameStyle(QFrame.NoFrame)
        scroll_area.setMaximumHeight(500)
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(0)
        scroll_layout.setContentsMargins(20, 15, 20, 10)
        
        # Информационный фрейм
        info_frame = QFrame()
        info_frame.setObjectName("infoFrame")
        
        info_layout = QVBoxLayout(info_frame)
        info_layout.setSpacing(10)
        info_layout.setContentsMargins(20, 15, 20, 15)
        
        # Команда 1 - с автоподсказками
        team1_layout = QHBoxLayout()
        team1_layout.setSpacing(10)
        team1_label = QLabel("Команда 1:")
        team1_label.setObjectName("fieldLabel")
        team1_layout.addWidget(team1_label)
        
        self.team1_edit = CompleterLineEdit(self)
        self.team1_edit.setMinimumHeight(40)
        self.team1_edit.setStyleSheet("font-size: 13px; padding: 10px;")
        team1_layout.addWidget(self.team1_edit)
        info_layout.addLayout(team1_layout)
        
        # Команда 2 - с автоподсказками
        team2_layout = QHBoxLayout()
        team2_layout.setSpacing(10)
        team2_label = QLabel("Команда 2:")
        team2_label.setObjectName("fieldLabel")
        team2_layout.addWidget(team2_label)
        
        self.team2_edit = CompleterLineEdit(self)
        self.team2_edit.setMinimumHeight(40)
        self.team2_edit.setStyleSheet("font-size: 13px; padding: 10px;")
        team2_layout.addWidget(self.team2_edit)
        info_layout.addLayout(team2_layout)
        
        # Фрейм счета
        score_frame = QFrame()
        score_frame.setObjectName("scoreFrame")
        score_layout = QHBoxLayout(score_frame)
        score_layout.setSpacing(12)
        score_layout.setContentsMargins(15, 8, 15, 8)
        
        score_label = QLabel("Счет:")
        score_label.setObjectName("fieldLabel")
        score_layout.addWidget(score_label)
        
        score_inputs = QHBoxLayout()
        score_inputs.setSpacing(5)
        
        self.score1_edit = QLineEdit()
        self.score1_edit.setPlaceholderText("0")
        self.score1_edit.setFixedWidth(55)
        self.score1_edit.setFixedHeight(32)
        self.score1_edit.setAlignment(Qt.AlignCenter)
        self.score1_edit.setValidator(QIntValidator(0, 99, self))
        score_inputs.addWidget(self.score1_edit)
        
        colon = QLabel(":")
        colon.setStyleSheet("font-size: 18px; font-weight: bold; background: transparent;")
        colon.setFixedWidth(12)
        score_inputs.addWidget(colon)
        
        self.score2_edit = QLineEdit()
        self.score2_edit.setPlaceholderText("0")
        self.score2_edit.setFixedWidth(55)
        self.score2_edit.setFixedHeight(32)
        self.score2_edit.setAlignment(Qt.AlignCenter)
        self.score2_edit.setValidator(QIntValidator(0, 99, self))
        score_inputs.addWidget(self.score2_edit)
        
        score_layout.addLayout(score_inputs)
        score_layout.addStretch()
        info_layout.addWidget(score_frame)
        
        # Статус
        status_layout = QHBoxLayout()
        status_layout.setSpacing(10)
        status_label = QLabel("Статус:")
        status_label.setObjectName("fieldLabel")
        status_layout.addWidget(status_label)
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Запланирован", "Завершен"])
        self.status_combo.setMinimumHeight(32)
        self.status_combo.currentIndexChanged.connect(self.on_status_changed)
        status_layout.addWidget(self.status_combo)
        status_layout.addStretch()
        info_layout.addLayout(status_layout)
        
        scroll_layout.addWidget(info_frame)
        
        # Комментарий
        comment_label = QLabel("Комментарий:")
        comment_label.setObjectName("fieldLabel")
        comment_label.setContentsMargins(0, 10, 0, 0)
        
        self.comment_edit = QTextEdit()
        self.comment_edit.setPlaceholderText("Введите комментарий...")
        self.comment_edit.setMinimumHeight(60)
        self.comment_edit.setMaximumHeight(60)
        self.comment_edit.setContentsMargins(0, 0, 0, 0)
        
        scroll_layout.addWidget(comment_label)
        scroll_layout.addWidget(self.comment_edit)
        
        scroll_area.setWidget(scroll_content)
        content_layout.addWidget(scroll_area)
        
        main_layout.addWidget(self.content_frame)
        
        # Кнопки
        buttons_widget = QWidget()
        buttons_widget.setMaximumHeight(50)
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setSpacing(15)
        buttons_layout.setContentsMargins(20, 0, 20, 5)
        
        self.close_button = QPushButton("Отмена")
        self.close_button.setObjectName("closeButton")
        self.close_button.clicked.connect(self.reject)
        
        self.add_button = QPushButton("Добавить")
        self.add_button.setObjectName("addButton")
        self.add_button.clicked.connect(self.save_event)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.close_button)
        buttons_layout.addWidget(self.add_button)
        buttons_layout.addStretch()
        
        main_layout.addWidget(buttons_widget)
        
        # Добавляем растягивающийся спейсер в конце
        main_layout.addStretch()
        
        self.setAutoFillBackground(True)
        
        self.score1_edit.setText("0")
        self.score2_edit.setText("0")
        self.on_status_changed(0)
    
    def set_database(self, db):
        self.db = db
        # Передаем db в поля с автоподсказками
        if hasattr(self, 'team1_edit'):
            self.team1_edit.set_db(db)
        if hasattr(self, 'team2_edit'):
            self.team2_edit.set_db(db)
    
    def set_user_data(self, user_data):
        self.user_data = user_data
    
    def on_status_changed(self, index):
        is_planned = (index == 0)
        self.score1_edit.setDisabled(is_planned)
        self.score2_edit.setDisabled(is_planned)
        
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
            
            self.content_frame.setStyleSheet("""
                QFrame#contentFrame {
                    background-color: rgba(240, 245, 240, 200);
                    border: 2px solid rgba(155, 184, 155, 160);
                    border-radius: 10px;
                }
            """)
        else:
            super().paintEvent(event)
    
    def set_background(self, image_path):
        try:
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                self.background_pixmap = pixmap
                self.update()
        except Exception as e:
            print(f"Ошибка установки фона: {e}")
    
    def set_background_pixmap(self, pixmap):
        if pixmap and not pixmap.isNull():
            self.background_pixmap = pixmap
            self.update()
    
    def resizeEvent(self, event):
        if self.background_pixmap and not self.background_pixmap.isNull():
            self.update()
        super().resizeEvent(event)
    
    def save_event(self):
        team1_input = self.team1_edit.text().strip()
        team2_input = self.team2_edit.text().strip()
        
        if not team1_input or not team2_input:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Предупреждение")
            msg_box.setText("Пожалуйста, заполните названия обеих команд")
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
        
        if team1_input == team2_input:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Предупреждение")
            msg_box.setText("Команды не могут быть одинаковыми")
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
        
        if not self.db:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Ошибка")
            msg_box.setText("Нет подключения к базе данных")
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
            return
        
        team1_data = self.db.get_club_by_name(team1_input)
        team2_data = self.db.get_club_by_name(team2_input)
        
        if team1_data is None:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Ошибка")
            msg_box.setText(f"Команда '{team1_input}' не найдена в базе данных.\nПожалуйста, проверьте название.")
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
        
        if team2_data is None:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Ошибка")
            msg_box.setText(f"Команда '{team2_input}' не найдена в базе данных.\nПожалуйста, проверьте название.")
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
        
        team1 = team1_data['name']
        team2 = team2_data['name']
        
        try:
            score1 = int(self.score1_edit.text() or "0")
            score2 = int(self.score2_edit.text() or "0")
        except ValueError:
            score1 = 0
            score2 = 0
        
        status = self.status_combo.currentText()
        comment = self.comment_edit.toPlainText().strip()
        
        saved_to_db = False
        if self.db and self.user_data and self.user_data.get('id'):
            try:
                success, event_id, message = self.db.add_event(
                    user_id=self.user_data['id'],
                    team1=team1,
                    team2=team2,
                    score1=score1,
                    score2=score2,
                    status=status,
                    comment=comment
                )
                
                if success:
                    saved_to_db = True
                    print(f"Событие сохранено в БД с ID: {event_id}")
                else:
                    print(f"Ошибка сохранения в БД: {message}")
            except Exception as e:
                print(f"Исключение при сохранении в БД: {e}")
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Успех")
        
        if saved_to_db:
            msg_box.setText("Событие успешно добавлено и сохранено в базу данных!")
        else:
            msg_box.setText("Событие успешно добавлено!\n(Данные не сохранены в БД - проверьте подключение)")
        
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
        
        self.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AddEventWindow()
    window.show()
    sys.exit(app.exec())