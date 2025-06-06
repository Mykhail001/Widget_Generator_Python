"""
Повністю виправлений widgets/minecraft_slider.py
"""
from PyQt6.QtWidgets import QFrame
from PyQt6.QtCore import Qt, pyqtSignal
from .minecraft_button import MinecraftButton

class MinecraftSlider(QFrame):
    """
    Слайдер в стилі Minecraft
    """
    valueChanged = pyqtSignal(float)  # Значення від 0.0 до 1.0

    def __init__(self, style_config=None, parent=None):
        super().__init__(parent)

        # Дефолтна конфігурація
        self.default_config = {
            'scale': 8,
            'orientation': 'vertical',  # 'vertical' або 'horizontal'
            'track_width': 6,   # Ширина підложки (пропорційні пікселі)
            'track_height': 30, # Висота підложки (пропорційні пікселі)
            'track_border_color': '#F2F2F2',  # Колір бордера підложки
            'track_fill_color': '#9A9FB4',    # Колір середини підложки
            'slider_button_config': {
                'button_width': 8,
                'button_height': 6,
                'scale': 8,
                'border_color': '#413F54',
                'button_normal': '#9A9FB4',
                'button_hover': '#9A9FB4',     # Без hover ефекту
                'button_pressed': '#9A9FB4',   # Без pressed ефекту
                'border_normal': '#ADB0C4',
                'border_hover': '#ADB0C4',     # Без hover ефекту
                'border_pressed': '#ADB0C4',   # Без pressed ефекту
                'bottom_normal': '#9A9FB4',
                'bottom_hover': '#9A9FB4',     # Без hover ефекту
                'bottom_pressed': '#9A9FB4',   # Без pressed ефекту
                'text_color': 'white',
                'font_family': 'Minecraftia',
                'has_shadow': True,
                'animation_enabled': False  # Відключаємо анімацію
            }
        }

        # Застосовуємо користувацьку конфігурацію
        self.config = self.default_config.copy()
        if style_config:
            for key, value in style_config.items():
                if key == 'slider_button_config':
                    # Оновлюємо конфігурацію кнопки окремо
                    self.config['slider_button_config'].update(value)
                else:
                    self.config[key] = value
        self.value = 0.0  # Поточне значення (0.0 - 1.0)
        self.dragging = False
        self.drag_offset = 0

        self.setup_slider()

    def setup_slider(self):
        """Налаштування слайдера"""
        self.scale = self.config['scale']
        self.orientation = self.config['orientation']

        # Розрахунок розмірів підложки
        if self.orientation == 'vertical':
            track_width = self.config['track_width']
            track_height = self.config['track_height']
        else:  # horizontal
            track_width = self.config['track_height']  # Міняємо місцями
            track_height = self.config['track_width']

        # Загальні розміри з бордерами (тільки світлі бордери)
        self.track_width = (track_width + 2) * self.scale
        self.track_height = (track_height + 2) * self.scale

        # Розміри віджета (додаємо місце для повзунка)
        if self.orientation == 'vertical':
            widget_width = max(self.track_width, 12 * self.scale)  # Більше місця для повзунка
            widget_height = self.track_height + 2 * self.scale  # Невеликий відступ
        else:
            widget_width = self.track_width + 2 * self.scale  # Невеликий відступ
            widget_height = max(self.track_height, 10 * self.scale)  # Більше місця для повзунка

        self.setFixedSize(widget_width, widget_height)

        # Створюємо елементи
        self.create_track()
        self.create_slider_button()
        self.update_slider_position()
        self.slider_button.update_styles()

    def create_track(self):
        """Створення підложки слайдера"""
        track_border_color = self.config['track_border_color']  # #F2F2F2
        track_fill_color = self.config['track_fill_color']      # #9A9FB4

        # Позиція підложки (центруємо)
        if self.orientation == 'vertical':
            track_x = (self.width() - self.track_width) // 2
            track_y = 0
        else:
            track_x = 0
            track_y = (self.height() - self.track_height) // 2

        # Світлі бордери (F2F2F2) - БЕЗ темного зовнішнього бордера
        self.track_border = QFrame(self)
        self.track_border.setGeometry(track_x, track_y, self.track_width, self.track_height)
        self.track_border.setStyleSheet(f"background-color: {track_border_color}; border-radius: 0px;")

        # Середина підложки (9A9FB4)
        fill_x = track_x + self.scale
        fill_y = track_y + self.scale
        fill_width = self.track_width - 2 * self.scale
        fill_height = self.track_height - 2 * self.scale

        self.track_fill = QFrame(self)
        self.track_fill.setGeometry(fill_x, fill_y, fill_width, fill_height)
        self.track_fill.setStyleSheet(f"background-color: {track_fill_color}; border-radius: 0px;")

    def create_slider_button(self):
        """Створення повзунка"""
        # Створюємо кнопку БЕЗ ефектів hover/press
        button_config = self.config['slider_button_config'].copy()
        button_config['scale'] = self.scale

        self.slider_button = MinecraftButton('', button_config, self)

        # Повністю відключаємо всі ефекти кнопки
        self.slider_button.hover_state = False
        self.slider_button.pressed_state = False

        # Перевизначаємо всі mouse events для перетягування
        self.slider_button.mousePressEvent = self.button_mouse_press
        self.slider_button.mouseMoveEvent = self.button_mouse_move
        self.slider_button.mouseReleaseEvent = self.button_mouse_release
        self.slider_button.enterEvent = lambda event: None  # Відключаємо hover
        self.slider_button.leaveEvent = lambda event: None  # Відключаємо hover

    def button_mouse_press(self, event):
        """Обробка натискання на повзунок"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            if self.orientation == 'vertical':
                self.drag_offset = event.pos().y()
            else:
                self.drag_offset = event.pos().x()

    def button_mouse_move(self, event):
        """Обробка переміщення повзунка"""
        if self.dragging:
            # Конвертуємо координати у координати батьківського віджета
            global_pos = self.slider_button.mapToParent(event.pos())

            if self.orientation == 'vertical':
                # Вертикальний слайдер - рух по Y
                track_start = self.scale  # Початок області руху
                track_end = self.track_height - self.scale  # Кінець області руху
                current_pos = global_pos.y() - self.drag_offset

                # Обмежуємо рух в межах підложки
                current_pos = max(track_start, min(track_end - self.slider_button.height(), current_pos))

                # Перерахунок значення (0.0 - 1.0)
                track_range = track_end - track_start - self.slider_button.height()
                if track_range > 0:
                    self.value = (current_pos - track_start) / track_range
                else:
                    self.value = 0.0
            else:
                # Горизонтальний слайдер - рух по X
                track_start = self.scale
                track_end = self.track_width - self.scale
                current_pos = global_pos.x() - self.drag_offset

                current_pos = max(track_start, min(track_end - self.slider_button.width(), current_pos))

                track_range = track_end - track_start - self.slider_button.width()
                if track_range > 0:
                    self.value = (current_pos - track_start) / track_range
                else:
                    self.value = 0.0

            # Обмежуємо значення
            self.value = max(0.0, min(1.0, self.value))
            self.update_slider_position()
            self.valueChanged.emit(self.value)

    def button_mouse_release(self, event):
        """Обробка відпускання повзунка"""
        if self.dragging:
            self.dragging = False

    def mousePressEvent(self, event):
        """Обробка кліку по підложці"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Переміщуємо повзунок до місця кліку
            if self.orientation == 'vertical':
                track_start = self.scale
                track_end = self.track_height - self.scale
                click_pos = event.pos().y()

                # Центруємо повзунок відносно кліку
                target_pos = click_pos - self.slider_button.height() // 2
                target_pos = max(track_start, min(track_end - self.slider_button.height(), target_pos))

                track_range = track_end - track_start - self.slider_button.height()
                if track_range > 0:
                    self.value = (target_pos - track_start) / track_range
            else:
                track_start = self.scale
                track_end = self.track_width - self.scale
                click_pos = event.pos().x()

                target_pos = click_pos - self.slider_button.width() // 2
                target_pos = max(track_start, min(track_end - self.slider_button.width(), target_pos))

                track_range = track_end - track_start - self.slider_button.width()
                if track_range > 0:
                    self.value = (target_pos - track_start) / track_range

            self.value = max(0.0, min(1.0, self.value))
            self.update_slider_position()
            self.valueChanged.emit(self.value)

    def update_slider_position(self):
        """Оновлення позиції повзунка"""
        if self.orientation == 'vertical':
            track_start = self.scale  # Відступ від початку підложки
            track_end = self.track_height - self.scale
            track_range = track_end - track_start - self.slider_button.height()

            if track_range > 0:
                button_y = track_start + int(self.value * track_range)
            else:
                button_y = track_start

            button_x = (self.width() - self.slider_button.width()) // 2

            self.slider_button.move(button_x, button_y)
        else:  # horizontal
            track_start = self.scale
            track_end = self.track_width - self.scale
            track_range = track_end - track_start - self.slider_button.width()

            if track_range > 0:
                button_x = track_start + int(self.value * track_range)
            else:
                button_x = track_start

            button_y = (self.height() - self.slider_button.height()) // 2

            self.slider_button.move(button_x, button_y)

    def set_value(self, value):
        """Встановлення значення програмно"""
        self.value = max(0.0, min(1.0, value))
        self.update_slider_position()
        self.valueChanged.emit(self.value)

    def get_value(self):
        """Отримання поточного значення"""
        return self.value

    def set_orientation(self, orientation):
        """Зміна орієнтації слайдера"""
        if orientation in ['vertical', 'horizontal']:
            self.config['orientation'] = orientation
            self.setup_slider()