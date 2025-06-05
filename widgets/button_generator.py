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

from managers import PatternManager, ButtonPatternManager, ButtonPresetManager
from .minecraft_button import MinecraftButton
from .minecraft_radio_button import MinecraftRadioButton, MinecraftRadioGroup
from .minecraft_toggle_button import MinecraftToggleButton

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
        self.preview_group = None
        self.generated_buttons = []
        self.generated_radios = []
        self.generated_toggles = []
        self.code_dialog = None

        # ДОДАЙТЕ ЦЕ - виклик setup_ui()
        self.setup_ui()
    def setup_ui(self):
        """Налаштування інтерфейсу"""
        main_layout = QHBoxLayout()

        # Ліва панель - настройки
        left_panel = self.create_settings_panel()
        main_layout.addWidget(left_panel, 1)

        # Права панель - превью та генеровані кнопки
        right_panel = self.create_preview_panel()
        main_layout.addWidget(right_panel, 2)

        self.setLayout(main_layout)
    def create_settings_panel(self):
        """Створення панелі налаштувань"""
        settings_widget = QWidget()
        settings_widget.setMaximumWidth(400)
        settings_widget.setStyleSheet("background-color: #3C3C3C; border-radius: 10px; padding: 10px;")

        layout = QVBoxLayout()

        # Заголовок
        title = QLabel("⚙️ WIDGET CONFIGURATOR")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #4CAF50; padding: 10px;")
        layout.addWidget(title)

        # Тип віджета
        widget_type_group = QGroupBox("🔘 Widget Type")
        widget_type_layout = QHBoxLayout()

        self.button_radio = QCheckBox("Button")
        self.button_radio.setChecked(True)
        self.button_radio.toggled.connect(lambda checked: self.set_widget_type("button" if checked else self.get_other_widget_type("button")))
        widget_type_layout.addWidget(self.button_radio)

        self.radio_radio = QCheckBox("Radio Button")
        self.radio_radio.toggled.connect(lambda checked: self.set_widget_type("radio" if checked else self.get_other_widget_type("radio")))
        widget_type_layout.addWidget(self.radio_radio)

        self.toggle_radio = QCheckBox("Toggle Switch")
        self.toggle_radio.toggled.connect(lambda checked: self.set_widget_type("toggle" if checked else self.get_other_widget_type("toggle")))
        widget_type_layout.addWidget(self.toggle_radio)

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
        self.pattern_combo.addItems(PatternManager.get_patterns().keys())
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

        self.scroll_area = QScrollArea()
        self.scroll_content = QWidget()
        self.scroll_layout = QGridLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background-color: #CBCCD4;")

        generated_layout = QVBoxLayout()
        generated_layout.addWidget(self.scroll_area)

        clear_btn = QPushButton("🗑️ Clear All")
        clear_btn.clicked.connect(self.clear_generated_buttons)
        generated_layout.addWidget(clear_btn)

        generated_group.setLayout(generated_layout)
        layout.addWidget(generated_group)

        preview_widget.setLayout(layout)
        return preview_widget

    def get_other_widget_type(self, unchecked_type):
        """Повертає інший тип віджета коли один був відключений"""
        if unchecked_type == "button":
            if self.radio_radio.isChecked():
                return "radio"
            elif self.toggle_radio.isChecked():
                return "toggle"
            else:
                return "button"  # fallback
        elif unchecked_type == "radio":
            if self.button_radio.isChecked():
                return "button"
            elif self.toggle_radio.isChecked():
                return "toggle"
            else:
                return "button"  # fallback
        elif unchecked_type == "toggle":
            if self.button_radio.isChecked():
                return "button"
            elif self.radio_radio.isChecked():
                return "radio"
            else:
                return "button"  # fallback
        return "button"  # fallback

    def set_widget_type(self, widget_type):
        """Встановлення типу віджета"""
        if widget_type != self.current_widget_type:
            self.current_widget_type = widget_type

            # Оновлюємо checkboxes (тільки один може бути вибраний)
            self.button_radio.setChecked(widget_type == "button")
            self.radio_radio.setChecked(widget_type == "radio")
            self.toggle_radio.setChecked(widget_type == "toggle")

            # Показуємо/приховуємо налаштування залежно від типу
            if widget_type == "button":
                # Для кнопок показуємо тільки розміри
                self.size_label_width.show()
                self.size_label_height.show()
                self.width_input.show()
                self.height_input.show()
                # Показуємо патерни для кнопок, приховуємо для toggle
                self.button_pattern_group.show()
                self.pattern_group.hide()
            elif widget_type == "radio":
                # Приховуємо налаштування для радіокнопок
                self.size_label_width.hide()
                self.size_label_height.hide()
                self.width_input.hide()
                self.height_input.hide()
                # Приховуємо всі патерни для radio
                self.button_pattern_group.hide()
                self.pattern_group.hide()
            elif widget_type == "toggle":
                # Для перемикача приховуємо всі налаштування розмірів
                self.size_label_width.hide()
                self.size_label_height.hide()
                self.width_input.hide()
                self.height_input.hide()
                # Показуємо патерни для toggle switch, приховуємо для кнопок
                self.button_pattern_group.hide()
                self.pattern_group.show()

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

        # Показуємо код у діалозі
        dialog = QWidget()
        dialog.setWindowTitle("Generated Code")
        dialog.setGeometry(200, 200, 600, 400)
        layout = QVBoxLayout()

        code_text = QTextEdit()
        code_text.setPlainText(code)
        code_text.setStyleSheet("background-color: #1E1E1E; color: #FFFFFF; font-family: monospace;")
        layout.addWidget(code_text)

        dialog.setLayout(layout)
        dialog.show()

        # Зберігаємо посилання, щоб діалог не зник
        self.code_dialog = dialog

