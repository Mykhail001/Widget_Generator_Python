"""
Головний генератор кнопок - інтерфейс програми з підтримкою Entry
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
from .minecraft_entry import MinecraftEntry

class ButtonGenerator(QWidget):
    """
    Головний генератор кнопок з підтримкою всіх віджетів
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
        self.preview_entry = None
        self.preview_group = None
        self.generated_buttons = []
        self.generated_radios = []
        self.generated_toggles = []
        self.generated_sliders = []
        self.generated_entries = []
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

        # Тип віджета - 3x2 розташування
        widget_type_group = QGroupBox("🔘 Widget Type")
        widget_type_layout = QGridLayout()

        # Перший рядок: Button, Radio Button, Entry
        self.button_radio = QCheckBox("Button")
        self.button_radio.setChecked(True)
        self.button_radio.toggled.connect(lambda checked: self.set_widget_type("button" if checked else self.get_other_widget_type("button")))
        widget_type_layout.addWidget(self.button_radio, 0, 0)

        self.radio_radio = QCheckBox("Radio Button")
        self.radio_radio.toggled.connect(lambda checked: self.set_widget_type("radio" if checked else self.get_other_widget_type("radio")))
        widget_type_layout.addWidget(self.radio_radio, 0, 1)

        self.entry_radio = QCheckBox("Entry")
        self.entry_radio.toggled.connect(lambda checked: self.set_widget_type("entry" if checked else self.get_other_widget_type("entry")))
        widget_type_layout.addWidget(self.entry_radio, 0, 2)

        # Другий рядок: Toggle Switch, Slider
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
        self.scale_input.valueChanged.connect(self.update_preview)
        basic_layout.addWidget(self.scale_input, 0, 1)

        # Розмір кнопки (в пропорційних пікселях) - тільки для звичайних кнопок
        self.size_label_width = QLabel("Button Width:")
        basic_layout.addWidget(self.size_label_width, 1, 0)
        self.width_input = QSpinBox()
        self.width_input.setRange(4, 32)
        self.width_input.setValue(16)
        self.width_input.valueChanged.connect(self.update_preview)
        basic_layout.addWidget(self.width_input, 1, 1)

        self.size_label_height = QLabel("Button Height:")
        basic_layout.addWidget(self.size_label_height, 2, 0)
        self.height_input = QSpinBox()
        self.height_input.setRange(4, 32)
        self.height_input.setValue(15)
        self.height_input.valueChanged.connect(self.update_preview)
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
        self.animation_check.toggled.connect(self.update_preview)
        options_layout.addWidget(self.animation_check)

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
        self.preview_container.setFixedSize(400, 200)
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
            "entry": self.entry_radio,
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
            self.entry_radio.setChecked(widget_type == "entry")
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
            elif widget_type == "entry":
                # Для entry приховуємо всі налаштування розмірів та патернів
                self.size_label_width.hide()
                self.size_label_height.hide()
                self.width_input.hide()
                self.height_input.hide()
                self.orientation_label.hide()
                self.orientation_combo.hide()
                self.slider_length_label.hide()
                self.slider_length_input.hide()
                # Приховуємо всі патерни
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
        for widget in [self.preview_button, self.preview_radio, self.preview_radio2,
                      self.preview_toggle, self.preview_slider, self.preview_entry]:
            if widget:
                widget.deleteLater()

        self.preview_button = None
        self.preview_radio = None
        self.preview_radio2 = None
        self.preview_toggle = None
        self.preview_slider = None
        self.preview_entry = None

        # Створюємо конфігурацію залежно від типу віджета
        if self.current_widget_type == "button":
            config = {
                'button_width': self.width_input.value(),
                'button_height': self.height_input.value(),
                'scale': self.scale_input.value(),
                'animation_enabled': self.animation_check.isChecked(),
                'has_shadow': True
            }
            config.update(self.current_config)

            self.preview_button = MinecraftButton('', config, self.preview_container)
            button_pattern_name = self.button_pattern_combo.currentText()
            self.preview_button.set_pattern(button_pattern_name)

            self.preview_button.move(
                (self.preview_container.width() - self.preview_button.width()) // 2,
                (self.preview_container.height() - self.preview_button.height()) // 2
            )
            self.preview_button.show()

        elif self.current_widget_type == "radio":
            config = {
                'text': "",
                'scale': self.scale_input.value(),
                'has_shadow': True
            }
            config.update(self.current_config)

            self.preview_radio = MinecraftRadioButton("", config, self.preview_container)
            self.preview_radio2 = MinecraftRadioButton("", config, self.preview_container)

            radio_spacing = 20
            total_width = self.preview_radio.width() * 2 + radio_spacing
            start_x = (self.preview_container.width() - total_width) // 2
            y_pos = (self.preview_container.height() - self.preview_radio.height()) // 2

            self.preview_radio.move(start_x, y_pos)
            self.preview_radio2.move(start_x + self.preview_radio.width() + radio_spacing, y_pos)

            self.preview_radio.set_selected(True)
            self.preview_radio2.set_selected(False)

            self.preview_group = MinecraftRadioGroup()
            self.preview_group.add_radio_button(self.preview_radio)
            self.preview_group.add_radio_button(self.preview_radio2)

            self.preview_radio.show()
            self.preview_radio2.show()

        elif self.current_widget_type == "entry":
            config = {
                'entry_width': 50,  # Компактна ширина
                'entry_height': 10, # Компактна висота з відступом знизу
                'scale': self.scale_input.value(),
                'placeholder': "Sample text..."
            }
            config.update(self.current_config)

            self.preview_entry = MinecraftEntry(placeholder="Sample text...", style_config=config, parent=self.preview_container)

            self.preview_entry.move(
                (self.preview_container.width() - self.preview_entry.width()) // 2,
                (self.preview_container.height() - self.preview_entry.height()) // 2
            )
            self.preview_entry.show()

        elif self.current_widget_type == "toggle":
            config = {
                'scale': self.scale_input.value(),
                'has_shadow': True
            }
            config.update(self.current_config)

            self.preview_toggle = MinecraftToggleButton(config, self.preview_container)
            pattern_name = self.pattern_combo.currentText()
            self.preview_toggle.set_pattern(pattern_name)

            self.preview_toggle.move(
                (self.preview_container.width() - self.preview_toggle.width()) // 2,
                (self.preview_container.height() - self.preview_toggle.height()) // 2
            )
            self.preview_toggle.show()

        elif self.current_widget_type == "slider":
            orientation = self.orientation_combo.currentText().lower()
            track_length = self.slider_length_input.value()

            if orientation == 'vertical':
                track_width = 6
                track_height = track_length
            else:
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
                    'animation_enabled': False
                }
            }

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
            self.update_preview()

    def apply_button_pattern(self, pattern_name):
        """Застосування патерну для кнопки"""
        if self.current_widget_type == "button" and self.preview_button:
            self.preview_button.set_pattern(pattern_name)

    def generate_widget(self):
        """Генерація нового віджета"""
        if self.current_widget_type == "button":
            config = {
                'button_width': self.width_input.value(),
                'button_height': self.height_input.value(),
                'scale': self.scale_input.value(),
                'animation_enabled': self.animation_check.isChecked(),
                'has_shadow': True
            }
            config.update(self.current_config)

            button = MinecraftButton('', config)
            button_pattern_name = self.button_pattern_combo.currentText()
            button.set_pattern(button_pattern_name)
            button.clicked.connect(lambda: print("Button clicked!"))

            item_count = self.scroll_layout.count()
            row = item_count // 4
            col = item_count % 4
            self.scroll_layout.addWidget(button, row, col)
            self.generated_buttons.append(button)

        elif self.current_widget_type == "radio":
            config = {
                'text': "",
                'scale': self.scale_input.value(),
                'has_shadow': True
            }
            config.update(self.current_config)

            radio1 = MinecraftRadioButton("", config)
            radio2 = MinecraftRadioButton("", config)

            radio_group = MinecraftRadioGroup()
            radio_group.add_radio_button(radio1)
            radio_group.add_radio_button(radio2)

            radio1.set_selected(True)
            radio2.set_selected(False)

            radio1.clicked.connect(lambda: print("Radio 1 clicked!"))
            radio2.clicked.connect(lambda: print("Radio 2 clicked!"))
            radio1.stateChanged.connect(lambda selected: print(f"Radio 1 {'selected' if selected else 'deselected'}"))
            radio2.stateChanged.connect(lambda selected: print(f"Radio 2 {'selected' if selected else 'deselected'}"))

            item_count = self.scroll_layout.count()
            row = item_count // 4
            col = item_count % 4

            radio_container = QWidget()
            radio_layout = QHBoxLayout(radio_container)
            radio_layout.setSpacing(10)
            radio_layout.setContentsMargins(0, 0, 0, 0)
            radio_layout.addWidget(radio1)
            radio_layout.addWidget(radio2)

            self.scroll_layout.addWidget(radio_container, row, col)
            self.generated_radios.extend([radio_container, radio_group])

        elif self.current_widget_type == "entry":
            config = {
                'entry_width': 60,
                'entry_height': 12,
                'scale': self.scale_input.value(),
                'placeholder': "Enter text..."
            }
            config.update(self.current_config)

            entry = MinecraftEntry(placeholder="Enter text...", style_config=config)
            entry.textChanged.connect(lambda text: print(f"Entry text changed: {text}"))
            entry.returnPressed.connect(lambda: print(f"Entry submitted: {entry.get_text()}"))

            item_count = self.scroll_layout.count()
            row = item_count // 4
            col = item_count % 4
            self.scroll_layout.addWidget(entry, row, col)

            self.generated_entries.append(entry)
            print(f"Generated Entry with {self.preset_combo.currentText()} preset")

        elif self.current_widget_type == "toggle":
            config = {
                'scale': self.scale_input.value(),
                'has_shadow': True
            }
            config.update(self.current_config)

            toggle = MinecraftToggleButton(config)
            pattern_name = self.pattern_combo.currentText()
            toggle.set_pattern(pattern_name)

            toggle.clicked.connect(lambda: print("Toggle clicked!"))
            toggle.stateChanged.connect(lambda toggled: print(f"Toggle {'ON' if toggled else 'OFF'}"))

            item_count = self.scroll_layout.count()
            row = item_count // 4
            col = item_count % 4
            self.scroll_layout.addWidget(toggle, row, col)
            self.generated_toggles.append(toggle)

        elif self.current_widget_type == "slider":
            orientation = self.orientation_combo.currentText().lower()
            track_length = self.slider_length_input.value()

            if orientation == 'vertical':
                track_width = 6
                track_height = track_length
            else:
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

            slider = MinecraftSlider(config)
            slider.set_value(0.5)
            slider.valueChanged.connect(lambda value: print(f"Slider value: {value:.2f}"))

            def on_slider_change(value):
                percentage = int(value * 100)
                length_info = f"length {track_length}px"
                print(f"Slider {orientation} ({length_info}): {percentage}%")

            slider.valueChanged.connect(on_slider_change)

            item_count = self.scroll_layout.count()
            row = item_count // 4
            col = item_count % 4
            self.scroll_layout.addWidget(slider, row, col)
            self.generated_sliders.append(slider)

            print(f"Generated {orientation} slider (length: {track_length}px) with {self.preset_combo.currentText()} preset")

    def clear_generated_buttons(self):
        """Очищення згенерованих віджетів"""
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
        self.generated_entries.clear()

    def save_preset(self):
        """Збереження пресету"""
        QMessageBox.information(self, "Info", "Preset saved! (Demo)")

    def export_code(self):
        """Експорт коду"""
        if self.current_widget_type == "button":
            config = {
                'button_width': self.width_input.value(),
                'button_height': self.height_input.value(),
                'scale': self.scale_input.value(),
                'animation_enabled': self.animation_check.isChecked(),
                'has_shadow': True
            }
            config.update(self.current_config)
            button_pattern_name = self.button_pattern_combo.currentText()
            preset_name = self.preset_combo.currentText()

            code = f'''# Generated Minecraft Button Code
# Preset: {preset_name}
# Pattern: {button_pattern_name}
# Size: {self.width_input.value()}x{self.height_input.value()} proportional pixels

from widgets.minecraft_button import MinecraftButton

button_config = {config}

# Створення кнопки (без тексту)
button = MinecraftButton("", button_config)

# Застосування патерну
button.set_pattern("{button_pattern_name}")

# Обробник натискання
button.clicked.connect(lambda: print("Button clicked!"))

# Програмне керування кнопкою
button.setEnabled(True)   # Увімкнути/вимкнути кнопку
button.show()             # Показати кнопку

# Зміна патерну програмно
available_patterns = ["None", "Configure", "Question", "Message", "Point 1", "Plus", "Arrow Up", "Arrow Down"]
button.set_pattern("Configure")  # Змінити патерн
'''

        elif self.current_widget_type == "radio":
            config = {
                'text': "",
                'scale': self.scale_input.value(),
                'has_shadow': True
            }
            config.update(self.current_config)
            preset_name = self.preset_combo.currentText()

            code = f'''# Generated Minecraft Radio Buttons Code
# Preset: {preset_name}

from widgets.minecraft_radio_button import MinecraftRadioButton, MinecraftRadioGroup

radio_config = {config}

# Створення двох радіокнопок
radio1 = MinecraftRadioButton("Option 1", radio_config)
radio2 = MinecraftRadioButton("Option 2", radio_config)

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
radio1.stateChanged.connect(lambda selected: print(f"Radio 1 {{'selected' if selected else 'deselected'}}"))
radio2.stateChanged.connect(lambda selected: print(f"Radio 2 {{'selected' if selected else 'deselected'}}"))

# Програмне керування
def select_option(option_number):
    if option_number == 1:
        radio1.set_selected(True)
    elif option_number == 2:
        radio2.set_selected(True)

# Перевірка вибраної опції
selected_radio = radio_group.get_selected()
if selected_radio == radio1:
    print("Option 1 is selected")
elif selected_radio == radio2:
    print("Option 2 is selected")

# Очищення вибору
radio_group.clear_selection()
'''

        elif self.current_widget_type == "entry":
            config = {
                'entry_width': 60,  # Компактна ширина
                'entry_height': 10, # Компактна висота з відступом знизу
                'scale': self.scale_input.value(),
                'placeholder': "Enter text..."
            }
            config.update(self.current_config)
            preset_name = self.preset_combo.currentText()
            scale_value = self.scale_input.value()
            calculated_font_size = scale_value * 4

            code = f'''# Generated Minecraft Entry Code
# Preset: {preset_name}
# Size: 50x10 proportional pixels (with 2px bottom margin)
# Scale: {scale_value} (Font size: {calculated_font_size} - auto-calculated)

from widgets.minecraft_entry import MinecraftEntry

entry_config = {config}

# Створення текстового поля
# Розмір шрифту автоматично обчислюється як: scale * 6
# Scale {scale_value} → Font size {calculated_font_size}
# Має відступ знизу 2 пропорційних пікселя
entry = MinecraftEntry("Enter text...", entry_config)

# Встановлення placeholder тексту
entry.set_placeholder("Your placeholder here")

# Обробники подій
entry.textChanged.connect(lambda text: print(f"Text changed: {{text}}"))
entry.returnPressed.connect(lambda: print(f"Enter pressed: {{entry.get_text()}}"))

# Програмна робота з текстом
entry.set_text("Some initial text")  # Встановити текст
current_text = entry.get_text()      # Отримати поточний текст
entry.clear()                        # Очистити текст

# Режим тільки для читання (опціонально)
entry.set_readonly(False)  # True для режиму читання

# Розширені обробники подій
def on_text_changed(text):
    print(f"Entry text: {{text}}")
    if len(text) > 50:
        print("Warning: Text is getting long!")

def on_enter_pressed():
    text = entry.get_text()
    if text.strip():  # Перевіряємо, чи не порожній текст
        print(f"Submitted: {{text}}")
        entry.clear()  # Очистити після відправки
    else:
        print("Cannot submit empty text!")

entry.textChanged.connect(on_text_changed)
entry.returnPressed.connect(on_enter_pressed)

# Валідація тексту
def validate_input():
    text = entry.get_text()
    if not text:
        return False, "Text is required"
    if len(text) < 3:
        return False, "Text must be at least 3 characters"
    return True, "Valid input"

# Використання валідації
is_valid, message = validate_input()
print(f"Validation: {{message}}")

# Примітка: При scale {scale_value} розмір шрифту автоматично встановлюється на {calculated_font_size}
# Формула: font_size = scale * 6
# Текстове поле має відступ знизу 2 пропорційних пікселя для кращого вигляду
'''

        elif self.current_widget_type == "toggle":
            config = {
                'scale': self.scale_input.value(),
                'has_shadow': True
            }
            config.update(self.current_config)
            pattern_name = self.pattern_combo.currentText()
            preset_name = self.preset_combo.currentText()

            code = f'''# Generated Minecraft Toggle Switch Code
# Preset: {preset_name}
# Pattern: {pattern_name}

from widgets.minecraft_toggle_button import MinecraftToggleButton

toggle_config = {config}

# Створення перемикача
toggle = MinecraftToggleButton(toggle_config)

# Застосування патерну
toggle.set_pattern("{pattern_name}")

# Встановлення початкового стану (за замовчуванням вимкнено)
toggle.set_toggled(False)

# Обробники подій
toggle.clicked.connect(lambda: print("Toggle clicked!"))
toggle.stateChanged.connect(lambda toggled: print(f"Toggle {{'ON' if toggled else 'OFF'}}"))

# Програмне керування
def toggle_on():
    toggle.set_toggled(True)
    print("Toggle turned ON programmatically")

def toggle_off():
    toggle.set_toggled(False)
    print("Toggle turned OFF programmatically")

def toggle_switch():
    current_state = toggle.is_toggled()
    toggle.set_toggled(not current_state)
    print(f"Toggle switched to {{'ON' if not current_state else 'OFF'}}")

# Перевірка стану
if toggle.is_toggled():
    print("Toggle is currently ON")
else:
    print("Toggle is currently OFF")

# Розширений обробник з логікою
def on_toggle_changed(is_on):
    if is_on:
        print("Feature enabled!")
        # Тут можна додати логіку для увімкненого стану
    else:
        print("Feature disabled!")
        # Тут можна додати логіку для вимкненого стану

toggle.stateChanged.connect(on_toggle_changed)

# Зміна патерну програмно
available_patterns = ["None", "Standard"]
toggle.set_pattern("Standard")  # Застосувати інший патерн
'''

        elif self.current_widget_type == "slider":
            orientation = self.orientation_combo.currentText().lower()
            track_length = self.slider_length_input.value()
            preset_name = self.preset_combo.currentText()

            if orientation == 'vertical':
                track_width = 6
                track_height = track_length
            else:
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

            code = f'''# Generated Minecraft Slider Code
# Preset: {preset_name}
# Orientation: {orientation}
# Track Length: {track_length} proportional pixels

from widgets.minecraft_slider import MinecraftSlider

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
slider.set_value(0.0)   # Мінімальне значення
slider.set_value(1.0)   # Максимальне значення

# Зміна орієнтації (якщо потрібно)
slider.set_orientation("{orientation}")  # "vertical" або "horizontal"

# Розширений обробник подій з детальною інформацією
def on_slider_changed(value):
    percentage = int(value * 100)
    print(f"Slider {orientation} (length: {track_length}px): {{value:.2f}} ({{percentage}}%)")
    
    # Додаткова логіка залежно від значення
    if value < 0.25:
        print("Low range")
    elif value < 0.75:
        print("Medium range")
    else:
        print("High range")

slider.valueChanged.connect(on_slider_changed)

# Створення функцій для конкретних значень
def set_minimum():
    slider.set_value(0.0)

def set_maximum():
    slider.set_value(1.0)

def set_middle():
    slider.set_value(0.5)

def increment_by_10_percent():
    current = slider.get_value()
    new_value = min(1.0, current + 0.1)
    slider.set_value(new_value)

def decrement_by_10_percent():
    current = slider.get_value()
    new_value = max(0.0, current - 0.1)
    slider.set_value(new_value)

# Встановлення значення з валідацією
def set_value_safe(value):
    if 0.0 <= value <= 1.0:
        slider.set_value(value)
        return True
    else:
        print(f"Invalid value: {{value}}. Must be between 0.0 and 1.0")
        return False

# Приклад використання
set_value_safe(0.8)  # Валідне значення
set_value_safe(1.5)  # Неваліне значення
'''
        else:
            code = f"# Export for {self.current_widget_type} not implemented yet"

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

        self.code_dialog = dialog