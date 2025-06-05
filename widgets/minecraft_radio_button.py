"""
Minecraft-стильні радіокнопки
"""
from PyQt6.QtWidgets import QFrame, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

class MinecraftRadioButton(QFrame):
    """
    Радіокнопка в стилі Minecraft
    """
    clicked = pyqtSignal()
    stateChanged = pyqtSignal(bool)  # True коли вибрано

    def __init__(self, text="", style_config=None, parent=None):
        super().__init__(parent)
        # Дефолтна конфігурація для радіокнопки
        self.default_config = {
            'text': text,
            'scale': 8,
            'border_color': '#413F54',
            'button_normal': '#9A9FB4',
            'button_hover': '#9CD3FF',
            'button_selected': '#9CD3FF',
            'border_normal': '#ADB0C4',
            'border_hover': '#DAFFFF',
            'border_selected': '#DAFFFF',
            'indicator_color': '#DAFFFF',
            'indicator_line_color': '#708CBA',  # Колір лінійки (51 74 97)
            'bottom_space_normal': '#696D88',   # Колір нижнього пробілу (неактивна)
            'bottom_space_hover': '#708CBA',    # Колір нижнього пробілу (навести)
            'bottom_space_selected': '#708CBA', # Колір нижнього пробілу (вибрано)
            'text_color': 'white',
            'font_family': 'Minecraftia'
        }

        # Застосовуємо користувацьку конфігурацію
        self.config = self.default_config.copy()
        if style_config:
            self.config.update(style_config)
        self.selected = False
        self.hover_state = False
        self.setup_radio_button()

    def setup_radio_button(self):
        """Налаштування радіокнопки"""
        self.scale = self.config['scale']

        # Розміри: зменшена основна частина (10x9) + бордери + нижній пробіл
        # Видаляємо відносно квадрату: 1 згори, 1 зліва, 1 зправа, 2 знизу
        main_width = 10  # було 12, мінус 1 зліва та 1 зправа
        main_height = 9  # було 12, мінус 1 згори та 2 знизу
        self.radio_width = (main_width + 2) * self.scale  # +2 для бордерів
        self.radio_height = (main_height + 2 + 2) * self.scale  # +2 для бордерів +2 для нижнього пробілу

        # Якщо є текст, додаємо місце для нього
        text_width = 0
        if self.config['text']:
            text_width = len(self.config['text']) * 10 + 10  # Фіксований розрахунок

        total_width = self.radio_width + text_width
        self.setFixedSize(total_width, self.radio_height)

        # Створюємо елементи
        self.create_radio_borders()
        self.create_radio_main()
        self.create_radio_indicator()
        self.create_radio_bottom_space()
        self.create_radio_text()
        self.update_radio_styles()

    def create_radio_borders(self):
        """Створення бордерів радіокнопки"""
        border_color = self.config['border_color']

        # Верхній бордер
        self.top_border = QFrame(self)
        self.top_border.setGeometry(0, 0, self.radio_width, self.scale)
        self.top_border.setStyleSheet(f"background-color: {border_color}; border-radius: 0px;")

        # Лівий бордер (висота для основної частини 9 + нижній простір 2)
        self.left_border = QFrame(self)
        self.left_border.setGeometry(0, self.scale, self.scale, 11 * self.scale)
        self.left_border.setStyleSheet(f"background-color: {border_color}; border-radius: 0px;")

        # Правий бордер (позиція для ширини 10+1)
        self.right_border = QFrame(self)
        self.right_border.setGeometry(11 * self.scale, self.scale, self.scale, 11 * self.scale)
        self.right_border.setStyleSheet(f"background-color: {border_color}; border-radius: 0px;")

        # Нижній бордер (позиція для висоти 9+2+1)
        self.bottom_border = QFrame(self)
        self.bottom_border.setGeometry(0, 12 * self.scale, self.radio_width, self.scale)
        self.bottom_border.setStyleSheet(f"background-color: {border_color}; border-radius: 0px;")

    def create_radio_main(self):
        """Створення основної частини радіокнопки"""
        self.main_area = QFrame(self)
        # Нова основна частина: 10x9 пікселів
        self.main_area.setGeometry(self.scale, self.scale, 10 * self.scale, 9 * self.scale)

    def create_radio_indicator(self):
        """Створення центрального індикатора для вибраного стану"""
        # Центральний квадрат 4x4 з новими відступами
        # Зліва: 3 пікселі (було 4, мінус 1)
        # Згори: 3 пікселі (було 4, мінус 1)
        indicator_size = 4 * self.scale
        indicator_x = self.scale + 3 * self.scale  # відступ 3 пікселі від лівого краю основної частини
        indicator_y = self.scale + 3 * self.scale  # відступ 3 пікселі від верхнього краю

        self.indicator = QFrame(self)
        self.indicator.setGeometry(indicator_x, indicator_y, indicator_size, indicator_size)
        self.indicator.hide()  # Спочатку прихований

        # Горизонтальна лінійка всередині індикатора (4x1 піксель) - в першому рядочку
        line_y = indicator_y  # В першому рядочку квадрату
        self.indicator_line = QFrame(self)
        self.indicator_line.setGeometry(indicator_x, line_y, indicator_size, self.scale)
        self.indicator_line.hide()  # Спочатку прихований

    def create_radio_bottom_space(self):
        """Створення нижнього пробілу радіокнопки"""
        # Нижній пробіл займає всю ширину нової основної частини (10 пікселів)
        space_width = 10 * self.scale  # Вся ширина всередині бордерів
        space_x = self.scale  # Починається одразу після лівого бордера
        space_y = 10 * self.scale  # Під основною частиною (1 + 9)

        self.radio_bottom_space = QFrame(self)
        self.radio_bottom_space.setGeometry(space_x, space_y, space_width, 2 * self.scale)

    def create_radio_text(self):
        """Створення тексту радіокнопки"""
        if self.config['text']:
            self.text_label = QLabel(self.config['text'], self)
            font = QFont(self.config['font_family'], 16)  # Фіксований розмір
            self.text_label.setFont(font)
            self.text_label.setStyleSheet(f"color: {self.config['text_color']}; background: transparent;")

            # Позиціонуємо текст праворуч від радіокнопки
            text_x = self.radio_width + 5
            text_y = (self.radio_height - 16) // 2  # Фіксований розмір шрифту
            self.text_label.move(text_x, text_y)

    def mousePressEvent(self, event):
        """Обробка натискання"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Перевіряємо, чи клік був по радіокнопці (не по тексту)
            if event.pos().x() <= self.radio_width:
                self.toggle_selection()
        super().mousePressEvent(event)

    def enterEvent(self, event):
        """Обробка наведення миші"""
        self.hover_state = True
        self.update_radio_styles()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Обробка виходу миші"""
        self.hover_state = False
        self.update_radio_styles()
        super().leaveEvent(event)

    def toggle_selection(self):
        """Перемикання стану вибору"""
        self.selected = not self.selected
        self.update_radio_styles()
        self.clicked.emit()
        self.stateChanged.emit(self.selected)

    def set_selected(self, selected):
        """Встановлення стану вибору програмно"""
        if self.selected != selected:
            self.selected = selected
            self.update_radio_styles()
            self.stateChanged.emit(self.selected)

    def is_selected(self):
        """Повертає стан вибору"""
        return self.selected

    def update_radio_styles(self):
        """Оновлення стилів радіокнопки"""
        if self.selected:
            # Вибраний стан (як натиснута кнопка)
            button_bg = self.config['button_selected']
            border_color = self.config['border_selected']
            bottom_space_color = self.config['bottom_space_selected']

            # Зміщуємо основну частину вниз на 1 піксель
            self.main_area.setGeometry(self.scale, 2 * self.scale, 10 * self.scale, 9 * self.scale)

            # Нижній пробіл зменшується до 1 пікселя (як у натиснутої кнопки)
            self.radio_bottom_space.setGeometry(self.scale, 11 * self.scale, 10 * self.scale, 1 * self.scale)

            # Показуємо індикатор
            self.indicator.show()
            self.indicator_line.show()

            # Змінюємо верхній бордер
            self.top_border.setStyleSheet("background-color: #CBCCD4; border-radius: 0px;")

        elif self.hover_state:
            # Стан наведення
            button_bg = self.config['button_hover']
            border_color = self.config['border_hover']
            bottom_space_color = self.config['bottom_space_hover']

            # Нормальна позиція
            self.main_area.setGeometry(self.scale, self.scale, 10 * self.scale, 9 * self.scale)

            # Нормальний розмір нижнього пробілу (2 пікселі)
            self.radio_bottom_space.setGeometry(self.scale, 10 * self.scale, 10 * self.scale, 2 * self.scale)

            # Приховуємо індикатор
            self.indicator.hide()
            self.indicator_line.hide()

            # Відновлюємо верхній бордер
            self.top_border.setStyleSheet(f"background-color: {self.config['border_color']}; border-radius: 0px;")

        else:
            # Нормальний стан
            button_bg = self.config['button_normal']
            border_color = self.config['border_normal']
            bottom_space_color = self.config['bottom_space_normal']

            # Нормальна позиція
            self.main_area.setGeometry(self.scale, self.scale, 10 * self.scale, 9 * self.scale)

            # Нормальний розмір нижнього пробілу (2 пікселі)
            self.radio_bottom_space.setGeometry(self.scale, 10 * self.scale, 10 * self.scale, 2 * self.scale)

            # Приховуємо індикатор
            self.indicator.hide()
            self.indicator_line.hide()

            # Відновлюємо верхній бордер
            self.top_border.setStyleSheet(f"background-color: {self.config['border_color']}; border-radius: 0px;")

        # Застосовуємо стилі
        main_style = f"""QFrame {{ 
            background-color: {button_bg}; 
            border: {self.scale}px solid {border_color};
            border-radius: 0px;
        }}"""

        indicator_style = f"""QFrame {{ 
            background-color: {self.config['indicator_color']}; 
            border: none;
            border-radius: 0px;
        }}"""

        line_style = f"""QFrame {{ 
            background-color: {self.config['indicator_line_color']}; 
            border: none;
            border-radius: 0px;
        }}"""

        bottom_space_style = f"""QFrame {{ 
            background-color: {bottom_space_color}; 
            border: none;
            border-radius: 0px;
        }}"""

        self.main_area.setStyleSheet(main_style)
        self.indicator.setStyleSheet(indicator_style)
        self.indicator_line.setStyleSheet(line_style)
        self.radio_bottom_space.setStyleSheet(bottom_space_style)
        self.setStyleSheet(f"background-color: {self.config['border_color']}; border-radius: 0px;")

class MinecraftRadioGroup:
    """
    Група радіокнопок (тільки одна може бути вибрана одночасно)
    """
    def __init__(self):
        self.radio_buttons = []
        self.selected_button = None

    def add_radio_button(self, radio_button):
        """Додати радіокнопку до групи"""
        if radio_button not in self.radio_buttons:
            self.radio_buttons.append(radio_button)
            radio_button.clicked.connect(lambda: self.on_radio_clicked(radio_button))

    def on_radio_clicked(self, clicked_button):
        """Обробка кліку по радіокнопці"""
        # Знімаємо вибір з усіх кнопок
        for button in self.radio_buttons:
            if button != clicked_button:
                button.set_selected(False)

        # Встановлюємо вибір на натиснуту кнопку
        self.selected_button = clicked_button
        clicked_button.set_selected(True)

    def get_selected(self):
        """Повертає вибрану радіокнопку"""
        return self.selected_button

    def clear_selection(self):
        """Очищає вибір"""
        for button in self.radio_buttons:
            button.set_selected(False)
        self.selected_button = None
