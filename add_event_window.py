# add_event_window.py.
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                               QLabel, QPushButton, QLineEdit,
                               QTextEdit, QFrame, QWidget, QApplication,
                               QComboBox, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPainter, QPixmap, QIntValidator
import sys

class AddEventWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Новое событие")
        self.setFixedSize(700, 780)
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
                min-width: 120px;
            }
            QLineEdit, QTextEdit {
                background-color: #ffffff;
                border: 2px solid #9bb89b;
                border-radius: 5px;
                padding: 8px;
                color: #1e3a2e;
                font-size: 12px;
                min-height: 20px;
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
                color: #1e3a2e;
                font-size: 12px;
                min-height: 20px;
                min-width: 150px;
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
                border-radius: 3px;
                background-color: #ffffff;
                color: #1e3a2e;
                min-height: 30px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #c3d9c3;
                color: #1e3a2e;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #6b8f6b;
                color: white;
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
                padding: 10px;
                font-weight: bold;
                font-size: 14px;
                min-height: 40px;
            }
            QPushButton#closeButton:hover {
                background-color: #748774;
            }
            QPushButton#addButton {
                background-color: #6b8f6b;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 12px;
                font-weight: bold;
                font-size: 14px;
                min-height: 40px;
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
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Верхняя панель с кнопкой назад и заголовком
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
        
        # Основной контентный фрейм
        self.content_frame = QFrame()
        self.content_frame.setObjectName("contentFrame")
        
        content_layout = QVBoxLayout(self.content_frame)
        content_layout.setSpacing(15)
        content_layout.setContentsMargins(25, 20, 25, 20)
        
        # Фрейм для ввода данных
        info_frame = QFrame()
        info_frame.setObjectName("infoFrame")
        
        info_layout = QVBoxLayout(info_frame)
        info_layout.setSpacing(12)
        info_layout.setContentsMargins(20, 15, 20, 15)
        
        # Команда 1
        team1_layout = QHBoxLayout()
        team1_layout.setSpacing(10)
        team1_layout.setAlignment(Qt.AlignLeft)
        
        team1_label = QLabel("Команда 1:")
        team1_label.setObjectName("fieldLabel")
        team1_layout.addWidget(team1_label)
        
        self.team1_edit = QLineEdit()
        self.team1_edit.setPlaceholderText("Введите название команды")
        self.team1_edit.setMinimumHeight(35)
        team1_layout.addWidget(self.team1_edit)
        
        info_layout.addLayout(team1_layout)
        
        # Команда 2
        team2_layout = QHBoxLayout()
        team2_layout.setSpacing(10)
        team2_layout.setAlignment(Qt.AlignLeft)
        
        team2_label = QLabel("Команда 2:")
        team2_label.setObjectName("fieldLabel")
        team2_layout.addWidget(team2_label)
        
        self.team2_edit = QLineEdit()
        self.team2_edit.setPlaceholderText("Введите название команды")
        self.team2_edit.setMinimumHeight(35)
        team2_layout.addWidget(self.team2_edit)
        
        info_layout.addLayout(team2_layout)
        
        # Фрейм для счета
        score_frame = QFrame()
        score_frame.setObjectName("scoreFrame")
        
        score_layout = QHBoxLayout(score_frame)
        score_layout.setSpacing(15)
        score_layout.setContentsMargins(15, 12, 15, 12)
        score_layout.setAlignment(Qt.AlignCenter)
        
        # Счет
        score_label = QLabel("Счет:")
        score_label.setObjectName("fieldLabel")
        score_layout.addWidget(score_label)
        
        # Создаем контейнер для полей счета
        score_inputs_layout = QHBoxLayout()
        score_inputs_layout.setSpacing(8)
        
        # Поле для голов первой команды
        self.score1_edit = QLineEdit()
        self.score1_edit.setPlaceholderText("0")
        self.score1_edit.setFixedWidth(55)
        self.score1_edit.setFixedHeight(35)
        self.score1_edit.setAlignment(Qt.AlignCenter)
        self.score1_edit.setMaxLength(2)
        
        # Валидатор только для цифр
        int_validator = QIntValidator(0, 99, self)
        self.score1_edit.setValidator(int_validator)
        
        score_inputs_layout.addWidget(self.score1_edit)
        
        # Двоеточие
        colon_label = QLabel(":")
        colon_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c4c3b; background-color: transparent;")
        colon_label.setFixedWidth(12)
        colon_label.setAlignment(Qt.AlignCenter)
        score_inputs_layout.addWidget(colon_label)
        
        # Поле для голов второй команды
        self.score2_edit = QLineEdit()
        self.score2_edit.setPlaceholderText("0")
        self.score2_edit.setFixedWidth(55)
        self.score2_edit.setFixedHeight(35)
        self.score2_edit.setAlignment(Qt.AlignCenter)
        self.score2_edit.setMaxLength(2)
        self.score2_edit.setValidator(int_validator)
        
        score_inputs_layout.addWidget(self.score2_edit)
        
        score_layout.addLayout(score_inputs_layout)
        score_layout.addStretch()
        
        info_layout.addWidget(score_frame)
        
        # Статус матча - выпадающий список
        status_layout = QHBoxLayout()
        status_layout.setSpacing(10)
        status_layout.setAlignment(Qt.AlignLeft)
        
        status_label = QLabel("Статус:")
        status_label.setObjectName("fieldLabel")
        status_layout.addWidget(status_label)
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Запланирован", "Завершен"])
        self.status_combo.setCurrentIndex(0)
        self.status_combo.setMinimumWidth(180)
        self.status_combo.setMinimumHeight(32)
        self.status_combo.currentIndexChanged.connect(self.on_status_changed)
        
        # Стиль для комбобокса без черной заливки
        self.status_combo.setStyleSheet("""
            QComboBox {
                background-color: #ffffff;
                border: 2px solid #9bb89b;
                border-radius: 5px;
                padding: 6px;
                padding-right: 25px;
                color: #1e3a2e;
                font-size: 12px;
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
        """)
        
        self.status_combo.setToolTip("Выберите статус матча")
        
        status_layout.addWidget(self.status_combo)
        status_layout.addStretch()
        
        info_layout.addLayout(status_layout)
        
        content_layout.addWidget(info_frame)
        
        # Комментарий к матчу
        comment_label = QLabel("Комментарий:")
        comment_label.setObjectName("fieldLabel")
        content_layout.addWidget(comment_label)
        
        self.comment_edit = QTextEdit()
        self.comment_edit.setPlaceholderText("Введите комментарий...")
        self.comment_edit.setMinimumHeight(70)
        self.comment_edit.setMaximumHeight(70)
        content_layout.addWidget(self.comment_edit)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        self.close_button = QPushButton("Закрыть")
        self.close_button.setObjectName("closeButton")
        self.close_button.clicked.connect(self.reject)
        
        self.add_button = QPushButton("Добавить")
        self.add_button.setObjectName("addButton")
        self.add_button.clicked.connect(self.save_event)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.close_button)
        buttons_layout.addWidget(self.add_button)
        
        content_layout.addLayout(buttons_layout)
        
        main_layout.addWidget(self.content_frame)
        
        self.setAutoFillBackground(True)
        
        # Устанавливаем значения по умолчанию
        self.score1_edit.setText("0")
        self.score2_edit.setText("0")
        
        # Применяем начальное состояние (счет заблокирован для запланированного матча)
        self.on_status_changed(0)
    
    def set_database(self, db):
        """Устанавливает объект базы данных"""
        self.db = db
    
    def set_user_data(self, user_data):
        """Устанавливает данные пользователя"""
        self.user_data = user_data
    
    def on_status_changed(self, index):
        """Обработчик изменения статуса"""
        is_planned = (index == 0)  # Запланирован
        self.score1_edit.setDisabled(is_planned)
        self.score2_edit.setDisabled(is_planned)
        
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
            
            # Делаем контентный фрейм полупрозрачным при наличии фона
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
        """Устанавливает фоновое изображение по пути к файлу"""
        try:
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                self.background_pixmap = pixmap
                self.update()
        except Exception as e:
            print(f"Ошибка установки фона: {e}")
    
    def set_background_pixmap(self, pixmap):
        """Устанавливает фоновое изображение из QPixmap"""
        if pixmap and not pixmap.isNull():
            self.background_pixmap = pixmap
            self.update()
    
    def resizeEvent(self, event):
        """Обновляет фон при изменении размера окна"""
        if self.background_pixmap and not self.background_pixmap.isNull():
            self.update()
        super().resizeEvent(event)
    
    def save_event(self):
        """Сохраняет данные события"""
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
        
        # Проверяем существование команд в базе данных
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
        
        # Получаем данные о командах (ID и правильное название)
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
        
        # Используем правильные названия команд из базы данных
        team1 = team1_data['name']
        team2 = team2_data['name']
        
        # Получаем значения счета
        try:
            score1 = int(self.score1_edit.text() or "0")
            score2 = int(self.score2_edit.text() or "0")
        except ValueError:
            score1 = 0
            score2 = 0
        
        # Получаем статус из выпадающего списка
        status = self.status_combo.currentText()
        comment = self.comment_edit.toPlainText().strip()
        
        # Выводим в консоль для отладки
        print(f"Событие добавлено: {team1} - {team2}")
        print(f"Счет: {score1}:{score2}")
        print(f"Статус: {status}")
        print(f"Комментарий: {comment}")
        
        # Сохраняем в базу данных
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
        
        # Показываем сообщение об успешном добавлении
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


# Код для самостоятельного запуска окна
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AddEventWindow()
    window.show()
    sys.exit(app.exec())