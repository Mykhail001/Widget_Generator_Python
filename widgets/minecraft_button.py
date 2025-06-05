"""
Minecraft-стильна кнопка з підтримкою патернів
"""
from PyQt6.QtWidgets import QFrame, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from managers import ButtonPatternManager


class MinecraftButton(QFrame):
    """
    Базовий клас для Minecraft-стильних кнопок з можливістю кастомізації
    Підтримує:
    - Налаштування розмірів головної частини
    - Анімації натискання
    - Кольорові схеми
    - Пропорційне масштабування
    - Патерни кнопок
    """
    clicked = pyqtSignal()
    def __init__(self, text="", style_config=None, parent=None):
        super().__init__(parent)

        # Дефолтна конфігурація стилю
        self.default_config = {
            'button_width': 16,  # Ширина головної частини в пропорційних пікселях
            'button_height': 15, # Висота головної частини в пропорційних пікселях
            'scale': 8,
            'border_color': '#413F54',
            'button_normal': '#9A9FB4',
            'button_hover': '#9CD3FF',
            'button_pressed': '#9CD3FF',
            'border_normal': '#ADB0C4',
            'border_hover': '#DAFFFF',
            'border_pressed': '#DAFFFF',
            'bottom_normal': '#9A9FB4',
            'bottom_hover': '#708CBA',
            'bottom_pressed': '#708CBA',
            'text_color': 'white',
            'font_family': 'Minecraftia',
            'has_shadow': True,
            'animation_enabled': True
        }
        # Застосовуємо користувацьку конфігурацію
        self.config = self.default_config.copy()
        if style_config:
            self.config.update(style_config)

        # Змінні для патернів
        self.pattern_name = 'None'  # Назва поточного патерну
        self.pattern_pixels = []    # Список QFrame елементів для патерну

        self.setup_button()

    def setup_button(self):
        """Налаштування кнопки на основі конфігурації"""
        self.scale = self.config['scale']

        # Розрахунок розмірів на основі головної частини
        button_width = self.config['button_width']  # пропорційні пікселі
        button_height = self.config['button_height']  # пропорційні пікселі

        # Загальні розміри: бордери (1+1) + головна частина + нижній простір (2)
        self.base_width = (button_width + 2) * self.scale  # +2 для лівого та правого бордерів
        self.base_height = (1 + button_height + 2 + 1) * self.scale  # верх + кнопка + простір + низ
        self.setFixedSize(self.base_width, self.base_height)
        self.pressed_state = False
        self.hover_state = False

        # Створюємо всі елементи кнопки
        self.create_borders()
        self.create_main_button()
        self.create_pattern()  # Створюємо патерн після основної кнопки
        self.create_bottom_space()
        self.update_styles()

    def create_borders(self):
        """Створення бордерів кнопки"""
        border_color = self.config['border_color']
        button_width = self.config['button_width']
        button_height = self.config['button_height']

        # Верхній бордер
        self.top_border = QFrame(self)
        self.top_border.setGeometry(0, 0, self.base_width, self.scale)
        self.top_border.setStyleSheet(f"background-color: {border_color}; border-radius: 0px;")

        # Лівий бордер
        self.left_border = QFrame(self)
        self.left_border.setGeometry(0, self.scale, self.scale, (button_height + 2) * self.scale)
        self.left_border.setStyleSheet(f"background-color: {border_color}; border-radius: 0px;")
        # Правий бордер
        self.right_border = QFrame(self)
        self.right_border.setGeometry((button_width + 1) * self.scale, self.scale, self.scale, (button_height + 2) * self.scale)
        self.right_border.setStyleSheet(f"background-color: {border_color}; border-radius: 0px;")
        # Нижній бордер
        self.bottom_border = QFrame(self)
        self.bottom_border.setGeometry(0, self.base_height - self.scale, self.base_width, self.scale)
        self.bottom_border.setStyleSheet(f"background-color: {border_color}; border-radius: 0px;")

    def create_main_button(self):
        """Створення основної кнопки"""
        button_width = self.config['button_width']
        button_height = self.config['button_height']

        self.button = QPushButton('', self)  # Завжди без тексту
        self.button.setGeometry(self.scale, self.scale, button_width * self.scale, button_height * self.scale)

        # Налаштування шрифту
        font = QFont(self.config['font_family'], 16)  # Фіксований розмір
        self.button.setFont(font)

        # Відключаємо mouse events на кнопці
        self.button.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def create_pattern(self):
        """Створення патерну на кнопці"""
        self.clear_pattern()  # Очищаємо попередній патерн

        patterns = ButtonPatternManager.get_patterns()
        colors = ButtonPatternManager.get_pattern_colors()

        if self.pattern_name not in patterns or patterns[self.pattern_name] is None:
            return  # Немає патерну

        pattern_data = patterns[self.pattern_name]
        button_width = self.config['button_width']
        button_height = self.config['button_height']

        # Створюємо пікселі патерну всередині кнопки (починаємо після бордера)
        max_rows = min(button_height, len(pattern_data))  # Обмежуємо висотою кнопки
        for row_idx in range(max_rows):
            row = pattern_data[row_idx]
            max_cols = min(button_width, len(row))  # Обмежуємо шириною кнопки
            for col_idx in range(max_cols):
                symbol = row[col_idx]
                if symbol != '0':  # Не прозорий піксель
                    color = colors.get(symbol)
                    if color:
                        # Позиція пікселя (починаємо після лівого та верхнього бордерів)
                        pixel_x = (1 + col_idx) * self.scale  # +1 для лівого бордера
                        pixel_y = (1 + row_idx) * self.scale  # +1 для верхнього бордера

                        pixel = QFrame(self)
                        pixel.setGeometry(pixel_x, pixel_y, self.scale, self.scale)
                        pixel.setStyleSheet(f"background-color: {color}; border: none;")
                        pixel.show()

                        self.pattern_pixels.append(pixel)

    def clear_pattern(self):
        """Очищення попереднього патерну"""
        for pixel in self.pattern_pixels:
            pixel.deleteLater()
        self.pattern_pixels.clear()

    def set_pattern(self, pattern_name):
        """Встановлення нового патерну"""
        self.pattern_name = pattern_name
        self.create_pattern()

    def update_pattern_position(self, offset_y=0):
        """Оновлення позиції патерну (для анімації натискання)"""
        if not self.pattern_pixels:
            return

        # Перерахунок позицій всіх пікселів патерну
        patterns = ButtonPatternManager.get_patterns()
        if self.pattern_name not in patterns or patterns[self.pattern_name] is None:
            return

        pattern_data = patterns[self.pattern_name]
        button_width = self.config['button_width']
        button_height = self.config['button_height']

        pixel_index = 0
        max_rows = min(button_height, len(pattern_data))
        for row_idx in range(max_rows):
            row = pattern_data[row_idx]
            max_cols = min(button_width, len(row))
            for col_idx in range(max_cols):
                symbol = row[col_idx]
                if symbol != '0' and pixel_index < len(self.pattern_pixels):
                    # Нова позиція з урахуванням зміщення
                    pixel_x = (1 + col_idx) * self.scale
                    pixel_y = (1 + row_idx + offset_y) * self.scale

                    self.pattern_pixels[pixel_index].setGeometry(pixel_x, pixel_y, self.scale, self.scale)
                    pixel_index += 1

    def create_bottom_space(self):
        """Створення нижнього простору (тінь)"""
        button_width = self.config['button_width']
        button_height = self.config['button_height']

        self.bottom_space = QFrame(self)
        self.bottom_space.setGeometry(self.scale, (1 + button_height) * self.scale, button_width * self.scale, 2 * self.scale)

    def mousePressEvent(self, event):
        """Обробка натискання миші"""
        if event.button() == Qt.MouseButton.LeftButton and self.config['animation_enabled']:
            self.on_pressed()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Обробка відпускання миші"""
        if event.button() == Qt.MouseButton.LeftButton:
            if self.config['animation_enabled']:
                self.on_released()
            if self.rect().contains(event.pos()):
                self.clicked.emit()
        super().mouseReleaseEvent(event)

    def enterEvent(self, event):
        """Обробка наведення миші"""
        self.hover_state = True
        self.update_styles()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Обробка виходу миші"""
        self.hover_state = False
        self.update_styles()
        super().leaveEvent(event)

    def on_pressed(self):
        """Анімація натискання"""
        self.pressed_state = True
        button_width = self.config['button_width']
        button_height = self.config['button_height']
        # Кнопка зміщується вниз на 1 пропорційний піксель
        self.button.setGeometry(self.scale, 2 * self.scale, button_width * self.scale, button_height * self.scale)
        # Bottom space зменшується на 1 пропорційний піксель
        self.bottom_space.setGeometry(self.scale, (2 + button_height) * self.scale, button_width * self.scale, self.scale)
        # Патерн також зміщується вниз
        self.update_pattern_position(offset_y=1)
        # Make top border match background color
        self.top_border.setStyleSheet("background-color: #CBCCD4; border-radius: 0px;")
        self.update_styles()

    def on_released(self):
        """Відновлення після натискання"""
        self.pressed_state = False
        button_width = self.config['button_width']
        button_height = self.config['button_height']

        # Повертаємо кнопку і простір до нормального стану
        self.button.setGeometry(self.scale, self.scale, button_width * self.scale, button_height * self.scale)
        self.bottom_space.setGeometry(self.scale, (1 + button_height) * self.scale, button_width * self.scale, 2 * self.scale)
        # Повертаємо патерн до нормальної позиції
        self.update_pattern_position(offset_y=0)

        # Restore top border color
        self.top_border.setStyleSheet(f"background-color: {self.config['border_color']}; border-radius: 0px;")
        self.update_styles()

    def update_styles(self):
        """Оновлення стилів на основі стану"""
        if self.pressed_state:
            button_bg = self.config['button_pressed']
            border_color = self.config['border_pressed']
            bottom_color = self.config['bottom_pressed']
        elif self.hover_state:
            button_bg = self.config['button_hover']
            border_color = self.config['border_hover']
            bottom_color = self.config['bottom_hover']
        else:
            button_bg = self.config['button_normal']
            border_color = self.config['border_normal']
            bottom_color = self.config['bottom_normal']

        # Стилі кнопки
        button_style = f"""
        QPushButton {{
            border: {self.scale}px solid {border_color};
            background-color: {button_bg};
            color: {self.config['text_color']};
            padding: 0px;
            margin: 0px;
            border-radius: 0px;
        }}
        """

        bottom_style = f"""QFrame {{ 
            background-color: {bottom_color}; 
            border: none; 
            border-radius: 0px;
        }}"""

        self.button.setStyleSheet(button_style)
        self.bottom_space.setStyleSheet(bottom_style)
        self.setStyleSheet(f"background-color: {self.config['border_color']}; border-radius: 0px;")
