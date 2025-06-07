"""
Minecraft-стильне текстове поле (Entry)
"""
from PyQt6.QtWidgets import QFrame, QLineEdit
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

class MinecraftEntry(QFrame):
    """
    Текстове поле в стилі Minecraft
    Розмір: 50x10 пропорційних пікселів, текст займає повну висоту
    """
    textChanged = pyqtSignal(str)
    returnPressed = pyqtSignal()

    def __init__(self, placeholder="", style_config=None, parent=None):
        super().__init__(parent)

        # Дефолтна конфігурація для Entry
        self.default_config = {
            'entry_width': 60,   # Ширина в пропорційних пікселях
            'entry_height': 10,  # Висота в пропорційних пікселях
            'scale': 8,
            'border_color': '#F2F2F2',      # Світлий бордер
            'top_space_color': '#696D88',   # Колір верхнього пропуску
            'background_color': '#9A9FB4',  # Основний фон
            'text_color': 'white',
            'font_family': 'Minecraft Standard',
            # font_size тепер обчислюється автоматично на основі scale
            'placeholder': placeholder
        }

        # Застосовуємо користувацьку конфігурацію
        self.config = self.default_config.copy()
        if style_config:
            self.config.update(style_config)

        self.focused = False
        self.setup_entry()

    def setup_entry(self):
        """Налаштування текстового поля"""
        try:
            self.scale = self.config['scale']

            # Розрахунок розмірів з бордерами
            entry_width = self.config['entry_width']
            entry_height = self.config['entry_height']

            # Загальні розміри: бордери (1+1) + основна частина
            self.base_width = (entry_width + 2) * self.scale
            self.base_height = (entry_height + 2) * self.scale

            self.setFixedSize(self.base_width, self.base_height)

            # Створюємо елементи
            self.create_entry_border()
            self.create_entry_background()
            self.create_text_input()
        except Exception as e:
            print(f"Setup error: {e}")

    def create_entry_border(self):
        """Створення бордера Entry"""
        border_color = self.config['border_color']  # #F2F2F2

        # Верхній бордер
        self.top_border = QFrame(self)
        self.top_border.setGeometry(0, 0, self.base_width, self.scale)
        self.top_border.setStyleSheet(f"background-color: {border_color}; border-radius: 0px;")

        # Лівий бордер
        self.left_border = QFrame(self)
        self.left_border.setGeometry(0, self.scale, self.scale, self.config['entry_height'] * self.scale)
        self.left_border.setStyleSheet(f"background-color: {border_color}; border-radius: 0px;")

        # Правий бордер
        self.right_border = QFrame(self)
        self.right_border.setGeometry((self.config['entry_width'] + 1) * self.scale, self.scale,
                                     self.scale, self.config['entry_height'] * self.scale)
        self.right_border.setStyleSheet(f"background-color: {border_color}; border-radius: 0px;")

        # Нижній бордер
        self.bottom_border = QFrame(self)
        self.bottom_border.setGeometry(0, (self.config['entry_height'] + 1) * self.scale,
                                     self.base_width, self.scale)
        self.bottom_border.setStyleSheet(f"background-color: {border_color}; border-radius: 0px;")

    def create_entry_background(self):
        """Створення фону Entry"""
        entry_width = self.config['entry_width']
        entry_height = self.config['entry_height']

        # Верхній пропуск (2 пропорційних пікселі після бордеру)
        self.top_space = QFrame(self)
        self.top_space.setGeometry(self.scale, self.scale,
                                 entry_width * self.scale, 2 * self.scale)
        self.top_space.setStyleSheet(f"background-color: {self.config['top_space_color']}; border-radius: 0px;")

        # Основна частина (решта після верхнього пропуску)
        main_height = entry_height - 2  # Віднімаємо 2 пікселі верхнього пропуску
        self.main_background = QFrame(self)
        self.main_background.setGeometry(self.scale, (1 + 2) * self.scale,
                                       entry_width * self.scale, main_height * self.scale)
        self.main_background.setStyleSheet(f"background-color: {self.config['background_color']}; border-radius: 0px;")

    def create_text_input(self):
        """Створення текстового поля для введення"""
        entry_width = self.config['entry_width']
        entry_height = self.config['entry_height']

        # Текстове поле розташоване на 2 проп пкс вище бордеру (тобто в основній частині)
        # Переміщуємо на 2 пропорційних пікселя вгору
        text_y = (1 + 2) * self.scale - 2 * self.scale  # Після бордеру + після верхнього пропуску - 2 пікселя вгору

        # Висота основної частини БЕЗ нижнього відступу + компенсація за переміщення вгору
        text_height = (entry_height - 2) * self.scale + 2 * self.scale  # +2 пікселя для компенсації переміщення

        self.text_input = QLineEdit(self)

        # Залишаємо повну ширину, але додаємо внутрішній відступ через CSS
        self.text_input.setGeometry(
            self.scale,  # тільки бордер
            text_y,
            entry_width * self.scale,  # повна ширина
            text_height
        )

        # Розрахунок розміру шрифту на основі scale
        # Формула: font_size = scale * 4 (для більшого, читабельного тексту)
        calculated_font_size = self.scale * 4

        # Якщо в конфігурації явно вказано font_size, використовуємо його
        if 'font_size' in self.config:
            font_size = self.config['font_size']
        else:
            font_size = calculated_font_size

        # Налаштування шрифту з масштабованим розміром
        font = QFont(self.config['font_family'], font_size)
        self.text_input.setFont(font)

        # Стилі для текстового поля
        self.text_input.setStyleSheet(f"""
        QLineEdit {{
            background-color: transparent;
            border: none;
            color: {self.config['text_color']};
            padding-left: {self.scale}px;
            padding-right: 0px;
            padding-top: 0px;
            padding-bottom: 0px;
            margin: 0px;
            selection-background-color: {self.config['text_color']};
            selection-color: {self.config['background_color']};
        }}
        QLineEdit:focus {{
            outline: none;
        }}
        """)

        # Placeholder
        if self.config['placeholder']:
            self.text_input.setPlaceholderText(self.config['placeholder'])

        # Підключаємо сигнали
        self.text_input.textChanged.connect(self.textChanged.emit)
        self.text_input.returnPressed.connect(self.returnPressed.emit)

        # Безпечні обробники фокусу через сигнали
        self.text_input.focusInEvent = lambda event: self.handle_focus_in(event)
        self.text_input.focusOutEvent = lambda event: self.handle_focus_out(event)

    def handle_focus_in(self, event):
        """Безпечна обробка отримання фокусу"""
        try:
            self.focused = True
            self.update_entry_styles()
            # Викликаємо оригінальний обробник
            QLineEdit.focusInEvent(self.text_input, event)
        except Exception as e:
            print(f"Focus in error: {e}")

    def handle_focus_out(self, event):
        """Безпечна обробка втрати фокусу"""
        try:
            self.focused = False
            self.update_entry_styles()
            # Викликаємо оригінальний обробник
            QLineEdit.focusOutEvent(self.text_input, event)
        except Exception as e:
            print(f"Focus out error: {e}")

    def update_entry_styles(self):
        """Оновлення стилів при зміні фокусу"""
        try:
            if self.focused:
                # При фокусі можна змінити колір бордеру або фону
                # Наразі залишаємо як є, але можна додати ефекти
                pass
            else:
                # Без фокусу - стандартні кольори
                pass
        except Exception as e:
            print(f"Style update error: {e}")

    def get_text(self):
        """Отримання тексту"""
        return self.text_input.text()

    def set_text(self, text):
        """Встановлення тексту"""
        self.text_input.setText(text)

    def clear(self):
        """Очищення тексту"""
        self.text_input.clear()

    def set_placeholder(self, placeholder):
        """Встановлення placeholder тексту"""
        self.text_input.setPlaceholderText(placeholder)

    def set_readonly(self, readonly):
        """Встановлення режиму тільки для читання"""
        self.text_input.setReadOnly(readonly)