"""
Головний файл запуску Minecraft Button Generator v2.0
"""
import sys
import os
from PyQt6.QtWidgets import QApplication

from widgets.button_generator import ButtonGenerator

def main():
    """Головна функція запуску програми"""
    app = QApplication(sys.argv)

    try:
        # Діагностичний вивід
        print("Створюємо ButtonGenerator...")
        generator = ButtonGenerator()
        print(f"ButtonGenerator створений: {type(generator)}")

        # Встановлюємо мінімальний розмір
        generator.resize(800, 600)
        generator.setWindowTitle("Minecraft Button Generator v2.0")

        print("Показуємо вікно...")
        generator.show()
        print("Вікно показано!")

        # Запускаємо програму
        sys.exit(app.exec())

    except Exception as e:
        print(f"Помилка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":  # Виправлено: подвійні підкреслення замість зірочок
    main()