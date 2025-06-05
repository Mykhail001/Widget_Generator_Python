"""
Простий тест для перевірки PyQt6
"""
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton


class TestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Тест PyQt6")
        self.setGeometry(300, 300, 400, 200)

        layout = QVBoxLayout()

        label = QLabel("Це тестове вікно PyQt6")
        button = QPushButton("Тестова кнопка")

        layout.addWidget(label)
        layout.addWidget(button)

        self.setLayout(layout)


def main():
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()