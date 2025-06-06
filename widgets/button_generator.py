"""
Головний генератор кнопок - інтерфейс програми
"""
import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QGroupBox, QGridLayout, QScrollArea, QTextEdit,
    QLabel, QSpinBox, QCheckBox, QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt

from managers import TogglePatternManager, ButtonPatternManager, ButtonPresetManager
from .minecraft_button import MinecraftButton
from .minecraft_radio_button import MinecraftRadioButton, MinecraftRadioGroup
from .minecraft_toggle_button import MinecraftToggleButton
from .minecraft_slider import MinecraftSlider

class ButtonGenerator(QWidget):
    """
    Головний генератор кнопок
    """

    def __init__(self):
        super().__init__()

        # Ініціалізуємо змінні
        self.current_widget_type = "button"
        self.current_config = {}
        self.preview_button = None
        self.preview_radio = None
        self.preview_radio2 = None
        self.preview_toggle = None
        self.preview_slider = None
        self.preview_group = None
        self.generated_buttons = []
        self.generated_radios = []
        self.generated_toggles = []
        self.generated_sliders = []
        self.code_dialog = None

        self.setup_ui()

    def setup_ui(self):
        """Налаштування інтерфейсу"""
        main_layout = QHBoxLayout()

        # Ліва панель - настройки
        left_panel = self.create_settings_panel()
        main_layout.addWidget(left_panel, 1)

        # Права панель - прев'ю та генеровані кнопки
        right_panel = self.create_preview_panel()
        main_layout.addWidget(right_panel, 2)

        self.setLayout(main_layout)
        self.setStyleSheet("background-color: #2C2C2C;")

        self.update_preview()

    def create_settings_panel(self):
        """Створення панелі налаштувань"""
        settings_widget = QWidget()
        settings_widget.setMaximumWidth(400)
        settings_widget.setStyleSheet("background-color: #3C3C3C; border-radius: 10px; padding: 10px; color: white;")
        layout = QVBoxLayout()

        # Заголовок
        title = QLabel("⚙️ WIDGET CONFIGURATOR")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #4CAF50; padding: 10px;")
        layout.addWidget(title)

        # Тип віджета
        widget_type_group = QGroupBox("🔘 Widget Type")
        widget_type_layout = QGridLayout()  # Змінено з QHBoxLayout на QGridLayout

        # Перший рядок: Button та Radio Button
        self.button_radio = QCheckBox("Button")
        self.button_radio.setChecked(True)
        self.button_radio.toggled.connect(lambda checked: self.set_widget_type("button" if checked else self.get_other_widget_type("button")))
        widget_type_layout.addWidget(self.button_radio, 0, 0)

        self.radio_radio = QCheckBox("Radio Button")
        self.radio_radio.toggled.connect(lambda checked: self.set_widget_type("radio" if checked else self.get_other_widget_type("radio")))
        widget_type_layout.addWidget(self.radio_radio, 0, 1)

        # Другий рядок: Toggle Switch та Slider
        self.toggle_radio = QCheckBox("Toggle Switch")
        self.toggle_radio.toggled.connect(lambda checked: self.set_widget_type("toggle" if checked else self.get_other_widget_type("toggle")))
        widget_type_layout.addWidget(self.toggle_radio, 1, 0)

        self.slider_radio = QCheckBox("Slider")
        self.slider_radio.toggled.connect(lambda checked: self.set_widget_type("slider" if checked else self.get_other_widget_type("slider")))
        widget_type_layout.addWidget(self.slider_radio, 1, 1)

        widget_type_group.setLayout(widget_type_layout)
        layout.addWidget(widget_type_group)

        # Основні налаштування
        basic_group = QGroupBox("🔧 Basic Settings")
        basic_layout = QGridLayout()

        # Масштаб
        basic_layout.addWidget(QLabel("Scale:"), 0, 0)
        self.scale_input = QSpinBox()
        self.scale_input.setRange(4, 16)
        self.scale_input.setValue(8)
        basic_layout.addWidget(self.scale_input, 0, 1)

        # Розмір кнопки (в пропорційних пікселях) - тільки для звичайних кнопок
        self.size_label_width = QLabel("Button Width:")
        basic_layout.addWidget(self.size_label_width, 1, 0)
        self.width_input = QSpinBox()
        self.width_input.setRange(4, 32)
        self.width_input.setValue(16)
        basic_layout.addWidget(self.width_input, 1, 1)

        self.size_label_height = QLabel("Button Height:")
        basic_layout.addWidget(self.size_label_height, 2, 0)
        self.height_input = QSpinBox()
        self.height_input.setRange(4, 32)
        self.height_input.setValue(15)
        basic_layout.addWidget(self.height_input, 2, 1)

        # Орієнтація слайдера
        self.orientation_label = QLabel("Orientation:")
        basic_layout.addWidget(self.orientation_label, 3, 0)
        self.orientation_combo = QComboBox()
        self.orientation_combo.addItems(["Vertical", "Horizontal"])
        self.orientation_combo.currentTextChanged.connect(self.update_preview)
        basic_layout.addWidget(self.orientation_combo, 3, 1)

        # Довжина слайдера
        self.slider_length_label = QLabel("Track Length:")
        basic_layout.addWidget(self.slider_length_label, 4, 0)
        self.slider_length_input = QSpinBox()
        self.slider_length_input.setRange(10, 60)
        self.slider_length_input.setValue(30)
        self.slider_length_input.valueChanged.connect(self.update_preview)
        basic_layout.addWidget(self.slider_length_input, 4, 1)

        # Приховуємо поля слайдера за замовчуванням
        self.orientation_label.hide()
        self.orientation_combo.hide()
        self.slider_length_label.hide()
        self.slider_length_input.hide()

        # Підключаємо сигнали після створення всіх елементів
        self.scale_input.valueChanged.connect(self.update_preview)
        self.width_input.valueChanged.connect(self.update_preview)
        self.height_input.valueChanged.connect(self.update_preview)

        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)

        # Встановлюємо початковий тип віджета (після підключення сигналів)
        self.set_widget_type("button")

        # Пресети
        preset_group = QGroupBox("🎨 Style Presets")
        preset_layout = QVBoxLayout()

        self.preset_combo = QComboBox()
        self.preset_combo.addItems(ButtonPresetManager.get_presets().keys())
        self.preset_combo.currentTextChanged.connect(self.apply_preset)
        preset_layout.addWidget(self.preset_combo)

        preset_group.setLayout(preset_layout)
        layout.addWidget(preset_group)

        # Патерни (тільки для toggle switch)
        self.pattern_group = QGroupBox("🎨 Toggle Patterns")
        pattern_layout = QVBoxLayout()

        self.pattern_combo = QComboBox()
        self.pattern_combo.addItems(TogglePatternManager.get_patterns().keys())
        self.pattern_combo.setCurrentText('Standard')  # Стандартний патерн за замовчуванням
        self.pattern_combo.currentTextChanged.connect(self.apply_pattern)
        pattern_layout.addWidget(self.pattern_combo)

        self.pattern_group.setLayout(pattern_layout)
        layout.addWidget(self.pattern_group)
        self.pattern_group.hide()  # Спочатку прихований

        # Патерни для кнопок (тільки для button)
        self.button_pattern_group = QGroupBox("🎨 Button Patterns")
        button_pattern_layout = QVBoxLayout()

        self.button_pattern_combo = QComboBox()
        self.button_pattern_combo.addItems(ButtonPatternManager.get_patterns().keys())
        self.button_pattern_combo.setCurrentText('None')  # Без патерну за замовчуванням
        self.button_pattern_combo.currentTextChanged.connect(self.apply_button_pattern)
        button_pattern_layout.addWidget(self.button_pattern_combo)

        self.button_pattern_group.setLayout(button_pattern_layout)
        layout.addWidget(self.button_pattern_group)
        self.button_pattern_group.show()  # Показано для кнопок за замовчуванням

        # Опції
        options_group = QGroupBox("⚡ Options")
        options_layout = QVBoxLayout()

        self.animation_check = QCheckBox("Enable Press Animation")
        self.animation_check.setChecked(True)
        options_layout.addWidget(self.animation_check)

        # Підключаємо сигнали checkboxes
        self.animation_check.toggled.connect(self.update_preview)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Кнопки дій
        actions_layout = QVBoxLayout()

        generate_btn = QPushButton("🔨 Generate Widget")
        generate_btn.setStyleSheet("background-color: #4CAF50; padding: 10px; font-weight: bold;")
        generate_btn.clicked.connect(self.generate_widget)
        actions_layout.addWidget(generate_btn)

        save_preset_btn = QPushButton("💾 Save Preset")
        save_preset_btn.clicked.connect(self.save_preset)
        actions_layout.addWidget(save_preset_btn)

        export_code_btn = QPushButton("📄 Export Code")
        export_code_btn.clicked.connect(self.export_code)
        actions_layout.addWidget(export_code_btn)

        layout.addLayout(actions_layout)
        layout.addStretch()

        settings_widget.setLayout(layout)
        return settings_widget

    def create_preview_panel(self):
        """Створення панелі превью"""
        preview_widget = QWidget()
        layout = QVBoxLayout()

        # Превью
        preview_group = QGroupBox("👁️ LIVE PREVIEW")
        preview_group.setStyleSheet("QGroupBox { color: white;}")
        preview_layout = QVBoxLayout()
        preview_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.preview_container = QWidget()
        self.preview_container.setFixedSize(400, 200)  # Збільшуємо ширину як у згенерованих віджетів
        self.preview_container.setStyleSheet("background-color: #CBCCD4;")
        preview_layout.addWidget(self.preview_container)

        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)

        # Згенеровані віджети
        generated_group = QGroupBox("🏭 GENERATED WIDGETS")
        generated_group.setStyleSheet("QGroupBox { color: white;}")

        self.scroll_area = QScrollArea()
        self.scroll_content = QWidget()
        self.scroll_layout = QGridLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background-color: #CBCCD4;")

        generated_layout = QVBoxLayout()
        generated_layout.addWidget(self.scroll_area)

        clear_btn = QPushButton("🗑️ Clear All")
        clear_btn.setStyleSheet("QPushButton { color: white; background-color: #9A9FB4; border: 1px solid #ADB0C4; padding: 5px; }")
        clear_btn.clicked.connect(self.clear_generated_buttons)
        generated_layout.addWidget(clear_btn)

        generated_group.setLayout(generated_layout)
        layout.addWidget(generated_group)

        preview_widget.setLayout(layout)
        return preview_widget

    def get_other_widget_type(self, unchecked_type):
        """Повертає інший тип віджета коли один був відключений"""
        checkboxes = {
            "button": self.button_radio,
            "radio": self.radio_radio,
            "toggle": self.toggle_radio,
            "slider": self.slider_radio
        }

        # Знаходимо перший вибраний checkbox (крім того що був відключений)
        for widget_type, checkbox in checkboxes.items():
            if widget_type != unchecked_type and checkbox.isChecked():
                return widget_type
        return "button"

    def set_widget_type(self, widget_type):
        """Встановлення типу віджета"""
        if widget_type != self.current_widget_type:
            self.current_widget_type = widget_type

            # Оновлюємо checkboxes (тільки один може бути вибраний)
            self.button_radio.setChecked(widget_type == "button")
            self.radio_radio.setChecked(widget_type == "radio")
            self.toggle_radio.setChecked(widget_type == "toggle")
            self.slider_radio.setChecked(widget_type == "slider")

            # Показуємо/приховуємо налаштування залежно від типу
            if widget_type == "button":
                # Для кнопок показуємо розміри
                self.size_label_width.show()
                self.size_label_height.show()
                self.width_input.show()
                self.height_input.show()
                self.orientation_label.hide()
                self.orientation_combo.hide()
                self.slider_length_label.hide()
                self.slider_length_input.hide()
                # Показуємо патерни для кнопок, приховуємо для toggle
                self.button_pattern_group.show()
                self.pattern_group.hide()
            elif widget_type == "radio":
                # Приховуємо налаштування для радіокнопок
                self.size_label_width.hide()
                self.size_label_height.hide()
                self.width_input.hide()
                self.height_input.hide()
                self.orientation_label.hide()
                self.orientation_combo.hide()
                self.slider_length_label.hide()
                self.slider_length_input.hide()
                # Приховуємо всі патерни для radio
                self.button_pattern_group.hide()
                self.pattern_group.hide()
            elif widget_type == "toggle":
                # Для перемикача приховуємо всі налаштування розмірів
                self.size_label_width.hide()
                self.size_label_height.hide()
                self.width_input.hide()
                self.height_input.hide()
                self.orientation_label.hide()
                self.orientation_combo.hide()
                self.slider_length_label.hide()
                self.slider_length_input.hide()
                # Показуємо патерни для toggle switch, приховуємо для кнопок
                self.button_pattern_group.hide()
                self.pattern_group.show()
            elif widget_type == "slider":
                # Для слайдера приховуємо розміри, показуємо орієнтацію та довжину
                self.size_label_width.hide()
                self.size_label_height.hide()
                self.width_input.hide()
                self.height_input.hide()
                self.orientation_label.show()
                self.orientation_combo.show()
                self.slider_length_label.show()
                self.slider_length_input.show()
                # Приховуємо всі патерни
                self.button_pattern_group.hide()
                self.pattern_group.hide()

            self.update_preview()

    def update_preview(self):
        """Оновлення превью віджета"""
        # Видаляємо старі віджети
        if self.preview_button:
            self.preview_button.deleteLater()
            self.preview_button = None
        if self.preview_radio:
            self.preview_radio.deleteLater()
            self.preview_radio = None
        if self.preview_radio2:
            self.preview_radio2.deleteLater()
            self.preview_radio2 = None
        if self.preview_toggle:
            self.preview_toggle.deleteLater()
            self.preview_toggle = None
        if self.preview_slider:
            self.preview_slider.deleteLater()
            self.preview_slider = None

        # Створюємо конфігурацію залежно від типу віджета
        if self.current_widget_type == "button":
            config = {
                'button_width': self.width_input.value(),
                'button_height': self.height_input.value(),
                'scale': self.scale_input.value(),
                'animation_enabled': self.animation_check.isChecked(),
                'has_shadow': True  # Завжди ввімкнено
            }
            config.update(self.current_config)

            # Створюємо нову кнопку без тексту
            self.preview_button = MinecraftButton('', config, self.preview_container)

            # Застосовуємо вибраний патерн
            button_pattern_name = self.button_pattern_combo.currentText()
            self.preview_button.set_pattern(button_pattern_name)

            self.preview_button.move(
                (self.preview_container.width() - self.preview_button.width()) // 2,
                (self.preview_container.height() - self.preview_button.height()) // 2
            )
            self.preview_button.show()

        elif self.current_widget_type == "radio":
            config = {
                'text': "",  # Без тексту для демонстрації
                'scale': self.scale_input.value(),
                'has_shadow': True  # Завжди ввімкнено
            }
            config.update(self.current_config)

            # Створюємо два радіо для демонстрації
            self.preview_radio = MinecraftRadioButton("", config, self.preview_container)
            self.preview_radio2 = MinecraftRadioButton("", config, self.preview_container)

            # Позиціонуємо їх поруч
            radio_spacing = 20
            total_width = self.preview_radio.width() * 2 + radio_spacing
            start_x = (self.preview_container.width() - total_width) // 2
            y_pos = (self.preview_container.height() - self.preview_radio.height()) // 2

            self.preview_radio.move(start_x, y_pos)
            self.preview_radio2.move(start_x + self.preview_radio.width() + radio_spacing, y_pos)

            # Один вибраний, другий ні
            self.preview_radio.set_selected(True)
            self.preview_radio2.set_selected(False)

            # Створюємо групу для демонстрації функціональності
            self.preview_group = MinecraftRadioGroup()
            self.preview_group.add_radio_button(self.preview_radio)
            self.preview_group.add_radio_button(self.preview_radio2)

            self.preview_radio.show()
            self.preview_radio2.show()

        elif self.current_widget_type == "toggle":
            config = {
                'scale': self.scale_input.value(),
                'has_shadow': True  # Завжди ввімкнено
            }
            config.update(self.current_config)

            # Створюємо перемикач (без тексту)
            self.preview_toggle = MinecraftToggleButton(config, self.preview_container)

            # Застосовуємо вибраний патерн
            pattern_name = self.pattern_combo.currentText()
            self.preview_toggle.set_pattern(pattern_name)

            self.preview_toggle.move(
                (self.preview_container.width() - self.preview_toggle.width()) // 2,
                (self.preview_container.height() - self.preview_toggle.height()) // 2
            )
            self.preview_toggle.show()

        elif self.current_widget_type == "slider":
            # Визначаємо розміри підложки залежно від орієнтації
            orientation = self.orientation_combo.currentText().lower()
            track_length = self.slider_length_input.value()

            if orientation == 'vertical':
                track_width = 6      # Фіксована ширина
                track_height = track_length  # Змінна висота
            else:  # horizontal
                track_width = track_length   # Змінна ширина
                track_height = 6     # Фіксована висота

            config = {
                'scale': self.scale_input.value(),
                'orientation': orientation,
                'track_width': track_width,
                'track_height': track_height,
                'has_shadow': True,
                'slider_button_config': {
                    'button_width': 8,
                    'button_height': 6,
                    'scale': self.scale_input.value(),
                    'border_color': '#413F54',
                    'animation_enabled': False
                }
            }

            # Застосовуємо поточні стилі з пресету
            if self.current_config:
                button_config = config['slider_button_config']

                if 'button_normal' in self.current_config:
                    button_config['button_normal'] = self.current_config['button_normal']
                    button_config['button_hover'] = self.current_config['button_normal']
                    button_config['button_pressed'] = self.current_config['button_normal']

                if 'border_normal' in self.current_config:
                    button_config['border_normal'] = self.current_config['border_normal']
                    button_config['border_hover'] = self.current_config['border_normal']
                    button_config['border_pressed'] = self.current_config['border_normal']

                if 'bottom_normal' in self.current_config:
                    button_config['bottom_normal'] = self.current_config['bottom_normal']
                    button_config['bottom_hover'] = self.current_config['bottom_normal']
                    button_config['bottom_pressed'] = self.current_config['bottom_normal']

                if 'button_normal' in self.current_config:
                    config['track_fill_color'] = self.current_config['button_normal']

            self.preview_slider = MinecraftSlider(config, self.preview_container)
            self.preview_slider.set_value(0.5)

            self.preview_slider.move(
                (self.preview_container.width() - self.preview_slider.width()) // 2,
                (self.preview_container.height() - self.preview_slider.height()) // 2
            )
            self.preview_slider.show()

    def apply_preset(self, preset_name):
        """Застосування пресету"""
        presets = ButtonPresetManager.get_presets()
        if preset_name in presets:
            self.current_config.update(presets[preset_name])
            self.update_preview()

    def apply_pattern(self, pattern_name):
        """Застосування патерну для toggle switch"""
        if self.current_widget_type == "toggle" and self.preview_toggle:
            self.preview_toggle.set_pattern(pattern_name)
            # Оновлюємо превью
            self.update_preview()

    def apply_button_pattern(self, pattern_name):
        """Застосування патерну для кнопки"""
        if self.current_widget_type == "button" and self.preview_button:
            self.preview_button.set_pattern(pattern_name)
            # Патерн автоматично відобразиться без повного оновлення превью

    def generate_widget(self):
        """Генерація нового віджета"""
        if self.current_widget_type == "button":
            config = {
                'button_width': self.width_input.value(),
                'button_height': self.height_input.value(),
                'scale': self.scale_input.value(),
                'animation_enabled': self.animation_check.isChecked(),
                'has_shadow': True  # Завжди ввімкнено
            }
            config.update(self.current_config)

            # Створюємо кнопку без тексту
            button = MinecraftButton('', config)

            # Застосовуємо вибраний патерн
            button_pattern_name = self.button_pattern_combo.currentText()
            button.set_pattern(button_pattern_name)

            button.clicked.connect(lambda: print("Button clicked!"))

            # Додаємо до сітки
            item_count = self.scroll_layout.count()
            row = item_count // 4
            col = item_count % 4
            self.scroll_layout.addWidget(button, row, col)

            self.generated_buttons.append(button)

        elif self.current_widget_type == "radio":
            config = {
                'text': "",  # Без тексту для радіокнопок
                'scale': self.scale_input.value(),
                'has_shadow': True  # Завжди ввімкнено
            }
            config.update(self.current_config)

            # Створюємо дві радіокнопки
            radio1 = MinecraftRadioButton("", config)
            radio2 = MinecraftRadioButton("", config)

            # Налаштовуємо групу
            radio_group = MinecraftRadioGroup()
            radio_group.add_radio_button(radio1)
            radio_group.add_radio_button(radio2)

            # Один вибраний, другий ні
            radio1.set_selected(True)
            radio2.set_selected(False)

            # Обробники подій
            radio1.clicked.connect(lambda: print("Radio 1 clicked!"))
            radio2.clicked.connect(lambda: print("Radio 2 clicked!"))
            radio1.stateChanged.connect(lambda selected: print(f"Radio 1 {'selected' if selected else 'deselected'}"))
            radio2.stateChanged.connect(lambda selected: print(f"Radio 2 {'selected' if selected else 'deselected'}"))

            # Додаємо до сітки (поруч один з одним)
            item_count = self.scroll_layout.count()
            row = item_count // 4
            col = item_count % 4

            # Створюємо контейнер для двох радіокнопок
            radio_container = QWidget()
            radio_layout = QHBoxLayout(radio_container)
            radio_layout.setSpacing(10)
            radio_layout.setContentsMargins(0, 0, 0, 0)
            radio_layout.addWidget(radio1)
            radio_layout.addWidget(radio2)

            self.scroll_layout.addWidget(radio_container, row, col)

            # Зберігаємо контейнер і групу для подальшого видалення
            self.generated_radios.extend([radio_container, radio_group])

        elif self.current_widget_type == "toggle":
            config = {
                'scale': self.scale_input.value(),
                'has_shadow': True  # Завжди ввімкнено
            }
            config.update(self.current_config)

            # Створюємо перемикач (без тексту)
            toggle = MinecraftToggleButton(config)

            # Застосовуємо вибраний патерн
            pattern_name = self.pattern_combo.currentText()
            toggle.set_pattern(pattern_name)

            toggle.clicked.connect(lambda: print("Toggle clicked!"))
            toggle.stateChanged.connect(lambda toggled: print(f"Toggle {'ON' if toggled else 'OFF'}"))

            # Додаємо до сітки
            item_count = self.scroll_layout.count()
            row = item_count // 4
            col = item_count % 4
            self.scroll_layout.addWidget(toggle, row, col)

            self.generated_toggles.append(toggle)

        elif self.current_widget_type == "slider":
            # Визначаємо розміри підложки залежно від орієнтації
            orientation = self.orientation_combo.currentText().lower()
            track_length = self.slider_length_input.value()

            if orientation == 'vertical':
                track_width = 6      # Фіксована ширина
                track_height = track_length  # Змінна висота
            else:  # horizontal
                track_width = track_length   # Змінна ширина
                track_height = 6     # Фіксована висота

            config = {
                'scale': self.scale_input.value(),
                'orientation': orientation,
                'track_width': track_width,
                'track_height': track_height,
                'has_shadow': True,
                'slider_button_config': {
                    'button_width': 8,
                    'button_height': 6,
                    'scale': self.scale_input.value(),
                    'border_color': '#413F54',
                    'animation_enabled': False,
                    'button_normal': '#9A9FB4',
                    'button_hover': '#9A9FB4',
                    'button_pressed': '#9A9FB4',
                    'border_normal': '#ADB0C4',
                    'border_hover': '#ADB0C4',
                    'border_pressed': '#ADB0C4',
                    'bottom_normal': '#9A9FB4',
                    'bottom_hover': '#9A9FB4',
                    'bottom_pressed': '#9A9FB4',
                    'text_color': 'white',
                    'font_family': 'Minecraftia',
                    'has_shadow': True
                },
                'track_border_color': '#F2F2F2',
                'track_fill_color': '#9A9FB4'
            }

            # Застосовуємо поточні стилі з пресету
            if self.current_config:
                button_config = config['slider_button_config']

                if 'button_normal' in self.current_config:
                    button_config['button_normal'] = self.current_config['button_normal']
                    button_config['button_hover'] = self.current_config['button_normal']
                    button_config['button_pressed'] = self.current_config['button_normal']

                if 'border_normal' in self.current_config:
                    button_config['border_normal'] = self.current_config['border_normal']
                    button_config['border_hover'] = self.current_config['border_normal']
                    button_config['border_pressed'] = self.current_config['border_normal']

                if 'bottom_normal' in self.current_config:
                    button_config['bottom_normal'] = self.current_config['bottom_normal']
                    button_config['bottom_hover'] = self.current_config['bottom_normal']
                    button_config['bottom_pressed'] = self.current_config['bottom_normal']

                if 'button_normal' in self.current_config:
                    config['track_fill_color'] = self.current_config['button_normal']

                if 'border_color' in self.current_config:
                    button_config['border_color'] = self.current_config['border_color']

                config['track_border_color'] = '#F2F2F2'

            # Створюємо слайдер
            slider = MinecraftSlider(config)
            slider.set_value(0.5)

            # Обробники подій
            slider.valueChanged.connect(lambda value: print(f"Slider value: {value:.2f}"))

            def on_slider_change(value):
                percentage = int(value * 100)
                length_info = f"length {track_length}px"
                print(f"Slider {orientation} ({length_info}): {percentage}%")

            slider.valueChanged.connect(on_slider_change)

            # Додаємо до сітки
            item_count = self.scroll_layout.count()
            row = item_count // 4
            col = item_count % 4
            self.scroll_layout.addWidget(slider, row, col)

            self.generated_sliders.append(slider)

            print(f"Generated {orientation} slider (length: {track_length}px) with {self.preset_combo.currentText()} preset")

    def clear_generated_buttons(self):
        """Очищення згенерованих віджетів"""
        # Очищаємо всі елементи зі scroll_layout
        for i in reversed(range(self.scroll_layout.count())):
            item = self.scroll_layout.itemAt(i)
            if item:
                widget = item.widget()
                if widget:
                    widget.deleteLater()

        self.generated_buttons.clear()
        self.generated_radios.clear()
        self.generated_toggles.clear()
        self.generated_sliders.clear()

    def save_preset(self):
        """Збереження пресету"""
        # Тут можна додати логіку збереження
        QMessageBox.information(self, "Info", "Preset saved! (Demo)")

    def export_code(self):
        """Експорт коду"""
        if self.current_widget_type == "button":
            config = {
                'button_width': self.width_input.value(),
                'button_height': self.height_input.value(),
                'scale': self.scale_input.value(),
                'animation_enabled': self.animation_check.isChecked(),
                'has_shadow': True  # Завжди ввімкнено
            }
            config.update(self.current_config)
            button_pattern_name = self.button_pattern_combo.currentText()

            code = f'''# Generated Minecraft Button Code (without text)
button_config = {config}
button = MinecraftButton("", button_config)

# Застосування патерну
button.set_pattern("{button_pattern_name}")

button.clicked.connect(lambda: print("Button clicked!"))
'''
        elif self.current_widget_type == "radio":
            config = {
                'text': "",  # Без тексту для радіокнопок
                'scale': self.scale_input.value(),
                'has_shadow': True  # Завжди ввімкнено
            }
            config.update(self.current_config)

            code = f'''# Generated Minecraft Radio Buttons Code
radio_config = {config}

# Створення двох радіокнопок
radio1 = MinecraftRadioButton("", radio_config)
radio2 = MinecraftRadioButton("", radio_config)

# Створення групи радіокнопок (тільки одна може бути вибрана)
radio_group = MinecraftRadioGroup()
radio_group.add_radio_button(radio1)
radio_group.add_radio_button(radio2)

# Встановлення початкового стану
radio1.set_selected(True)
radio2.set_selected(False)

# Обробники подій
radio1.clicked.connect(lambda: print("Radio 1 clicked!"))
radio2.clicked.connect(lambda: print("Radio 2 clicked!"))
radio1.stateChanged.connect(lambda selected: print(f"Radio 1 {{''selected'' if selected else ''deselected''}}"))
radio2.stateChanged.connect(lambda selected: print(f"Radio 2 {{''selected'' if selected else ''deselected''}}"))
'''
        elif self.current_widget_type == "toggle":
            config = {
                'scale': self.scale_input.value(),
                'has_shadow': True  # Завжди ввімкнено
            }
            config.update(self.current_config)
            pattern_name = self.pattern_combo.currentText()

            code = f'''# Generated Minecraft Toggle Switch Code
toggle_config = {config}

# Створення перемикача (без тексту)
toggle = MinecraftToggleButton(toggle_config)

# Застосування патерну
toggle.set_pattern("{pattern_name}")

# Встановлення початкового стану (за замовчуванням вимкнено)
toggle.set_toggled(False)

# Обробники подій
toggle.clicked.connect(lambda: print("Toggle clicked!"))
toggle.stateChanged.connect(lambda toggled: print(f"Toggle {{''ON'' if toggled else ''OFF''}}"))

# Перевірка стану
if toggle.is_toggled():
    print("Toggle is ON")
else:
    print("Toggle is OFF")
'''
        elif self.current_widget_type == "slider":
            # Визначаємо розміри підложки залежно від орієнтації
            orientation = self.orientation_combo.currentText().lower()
            track_length = self.slider_length_input.value()

            if orientation == 'vertical':
                track_width = 6
                track_height = track_length
            else:  # horizontal
                track_width = track_length
                track_height = 6

            config = {
                'scale': self.scale_input.value(),
                'orientation': orientation,
                'track_width': track_width,
                'track_height': track_height,
                'has_shadow': True,
                'slider_button_config': {
                    'button_width': 8,
                    'button_height': 6,
                    'scale': self.scale_input.value(),
                    'border_color': '#413F54',
                    'animation_enabled': False,
                    'button_normal': '#9A9FB4',
                    'button_hover': '#9A9FB4',
                    'button_pressed': '#9A9FB4',
                    'border_normal': '#ADB0C4',
                    'border_hover': '#ADB0C4',
                    'border_pressed': '#ADB0C4',
                    'bottom_normal': '#9A9FB4',
                    'bottom_hover': '#9A9FB4',
                    'bottom_pressed': '#9A9FB4',
                    'text_color': 'white',
                    'font_family': 'Minecraftia',
                    'has_shadow': True
                },
                'track_border_color': '#F2F2F2',
                'track_fill_color': '#9A9FB4'
            }

            # Застосовуємо поточні стилі з пресету
            if self.current_config:
                button_config = config['slider_button_config']

                if 'button_normal' in self.current_config:
                    button_config['button_normal'] = self.current_config['button_normal']
                    button_config['button_hover'] = self.current_config['button_normal']
                    button_config['button_pressed'] = self.current_config['button_normal']

                if 'border_normal' in self.current_config:
                    button_config['border_normal'] = self.current_config['border_normal']
                    button_config['border_hover'] = self.current_config['border_normal']
                    button_config['border_pressed'] = self.current_config['border_normal']

                if 'bottom_normal' in self.current_config:
                    button_config['bottom_normal'] = self.current_config['bottom_normal']
                    button_config['bottom_hover'] = self.current_config['bottom_normal']
                    button_config['bottom_pressed'] = self.current_config['bottom_normal']

                if 'button_normal' in self.current_config:
                    config['track_fill_color'] = self.current_config['button_normal']

            preset_name = self.preset_combo.currentText()

            code = f'''# Generated Minecraft Slider Code
# Preset: {preset_name}
# Orientation: {orientation}
# Track Length: {track_length} proportional pixels

slider_config = {config}

# Створення слайдера
slider = MinecraftSlider(slider_config)

# Встановлення початкового значення (50%)
slider.set_value(0.5)

# Обробник змін значення
slider.valueChanged.connect(lambda value: print(f"Slider value: {{value:.2f}}"))

# Отримання поточного значення
current_value = slider.get_value()
print(f"Current value: {{current_value:.2f}}")

# Програмна зміна значення
slider.set_value(0.75)  # Встановити на 75%

# Зміна орієнтації (якщо потрібно)
slider.set_orientation("{orientation}")  # "vertical" або "horizontal"

# Обробник події зміни значення з детальною інформацією
def on_slider_changed(value):
    print(f"Slider {{'{orientation}'}} (length: {track_length}px): {{value:.2f}} ({{value*100:.0f}}%)")

slider.valueChanged.connect(on_slider_changed)
'''

        # Показуємо код у діалозі
        dialog = QWidget()
        dialog.setWindowTitle("Generated Code")
        dialog.setGeometry(200, 200, 600, 400)
        layout = QVBoxLayout()

        code_text = QTextEdit()
        code_text.setPlainText(code)
        code_text.setStyleSheet("background-color: #F5F5F5; color: #000000; font-family: monospace;")
        layout.addWidget(code_text)

        dialog.setLayout(layout)
        dialog.show()

        # Зберігаємо посилання, щоб діалог не зник
        self.code_dialog = dialog