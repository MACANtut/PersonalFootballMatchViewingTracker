from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QLineEdit, QFileDialog, QMessageBox)
from PySide6.QtCore import Qt

class BackgroundDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_file = None
        self.setWindowTitle("Персонализация фона")
        self.setFixedSize(450, 200)
        self.setModal(True)
        
        # Устанавливаем стиль в светлой теме
        self.setStyleSheet("""
            QDialog {
                background-color: #e8f0e8;
            }
            QLabel {
                color: #2c4c3b;
                font-weight: bold;
                font-size: 12px;
            }
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
            QLineEdit:read-only {
                background-color: #f0f5f0;
            }
            QPushButton {
                background-color: #6b8f6b;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
                font-size: 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #527352;
            }
            QPushButton:pressed {
                background-color: #3e5a3e;
            }
            QPushButton#cancelButton {
                background-color: #8f9e8f;
            }
            QPushButton#cancelButton:hover {
                background-color: #748774;
            }
            QPushButton#applyButton {
                background-color: #6b8f6b;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 20, 30, 20)
        
        # Заголовок
        title = QLabel("Персонализация фона")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 16px; 
            font-weight: bold; 
            padding: 10px;
            color: #1e4a2e;
            background-color: rgba(150, 180, 150, 0.3);
            border-radius: 8px;
        """)
        layout.addWidget(title)
        
        # Строка выбора файла
        file_layout = QHBoxLayout()
        file_layout.setSpacing(10)
        
        file_label = QLabel("Изображение:")
        file_label.setFixedWidth(80)
        file_layout.addWidget(file_label)
        
        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        self.path_edit.setPlaceholderText("выберите изображение для фона")
        file_layout.addWidget(self.path_edit)
        
        browse_btn = QPushButton("Обзор...")
        browse_btn.setFixedWidth(80)
        browse_btn.clicked.connect(self.browse)
        file_layout.addWidget(browse_btn)
        
        layout.addLayout(file_layout)
        layout.addStretch()
        
        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Отмена")
        cancel_btn.setObjectName("cancelButton")
        cancel_btn.setFixedWidth(100)
        cancel_btn.clicked.connect(self.reject)
        
        apply_btn = QPushButton("Применить")
        apply_btn.setObjectName("applyButton")
        apply_btn.setFixedWidth(100)
        apply_btn.clicked.connect(self.apply)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(apply_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def browse(self):
        file, _ = QFileDialog.getOpenFileName(
            self, 
            "Выберите изображение", 
            "", 
            "Изображения (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file:
            self.selected_file = file
            self.path_edit.setText(file)
    
    def apply(self):
        if self.selected_file:
            self.accept()
        else:
            # Стилизованное сообщение об ошибке
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Ошибка")
            msg_box.setText("Выберите изображение для фона")
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
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #527352;
                }
                QPushButton:pressed {
                    background-color: #3e5a3e;
                }
            """)
            ok_button = msg_box.addButton("ОК", QMessageBox.AcceptRole)
            msg_box.exec_()