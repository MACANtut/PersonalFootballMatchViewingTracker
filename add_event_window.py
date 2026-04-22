# add_event_window.py
import json
import os
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                               QLabel, QPushButton, QLineEdit,
                               QTextEdit, QFrame, QWidget, QApplication,
                               QComboBox, QMessageBox, QSizePolicy, QScrollArea,
                               QSpinBox)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QPainter, QPixmap, QIntValidator
import sys


def get_ratings_file_path(user_id):
    ratings_dir = "player_ratings"
    if not os.path.exists(ratings_dir):
        os.makedirs(ratings_dir)
    return os.path.join(ratings_dir, f"ratings_user_{user_id}.json")


def save_ratings_to_json(user_id, ratings):
    if not ratings:
        return
    file_path = get_ratings_file_path(user_id)
    try:
        data_to_save = {str(k): v for k, v in ratings.items()}
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)
    except Exception:
        pass


def load_ratings_from_json(user_id):
    file_path = get_ratings_file_path(user_id)
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {int(k): v for k, v in data.items()}
        except Exception:
            return {}
    return {}


def save_event_ratings_to_json(user_id, event_id, ratings):
    if not ratings:
        return
    file_path = get_ratings_file_path(user_id)
    try:
        all_data = {}
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                all_data = json.load(f)
        all_data[str(event_id)] = {str(k): v for k, v in ratings.items()}
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=4)
    except Exception:
        pass


def load_event_ratings_from_json(user_id, event_id):
    file_path = get_ratings_file_path(user_id)
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                all_data = json.load(f)
            event_ratings = all_data.get(str(event_id), {})
            return {int(k): v for k, v in event_ratings.items()}
        except Exception:
            return {}
    return {}


class PlayerRatingWidget(QWidget):
    rating_changed = Signal(int, int)

    def __init__(self, player_id, player_name, initial_rating=5, parent=None):
        super().__init__(parent)
        self.player_id = player_id
        self.player_name = player_name
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.initUI(initial_rating)

    def initUI(self, initial_rating):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 3, 5, 3)
        layout.setSpacing(8)

        self.name_label = QLabel(self.player_name)
        self.name_label.setStyleSheet("""
            QLabel {
                color: #2c4c3b;
                font-size: 11px;
                font-weight: bold;
            }
        """)
        self.name_label.setMinimumWidth(100)
        layout.addWidget(self.name_label)
        layout.addStretch()

        rating_label = QLabel("Оценка:")
        rating_label.setStyleSheet("color: #2c4c3b; font-size: 10px;")
        layout.addWidget(rating_label)

        self.rating_spin = QSpinBox()
        self.rating_spin.setRange(1, 10)
        self.rating_spin.setValue(initial_rating if 1 <= initial_rating <= 10 else 5)
        self.rating_spin.setFixedWidth(60)
        self.rating_spin.setFixedHeight(25)
        self.rating_spin.setAlignment(Qt.AlignCenter)
        self.rating_spin.setStyleSheet("""
            QSpinBox {
                background-color: #ffffff;
                border: 1px solid #9bb89b;
                border-radius: 4px;
                color: #1e3a2e;
                font-size: 11px;
                font-weight: bold;
            }
            QSpinBox:hover {
                border-color: #6b8f6b;
            }
            QSpinBox::up-button {
                width: 16px;
                border-left: 1px solid #9bb89b;
                border-top-right-radius: 3px;
            }
            QSpinBox::down-button {
                width: 16px;
                border-left: 1px solid #9bb89b;
                border-bottom-right-radius: 3px;
            }
        """)
        self.rating_spin.valueChanged.connect(self.on_rating_changed)
        layout.addWidget(self.rating_spin)

    def on_rating_changed(self, rating):
        self.rating_changed.emit(self.player_id, rating)

    def get_rating(self):
        return self.rating_spin.value()

    def set_rating(self, rating):
        if 1 <= rating <= 10:
            self.rating_spin.setValue(rating)

    def setEnabled(self, enabled):
        super().setEnabled(enabled)
        self.rating_spin.setEnabled(enabled)


class PlayersRatingFrame(QFrame):
    players_loaded = Signal()

    def __init__(self, team_name="", db=None, parent=None):
        super().__init__(parent)
        self.team_name = team_name
        self.db = db
        self.players = []
        self.player_widgets = {}
        self.ratings = {}
        self._loading = False
        self.initUI()

    def initUI(self):
        self.setStyleSheet("""
            QFrame {
                background-color: #f8fff8;
                border: 1px solid #9bb89b;
                border-radius: 5px;
                margin-top: 2px;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(3)

        self.title_label = QLabel(f"Оценка игроков: {self.team_name}")
        self.title_label.setStyleSheet("""
            QLabel {
                color: #1e4a2e;
                font-size: 11px;
                font-weight: bold;
                padding: 3px;
                background-color: rgba(107, 143, 107, 0.15);
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.title_label)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMinimumHeight(80)
        self.scroll_area.setMaximumHeight(200)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet("""
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
            QScrollBar::handle:vertical:hover {
                background-color: #527352;
            }
        """)

        self.players_container = QWidget()
        self.players_container.setStyleSheet("background-color: transparent;")
        self.players_layout = QVBoxLayout(self.players_container)
        self.players_layout.setContentsMargins(3, 3, 3, 3)
        self.players_layout.setSpacing(2)
        self.players_layout.setAlignment(Qt.AlignTop)
        self.players_layout.addStretch()
        self.scroll_area.setWidget(self.players_container)
        layout.addWidget(self.scroll_area)

        self.reset_button = QPushButton("Сбросить оценки")
        self.reset_button.setFixedHeight(25)
        self.reset_button.setStyleSheet("""
            QPushButton {
                background-color: #8f9e8f;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 3px 8px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #748774;
            }
        """)
        self.reset_button.clicked.connect(self.reset_all_ratings)
        layout.addWidget(self.reset_button)
        self.setVisible(False)

    def set_team(self, team_name, db):
        self._loading = True
        self.team_name = team_name
        self.db = db
        self.title_label.setText(f"Оценка игроков: {team_name}")
        old_ratings = self.ratings.copy()
        self.load_players()
        if old_ratings:
            QTimer.singleShot(200, lambda: self.set_ratings(old_ratings))
        self._loading = False

    def load_players(self):
        self.clear_layout(self.players_layout)
        self.player_widgets.clear()

        if not self.db or not self.team_name:
            empty_label = QLabel("Выберите команду")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("color: #8f9e8f; padding: 10px; font-size: 10px;")
            self.players_layout.addWidget(empty_label)
            self.players_layout.addStretch()
            self.players_loaded.emit()
            return

        try:
            club = self.db.get_club_by_name(self.team_name)
            if not club:
                empty_label = QLabel(f"Команда не найдена")
                empty_label.setAlignment(Qt.AlignCenter)
                empty_label.setStyleSheet("color: #d46b6b; padding: 10px; font-size: 10px;")
                self.players_layout.addWidget(empty_label)
                self.players_layout.addStretch()
                self.players_loaded.emit()
                return

            self.players = self.db.get_players_by_club(club['id'])
            if not self.players:
                empty_label = QLabel(f"Нет игроков в команде")
                empty_label.setAlignment(Qt.AlignCenter)
                empty_label.setStyleSheet("color: #8f9e8f; padding: 10px; font-size: 10px; font-style: italic;")
                self.players_layout.addWidget(empty_label)
                self.players_layout.addStretch()
            else:
                for player in self.players:
                    initial_rating = self.ratings.get(player['id'], 5)
                    player_widget = PlayerRatingWidget(
                        player['id'],
                        f"{player['last_name']} {player['first_name']}",
                        initial_rating,
                        self
                    )
                    player_widget.rating_changed.connect(self.on_player_rating_changed)
                    self.players_layout.insertWidget(self.players_layout.count() - 1, player_widget)
                    self.player_widgets[player['id']] = player_widget
            self.players_loaded.emit()
        except Exception:
            empty_label = QLabel("Ошибка загрузки")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("color: #d46b6b; padding: 10px; font-size: 10px;")
            self.players_layout.addWidget(empty_label)
            self.players_layout.addStretch()
            self.players_loaded.emit()

    def on_player_rating_changed(self, player_id, rating):
        if not self._loading:
            self.ratings[player_id] = rating

    def reset_all_ratings(self):
        self.ratings.clear()
        for widget in self.player_widgets.values():
            widget.set_rating(5)
            self.ratings[widget.player_id] = 5

    def get_all_ratings(self):
        for player_id, widget in self.player_widgets.items():
            self.ratings[player_id] = widget.get_rating()
        return self.ratings.copy()

    def set_ratings(self, ratings):
        if not ratings:
            return
        self.ratings = ratings.copy()
        for player_id, rating in ratings.items():
            if player_id in self.player_widgets:
                self.player_widgets[player_id].set_rating(rating)

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def set_visible(self, visible):
        self.setVisible(visible)

    def setEnabled(self, enabled):
        super().setEnabled(enabled)
        self.reset_button.setEnabled(enabled)
        for widget in self.player_widgets.values():
            widget.setEnabled(enabled)


class CompleterLineEdit(QLineEdit):
    team_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._db = None
        self.completer = None
        self.all_clubs = []
        self.setPlaceholderText("Введите название команды")

    def set_db(self, db):
        self._db = db
        if db:
            self.load_all_clubs()

    def load_all_clubs(self):
        try:
            clubs = self._db.get_all_clubs_for_select()
            self.all_clubs = [club['name'] for club in clubs]
            self.setup_completer()
        except Exception:
            pass

    def setup_completer(self):
        if not self.all_clubs:
            return
        from PySide6.QtCore import QStringListModel
        self.model = QStringListModel()
        self.model.setStringList(self.all_clubs)
        from PySide6.QtWidgets import QCompleter
        self.completer = QCompleter()
        self.completer.setModel(self.model)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchContains)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.completer.setMaxVisibleItems(8)
        self.completer.popup().setStyleSheet("""
            QListView {
                background-color: #ffffff;
                border: 1px solid #9bb89b;
                border-radius: 3px;
                color: #000000;
                font-size: 11px;
                padding: 2px;
            }
            QListView::item {
                padding: 4px;
                border-radius: 2px;
            }
            QListView::item:hover {
                background-color: #e8f0e8;
            }
            QListView::item:selected {
                background-color: #6b8f6b;
                color: #ffffff;
            }
        """)
        self.setCompleter(self.completer)

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        if self.text().strip():
            self.team_changed.emit(self.text().strip())


class AddEventWindow(QDialog):
    event_saved = Signal()

    def __init__(self, parent=None, edit_mode=False, event_data=None):
        super().__init__(parent)
        self.edit_mode = edit_mode
        self.event_data = event_data
        self.event_id = event_data.get('id') if event_data else None
        self.user_id = None
        self.team1_ratings = {}
        self.team2_ratings = {}

        if edit_mode:
            self.setWindowTitle("Редактирование события")
        else:
            self.setWindowTitle("Новое событие")

        self.setFixedWidth(600)
        self.setMinimumHeight(650)
        self.setMaximumHeight(800)
        self.setModal(True)
        self.background_pixmap = None
        self.db = None
        self.user_data = None
        self.initUI()

        if edit_mode and event_data:
            QTimer.singleShot(100, self.fill_event_data)

    def initUI(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #e8f0e8;
            }
            QFrame#contentFrame {
                background-color: #f0f5f0;
                border: 1px solid #9bb89b;
                border-radius: 8px;
            }
            QLabel {
                color: #2c4c3b;
                font-size: 11px;
            }
            QLabel#titleLabel {
                color: #1e4a2e;
                font-size: 18px;
                font-weight: bold;
                padding: 5px 15px;
                background-color: rgba(150, 180, 150, 0.3);
                border-radius: 6px;
            }
            QLabel#fieldLabel {
                font-weight: bold;
                color: #2c4c3b;
                font-size: 11px;
                min-width: 80px;
            }
            QLineEdit, QTextEdit {
                background-color: #ffffff;
                border: 1px solid #9bb89b;
                border-radius: 4px;
                padding: 5px;
                color: #1e3a2e;
                font-size: 11px;
            }
            QLineEdit:focus, QTextEdit:focus {
                border-color: #6b8f6b;
                background-color: #f8fff8;
            }
            QLineEdit:disabled {
                background-color: #e0e8e0;
                border: 1px solid #c0d0c0;
                color: #8f9e8f;
            }
            QComboBox {
                background-color: #ffffff;
                border: 1px solid #9bb89b;
                border-radius: 4px;
                padding: 5px;
                color: #000000;
                font-size: 11px;
                min-width: 120px;
            }
            QComboBox:hover {
                border-color: #6b8f6b;
            }
            QComboBox::drop-down {
                width: 20px;
                border-left: 1px solid #9bb89b;
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
                background-color: #e8f0e8;
            }
            QComboBox::down-arrow {
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #527352;
                margin-right: 3px;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff !important;
                border: 1px solid #9bb89b !important;
                border-radius: 4px !important;
                selection-background-color: #6b8f6b !important;
                selection-color: #ffffff !important;
                color: #000000 !important;
                outline: none !important;
                padding: 2px !important;
            }
            QComboBox QAbstractItemView::item {
                padding: 4px !important;
                background-color: #ffffff !important;
                color: #000000 !important;
                min-height: 20px !important;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #e8f0e8 !important;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #6b8f6b !important;
                color: #ffffff !important;
            }
            QTextEdit {
                min-height: 50px;
                max-height: 50px;
            }
            QPushButton#closeButton {
                background-color: #8f9e8f;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 15px;
                font-weight: bold;
                font-size: 11px;
                min-width: 70px;
            }
            QPushButton#closeButton:hover {
                background-color: #748774;
            }
            QPushButton#actionButton {
                background-color: #6b8f6b;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 15px;
                font-weight: bold;
                font-size: 11px;
                min-width: 70px;
            }
            QPushButton#actionButton:hover {
                background-color: #527352;
            }
            QFrame#infoFrame {
                background-color: #ffffff;
                border: 1px solid #9bb89b;
                border-radius: 6px;
            }
            QFrame#scoreFrame {
                background-color: #f8fff8;
                border: 1px solid #9bb89b;
                border-radius: 6px;
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
        main_layout.setContentsMargins(15, 10, 15, 10)
        main_layout.setSpacing(5)

        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)
        if self.edit_mode:
            title_label = QLabel("Редактирование события")
        else:
            title_label = QLabel("Новое событие")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        top_layout.addWidget(title_label)
        main_layout.addLayout(top_layout)

        self.content_frame = QFrame()
        self.content_frame.setObjectName("contentFrame")
        self.content_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        content_layout = QVBoxLayout(self.content_frame)
        content_layout.setContentsMargins(10, 10, 10, 10)

        main_scroll = QScrollArea()
        main_scroll.setWidgetResizable(True)
        main_scroll.setFrameShape(QFrame.NoFrame)
        main_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(8)
        scroll_layout.setContentsMargins(0, 0, 0, 0)

        info_frame = QFrame()
        info_frame.setObjectName("infoFrame")
        info_layout = QVBoxLayout(info_frame)
        info_layout.setSpacing(8)
        info_layout.setContentsMargins(10, 10, 10, 10)

        team1_layout = QHBoxLayout()
        team1_layout.setSpacing(8)
        team1_label = QLabel("Команда 1:")
        team1_label.setObjectName("fieldLabel")
        team1_layout.addWidget(team1_label)
        self.team1_edit = CompleterLineEdit(self)
        self.team1_edit.setMinimumHeight(30)
        self.team1_edit.team_changed.connect(self.on_team1_changed)
        team1_layout.addWidget(self.team1_edit)
        info_layout.addLayout(team1_layout)

        self.team1_ratings_frame = PlayersRatingFrame(db=self.db, parent=self)
        info_layout.addWidget(self.team1_ratings_frame)

        team2_layout = QHBoxLayout()
        team2_layout.setSpacing(8)
        team2_label = QLabel("Команда 2:")
        team2_label.setObjectName("fieldLabel")
        team2_layout.addWidget(team2_label)
        self.team2_edit = CompleterLineEdit(self)
        self.team2_edit.setMinimumHeight(30)
        self.team2_edit.team_changed.connect(self.on_team2_changed)
        team2_layout.addWidget(self.team2_edit)
        info_layout.addLayout(team2_layout)

        self.team2_ratings_frame = PlayersRatingFrame(db=self.db, parent=self)
        info_layout.addWidget(self.team2_ratings_frame)

        score_frame = QFrame()
        score_frame.setObjectName("scoreFrame")
        score_layout = QHBoxLayout(score_frame)
        score_layout.setSpacing(8)
        score_layout.setContentsMargins(10, 5, 10, 5)

        score_label = QLabel("Счет:")
        score_label.setObjectName("fieldLabel")
        score_layout.addWidget(score_label)

        score_inputs = QHBoxLayout()
        score_inputs.setSpacing(3)
        self.score1_edit = QLineEdit()
        self.score1_edit.setPlaceholderText("0")
        self.score1_edit.setFixedWidth(45)
        self.score1_edit.setFixedHeight(28)
        self.score1_edit.setAlignment(Qt.AlignCenter)
        self.score1_edit.setValidator(QIntValidator(0, 99, self))
        score_inputs.addWidget(self.score1_edit)

        colon = QLabel(":")
        colon.setStyleSheet("font-size: 14px; font-weight: bold; background: transparent;")
        colon.setFixedWidth(8)
        score_inputs.addWidget(colon)

        self.score2_edit = QLineEdit()
        self.score2_edit.setPlaceholderText("0")
        self.score2_edit.setFixedWidth(45)
        self.score2_edit.setFixedHeight(28)
        self.score2_edit.setAlignment(Qt.AlignCenter)
        self.score2_edit.setValidator(QIntValidator(0, 99, self))
        score_inputs.addWidget(self.score2_edit)

        score_layout.addLayout(score_inputs)
        score_layout.addStretch()
        info_layout.addWidget(score_frame)

        status_layout = QHBoxLayout()
        status_layout.setSpacing(8)
        status_label = QLabel("Статус:")
        status_label.setObjectName("fieldLabel")
        status_layout.addWidget(status_label)

        self.status_combo = QComboBox()
        self.status_combo.addItems(["Запланирован", "Завершен"])
        self.status_combo.setMinimumHeight(28)
        self.status_combo.currentIndexChanged.connect(self.on_status_changed)
        self.status_combo.setStyleSheet("""
            QComboBox {
                background-color: #ffffff;
                border: 1px solid #9bb89b;
                border-radius: 4px;
                padding: 5px;
                color: #000000;
                font-size: 11px;
                min-width: 120px;
            }
            QComboBox:hover {
                border-color: #6b8f6b;
            }
            QComboBox::drop-down {
                width: 20px;
                border-left: 1px solid #9bb89b;
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
                background-color: #e8f0e8;
            }
            QComboBox::down-arrow {
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #527352;
                margin-right: 3px;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff !important;
                border: 1px solid #9bb89b !important;
                border-radius: 4px !important;
                selection-background-color: #6b8f6b !important;
                selection-color: #ffffff !important;
                color: #000000 !important;
                outline: none !important;
                padding: 2px !important;
            }
            QComboBox QAbstractItemView::item {
                padding: 4px !important;
                background-color: #ffffff !important;
                color: #000000 !important;
                min-height: 20px !important;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #e8f0e8 !important;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #6b8f6b !important;
                color: #ffffff !important;
            }
        """)
        status_layout.addWidget(self.status_combo)
        status_layout.addStretch()
        info_layout.addLayout(status_layout)

        scroll_layout.addWidget(info_frame)

        comment_label = QLabel("Комментарий:")
        comment_label.setObjectName("fieldLabel")
        comment_label.setContentsMargins(0, 5, 0, 0)

        self.comment_edit = QTextEdit()
        self.comment_edit.setPlaceholderText("Введите комментарий...")
        self.comment_edit.setMinimumHeight(45)
        self.comment_edit.setMaximumHeight(45)

        scroll_layout.addWidget(comment_label)
        scroll_layout.addWidget(self.comment_edit)

        main_scroll.setWidget(scroll_content)
        content_layout.addWidget(main_scroll)
        main_layout.addWidget(self.content_frame)

        buttons_widget = QWidget()
        buttons_widget.setMaximumHeight(40)
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setSpacing(10)
        buttons_layout.setContentsMargins(10, 0, 10, 5)

        self.close_button = QPushButton("Отмена")
        self.close_button.setObjectName("closeButton")
        self.close_button.clicked.connect(self.reject)

        if self.edit_mode:
            self.action_button = QPushButton("Сохранить изменения")
        else:
            self.action_button = QPushButton("Добавить событие")
        self.action_button.setObjectName("actionButton")
        self.action_button.clicked.connect(self.save_event)

        buttons_layout.addStretch()
        buttons_layout.addWidget(self.close_button)
        buttons_layout.addWidget(self.action_button)
        buttons_layout.addStretch()

        main_layout.addWidget(buttons_widget)
        self.setAutoFillBackground(True)

        self.score1_edit.setText("0")
        self.score2_edit.setText("0")
        self.on_status_changed(0)

    def on_team1_changed(self, team_name):
        if team_name and self.db:
            current_ratings = self.team1_ratings_frame.get_all_ratings()
            if current_ratings:
                self.team1_ratings = current_ratings
            self.team1_ratings_frame.set_team(team_name, self.db)
            self.team1_ratings_frame.set_visible(True)
            if self.team1_ratings:
                QTimer.singleShot(100, lambda: self.team1_ratings_frame.set_ratings(self.team1_ratings))
        else:
            self.team1_ratings_frame.set_visible(False)

    def on_team2_changed(self, team_name):
        if team_name and self.db:
            current_ratings = self.team2_ratings_frame.get_all_ratings()
            if current_ratings:
                self.team2_ratings = current_ratings
            self.team2_ratings_frame.set_team(team_name, self.db)
            self.team2_ratings_frame.set_visible(True)
            if self.team2_ratings:
                QTimer.singleShot(100, lambda: self.team2_ratings_frame.set_ratings(self.team2_ratings))
        else:
            self.team2_ratings_frame.set_visible(False)

    def fill_event_data(self):
        if not self.event_data:
            return
        self.team1_edit.setText(self.event_data.get('team1', ''))
        self.team2_edit.setText(self.event_data.get('team2', ''))
        score1 = self.event_data.get('score1', 0)
        score2 = self.event_data.get('score2', 0)
        self.score1_edit.setText(str(score1))
        self.score2_edit.setText(str(score2))
        status = self.event_data.get('status', 'Запланирован')
        index = self.status_combo.findText(status)
        if index >= 0:
            self.status_combo.setCurrentIndex(index)
        comment = self.event_data.get('comment', '')
        self.comment_edit.setPlainText(comment)
        if self.event_data.get('team1'):
            self.team1_edit.team_changed.emit(self.event_data.get('team1'))
        if self.event_data.get('team2'):
            self.team2_edit.team_changed.emit(self.event_data.get('team2'))
        QTimer.singleShot(300, self.load_player_ratings)

    def load_player_ratings(self):
        if not self.event_id or not self.user_id:
            return
        ratings = load_event_ratings_from_json(self.user_id, self.event_id)
        if ratings:
            team1_player_ids = {p['id'] for p in self.team1_ratings_frame.players}
            team2_player_ids = {p['id'] for p in self.team2_ratings_frame.players}
            team1_ratings = {}
            team2_ratings = {}
            for player_id, rating in ratings.items():
                if player_id in team1_player_ids:
                    team1_ratings[player_id] = rating
                elif player_id in team2_player_ids:
                    team2_ratings[player_id] = rating
            self.team1_ratings = team1_ratings
            self.team2_ratings = team2_ratings
            if team1_ratings:
                self.team1_ratings_frame.set_ratings(team1_ratings)
            if team2_ratings:
                self.team2_ratings_frame.set_ratings(team2_ratings)

        is_planned = (self.status_combo.currentIndex() == 0)
        self.team1_ratings_frame.setEnabled(not is_planned)
        self.team2_ratings_frame.setEnabled(not is_planned)

    def set_database(self, db):
        self.db = db
        if hasattr(self, 'team1_edit'):
            self.team1_edit.set_db(db)
        if hasattr(self, 'team2_edit'):
            self.team2_edit.set_db(db)
        if hasattr(self, 'team1_ratings_frame'):
            self.team1_ratings_frame.db = db
        if hasattr(self, 'team2_ratings_frame'):
            self.team2_ratings_frame.db = db

    def set_user_data(self, user_data):
        self.user_data = user_data
        self.user_id = user_data.get('id') if user_data else None

    def on_status_changed(self, index):
        is_planned = (index == 0)
        self.score1_edit.setDisabled(is_planned)
        self.score2_edit.setDisabled(is_planned)
        self.team1_ratings_frame.setEnabled(not is_planned)
        self.team2_ratings_frame.setEnabled(not is_planned)

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
                    border: 1px solid rgba(155, 184, 155, 160);
                    border-radius: 8px;
                }
            """)
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

    def save_event(self):
        team1_input = self.team1_edit.text().strip()
        team2_input = self.team2_edit.text().strip()

        if not team1_input or not team2_input:
            self.show_warning("Пожалуйста, заполните названия обеих команд")
            return

        if team1_input == team2_input:
            self.show_warning("Команды не могут быть одинаковыми")
            return

        if not self.db:
            self.show_error("Нет подключения к базе данных")
            return

        team1_data = self.db.get_club_by_name(team1_input)
        team2_data = self.db.get_club_by_name(team2_input)

        if team1_data is None:
            self.show_warning(f"Команда '{team1_input}' не найдена в базе данных.")
            return

        if team2_data is None:
            self.show_warning(f"Команда '{team2_input}' не найдена в базе данных.")
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

        all_ratings = {}
        if status == "Завершен":
            team1_ratings = self.team1_ratings_frame.get_all_ratings()
            team2_ratings = self.team2_ratings_frame.get_all_ratings()
            all_ratings = {**team1_ratings, **team2_ratings}

        saved_to_db = False
        awarded_achievements = []

        if self.db and self.user_data and self.user_data.get('id'):
            try:
                if self.edit_mode and self.event_id:
                    success, message = self.db.update_event(
                        event_id=self.event_id,
                        team1_name=team1,
                        team2_name=team2,
                        score1=score1,
                        score2=score2,
                        status=status,
                        comment=comment
                    )
                    if success:
                        if all_ratings and self.user_id:
                            save_event_ratings_to_json(self.user_id, self.event_id, all_ratings)
                        saved_to_db = True
                else:
                    success, event_id, message = self.db.add_event(
                        user_id=self.user_data['id'],
                        team1_name=team1,
                        team2_name=team2,
                        score1=score1,
                        score2=score2,
                        status=status,
                        comment=comment
                    )
                    if success:
                        self.event_id = event_id
                        if all_ratings and self.user_id:
                            save_event_ratings_to_json(self.user_id, event_id, all_ratings)
                        saved_to_db = True
            except Exception:
                pass

        if saved_to_db and self.db and self.user_data:
            awarded_achievements = self.db.check_and_award_achievements(self.user_data['id'])

        self.show_success(saved_to_db, awarded_achievements)
        self.event_saved.emit()
        self.accept()

    def show_warning(self, text):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Предупреждение")
        msg_box.setText(text)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.exec()

    def show_error(self, text):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Ошибка")
        msg_box.setText(text)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.exec()

    def show_success(self, saved_to_db, awarded_achievements):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Успех")

        if saved_to_db:
            if self.edit_mode:
                msg_text = "Событие успешно обновлено!"
            else:
                msg_text = "Событие успешно добавлено!"

            if awarded_achievements:
                msg_text += "\n\n🏆 ВЫ ПОЛУЧИЛИ НОВЫЕ ДОСТИЖЕНИЯ! 🏆\n\n"
                for ach in awarded_achievements:
                    msg_text += f"⭐ {ach['name']}\n   {ach['description']}\n\n"
                msg_text += "Посмотрите их в своем профиле!"

            msg_box.setText(msg_text)
        else:
            msg_box.setText("Ошибка при сохранении события!")

        msg_box.setIcon(QMessageBox.Information)
        ok_button = msg_box.addButton("ОК", QMessageBox.AcceptRole)
        ok_button.setStyleSheet("""
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
        msg_box.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AddEventWindow()
    window.show()
    sys.exit(app.exec())