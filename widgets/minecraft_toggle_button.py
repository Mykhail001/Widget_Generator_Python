"""
Minecraft-стильний перемикач (toggle switch)
"""
from PyQt6.QtWidgets import QFrame
from PyQt6.QtCore import Qt, pyqtSignal

from managers import TogglePatternManager
from .minecraft_button import MinecraftButton

class MinecraftToggleButton(QFrame):
    """
    Перемикач (toggle switch) в стилі Minecraft
    """
    clicked = pyqtSignal()
    stateChanged = pyqtSignal(bool)  # True коли увімкнено

    def __init__(self, style_config=None, parent=None):
        super().__init__(parent)

        # Дефолтна конфігурація для перемикача (без тексту)
        self.default_config = {
            'scale': 8,
            'border_color': '#413F54',  # (65, 63, 84)
            'left_area_color': '#9CD3FF',  # Ліва частина
            'right_area_color': '#696D88',  # Права частина
            'button_normal': '#9A9FB4',
            'button_pressed': '#9CD3FF',
            'border_normal': '#ADB0C4',
            'border_pressed': '#DAFFFF',
            'bottom_normal': '#9A9FB4',
            'bottom_pressed': '#708CBA'
        }

        # Застосовуємо користувацьку конфігурацію
        self.config = self.default_config.copy()
        if style_config:
            self.config.update(style_config)

        self.toggled = False  # Стан перемикача
        self.hover_state = False  # Стан наведення миші
        self.hover_active = True  # Чи активний hover ефект (скидається після натискання)
        self.pattern_name = 'Standard'  # Стандартний патерн за замовчуванням
        self.pattern_pixels = []  # Список QFrame елементів для патерну
        self.setup_toggle()

    def setup_toggle(self):
        """Налаштування перемикача"""
        self.scale = self.config['scale']

        # Розміри: 20x9 + бордери (1+1)x(1+1) = 22x13 (зменшили ширину на 2, висоту на 2)
        # Додаємо додатковий простір зверху для рухомої кнопки
        self.toggle_width = 22 * self.scale  # було 24
        self.toggle_height = 13 * self.scale  # було 15

        self.setFixedSize(self.toggle_width, self.toggle_height)

        # Створюємо елементи
        self.create_toggle_borders()
        self.create_toggle_areas()
        self.create_pattern()  # Створюємо патерн перед рухомою кнопкою
        self.create_moving_button()
        self.update_toggle_styles()

    def create_toggle_borders(self):
        """Створення бордерів перемикача"""
        border_color = self.config['border_color']

        # Зсунуто вниз на 2 пікселі для місця під рухому кнопку
        # Верхній бордер
        self.top_border = QFrame(self)
        self.top_border.setGeometry(0, 2 * self.scale, self.toggle_width, self.scale)
        self.top_border.setStyleSheet(f"background-color: {border_color}; border-radius: 0px;")

        # Лівий бордер (висота 9 пікселів - зменшено на 2)
        self.left_border = QFrame(self)
        self.left_border.setGeometry(0, 3 * self.scale, self.scale, 9 * self.scale)
        self.left_border.setStyleSheet(f"background-color: {border_color}; border-radius: 0px;")

        # Правий бордер (позиція 21 - зменшено на 2)
        self.right_border = QFrame(self)
        self.right_border.setGeometry(21 * self.scale, 3 * self.scale, self.scale, 9 * self.scale)
        self.right_border.setStyleSheet(f"background-color: {border_color}; border-radius: 0px;")

        # Нижній бордер (позиція 12 - зменшено на 2)
        self.bottom_border = QFrame(self)
        self.bottom_border.setGeometry(0, 12 * self.scale, self.toggle_width, self.scale)
        self.bottom_border.setStyleSheet(f"background-color: {border_color}; border-radius: 0px;")

    def create_toggle_areas(self):
        """Створення лівої та правої областей"""
        # Зсунуто вниз на 2 пікселі для місця під рухому кнопку
        # Ліва область (11x9) - висота зменшена на 2
        self.left_area = QFrame(self)
        self.left_area.setGeometry(self.scale, 3 * self.scale, 11 * self.scale, 9 * self.scale)
        self.left_area.setStyleSheet(f"background-color: {self.config['left_area_color']}; border-radius: 0px;")

        # Права область (9x9) - ширина та висота зменшені на 2
        self.right_area = QFrame(self)
        self.right_area.setGeometry(12 * self.scale, 3 * self.scale, 9 * self.scale, 9 * self.scale)
        self.right_area.setStyleSheet(f"background-color: {self.config['right_area_color']}; border-radius: 0px;")

    def create_pattern(self):
        """Створення патерну на підложці"""
        self.clear_pattern()  # Очищаємо попередній патерн

        patterns = TogglePatternManager.get_patterns()
        colors = TogglePatternManager.get_pattern_colors()

        if self.pattern_name not in patterns or patterns[self.pattern_name] is None:
            return  # Немає патерну

        pattern_data = patterns[self.pattern_name]

        # Створюємо пікселі патерну (18x7 всередині областей - зменшено на 2x2)
        max_rows = min(7, len(pattern_data))  # Максимум 7 рядків
        for row_idx in range(max_rows):
            row = pattern_data[row_idx]
            max_cols = min(18, len(row))  # Максимум 18 колонок
            for col_idx in range(max_cols):
                symbol = row[col_idx]
                if symbol != '0':  # Не прозорий піксель
                    color = colors.get(symbol)
                    if color:
                        # Позиція пікселя (зсунуто вниз на 3 для бордерів)
                        pixel_x = (1 + col_idx) * self.scale  # +1 для лівого бордера
                        pixel_y = (3 + row_idx) * self.scale  # +3 для верхнього бордера

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
        # Переконуємося, що рухома кнопка залишається зверху
        if hasattr(self, 'moving_button'):
            self.moving_button.raise_()

    def create_moving_button(self):
        """Створення рухомої кнопки як справжнього MinecraftButton"""
        # Конфігурація для рухомої кнопки (10x8 - зменшили висоту на 2)
        button_config = {
            'button_width': 10,  # Ширина головної частини
            'button_height': 8,  # Висота головної частини (було 10, тепер 8)
            'scale': self.scale,
            'border_color': '#413F54',  # Темний бордер
            'button_normal': '#9A9FB4',  # Світліший колір для видимості
            'button_hover': '#9A9FB4',   # Без hover ефекту
            'button_pressed': '#9A9FB4', # Без pressed ефекту
            'border_normal': '#ADB0C4',  # Світлий бордер для контрасту
            'border_hover': '#ADB0C4',   # Без hover ефекту
            'border_pressed': '#ADB0C4', # Без pressed ефекту
            'bottom_normal': '#9A9FB4',  # Тінь
            'bottom_hover': '#9A9FB4',   # Без hover ефекту
            'bottom_pressed': '#9A9FB4', # Без pressed ефекту
            'text_color': 'white',
            'font_family': 'Minecraftia',
            'has_shadow': True,
            'animation_enabled': False  # Відключаємо анімацію натискання
        }

        # Створюємо справжню Minecraft кнопку
        self.moving_button = MinecraftButton('', button_config, self)

        # Переконуємося, що кнопка видима
        self.moving_button.show()
        self.moving_button.raise_()  # Піднімаємо на передній план

        # Початкова позиція (вимкнено - зліва)
        self.update_button_position()

    def mousePressEvent(self, event):
        """Обробка натискання"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Скидаємо hover ефект після натискання
            self.hover_active = False
            self.toggle_state()
        super().mousePressEvent(event)

    def enterEvent(self, event):
        """Обробка наведення миші"""
        self.hover_state = True
        self.update_button_position()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Обробка виходу миші"""
        self.hover_state = False
        # Відновлюємо можливість hover ефекту при наступному наведенні
        self.hover_active = True
        self.update_button_position()
        super().leaveEvent(event)

    def toggle_state(self):
        """Перемикання стану"""
        self.toggled = not self.toggled
        self.update_button_position()
        self.update_toggle_styles()
        self.clicked.emit()
        self.stateChanged.emit(self.toggled)

    def set_toggled(self, toggled):
        """Встановлення стану програмно"""
        if self.toggled != toggled:
            self.toggled = toggled
            self.update_button_position()
            self.update_toggle_styles()
            self.stateChanged.emit(self.toggled)

    def is_toggled(self):
        """Повертає стан перемикача"""
        return self.toggled

    def update_button_position(self):
        """Оновлення позиції рухомої кнопки"""
        base_x = 0  # Базова позиція

        if self.toggled:
            # Увімкнено - справа (зменшено на 2 через зменшення ширини підложки)
            base_x = 10 * self.scale  # було 12, тепер 10
            if self.hover_state and self.hover_active:
                # При наведенні зміщуємо вліво на 2 пікселі (тільки якщо hover активний)
                button_x = base_x - 2 * self.scale
            else:
                button_x = base_x
        else:
            # Вимкнено - зліва
            base_x = 0 * self.scale
            if self.hover_state and self.hover_active:
                # При наведенні зміщуємо вправо на 2 пікселі (тільки якщо hover активний)
                button_x = base_x + 2 * self.scale
            else:
                button_x = base_x

        button_y = 1 * self.scale  # Тепер у зарезервованому просторі зверху
        self.moving_button.move(button_x, button_y)

        # Додаткові перевірки для видимості
        self.moving_button.show()
        self.moving_button.raise_()

    def update_toggle_styles(self):
        """Оновлення стилів перемикача"""
        # Кнопка завжди має однаковий колір незалежно від стану перемикача
        self.moving_button.config.update({
            'button_normal': self.config['button_normal'],
            'button_hover': self.config['button_normal'],
            'button_pressed': self.config['button_normal'],
            'border_normal': self.config['border_normal'],
            'border_hover': self.config['border_normal'],
            'border_pressed': self.config['border_normal'],
            'bottom_normal': self.config['bottom_normal'],
            'bottom_hover': self.config['bottom_normal'],
            'bottom_pressed': self.config['bottom_normal'],
            # Переконуємося, що бордери завжди мають правильний колір
            'border_color': '#413F54'
        })

        # Принудительно встановлюємо стан hover=False, pressed=False
        self.moving_button.hover_state = False
        self.moving_button.pressed_state = False

        # Застосовуємо оновлені стилі до кнопки
        self.moving_button.update_styles()
        # Верхня частина має колір заднього фону, а не бордера
        self.setStyleSheet(f"background-color: #CBCCD4; border-radius: 0px;")
