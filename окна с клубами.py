import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTreeWidget, QTreeWidgetItem,
    QMessageBox
)
from PyQt6.QtCore import Qt


class ClubsWindow(QWidget):
    def __init__(self, is_admin=False):
        super().__init__()
        self.is_admin = is_admin
        self.setWindowTitle("Список клубов")
        self.setMinimumSize(900, 600)

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Заголовок
        title = QLabel("Футбольные лиги")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        main_layout.addWidget(title)

        # Дерево лиг и клубов
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        main_layout.addWidget(self.tree)

        # Заполнение тестовыми данными (в дальнейшем заменить на данные из БД)
        self.load_data()

        # Кнопки администратора
        if self.is_admin:
            buttons_layout = QHBoxLayout()

            self.add_button = QPushButton("Добавить клуб")
            self.add_button.clicked.connect(self.add_club)

            self.delete_button = QPushButton("Удалить клуб")
            self.delete_button.clicked.connect(self.delete_club)

            buttons_layout.addWidget(self.add_button)
            buttons_layout.addWidget(self.delete_button)

            main_layout.addLayout(buttons_layout)

        # Кнопка назад
        self.back_button = QPushButton("Назад")
        self.back_button.clicked.connect(self.close)
        main_layout.addWidget(self.back_button)

        self.setLayout(main_layout)

    def load_data(self):
        leagues = {
            "РПЛ": ["Зенит", "Спартак", "ЦСКА"],
            "АПЛ": ["Манчестер Сити", "Арсенал", "Ливерпуль"],
            "Ла Лига": ["Барселона", "Реал Мадрид", "Атлетико"]
        }

        for league, clubs in leagues.items():
            league_item = QTreeWidgetItem([league])
            self.tree.addTopLevelItem(league_item)

            for club in clubs:
                club_item = QTreeWidgetItem([club])
                league_item.addChild(club_item)

    def add_club(self):
        QMessageBox.information(self, "Добавление", "Открыть окно добавления клуба")

    def delete_club(self):
        selected_item = self.tree.currentItem()
        if selected_item and selected_item.parent():
            selected_item.parent().removeChild(selected_item)
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите клуб для удаления")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Передать True, если пользователь администратор
    window = ClubsWindow(is_admin=True)
    window.show()

    sys.exit(app.exec())