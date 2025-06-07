"""
Main button generator - program interface with Entry support
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

class WidgetGenerator(QWidget):
    """
    Main button generator with support for all widgets
    """

    def __init__(self):
        super().__init__()

        # Initialize variables
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
        """Setup interface"""
        main_layout = QHBoxLayout()

        # Left panel - settings
        left_panel = self.create_settings_panel()
        main_layout.addWidget(left_panel, 1)

        # Right panel - preview and generated buttons
        right_panel = self.create_preview_panel()
        main_layout.addWidget(right_panel, 2)

        self.setLayout(main_layout)
        self.setStyleSheet("background-color: #2C2C2C;")

        self.update_preview()

    def create_settings_panel(self):
        """Create settings panel"""
        settings_widget = QWidget()
        settings_widget.setMaximumWidth(400)
        settings_widget.setStyleSheet("background-color: #3C3C3C; border-radius: 10px; padding: 10px; color: white;")
        layout = QVBoxLayout()

        # Title
        title = QLabel("⚙️ WIDGET CONFIGURATOR")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #4CAF50; padding: 10px;")
        layout.addWidget(title)

        # Widget type - 3x2 layout
        widget_type_group = QGroupBox("🔘 Widget Type")
        widget_type_layout = QGridLayout()

        # First row: Button, Radio Button, Entry
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

        # Second row: Toggle Switch, Slider
        self.toggle_radio = QCheckBox("Toggle Switch")
        self.toggle_radio.toggled.connect(lambda checked: self.set_widget_type("toggle" if checked else self.get_other_widget_type("toggle")))
        widget_type_layout.addWidget(self.toggle_radio, 1, 0)

        self.slider_radio = QCheckBox("Slider")
        self.slider_radio.toggled.connect(lambda checked: self.set_widget_type("slider" if checked else self.get_other_widget_type("slider")))
        widget_type_layout.addWidget(self.slider_radio, 1, 1)

        widget_type_group.setLayout(widget_type_layout)
        layout.addWidget(widget_type_group)

        # Basic settings
        basic_group = QGroupBox("🔧 Basic Settings")
        basic_layout = QGridLayout()

        # Scale
        basic_layout.addWidget(QLabel("Scale:"), 0, 0)
        self.scale_input = QSpinBox()
        self.scale_input.setRange(4, 16)
        self.scale_input.setValue(8)
        self.scale_input.valueChanged.connect(self.update_preview)
        basic_layout.addWidget(self.scale_input, 0, 1)

        # Button size (in proportional pixels) - only for regular buttons
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

        # Entry width - only for Entry widgets
        self.entry_width_label = QLabel("Entry Width:")
        basic_layout.addWidget(self.entry_width_label, 3, 0)
        self.entry_width_input = QSpinBox()
        self.entry_width_input.setRange(20, 100)
        self.entry_width_input.setValue(60)
        self.entry_width_input.valueChanged.connect(self.update_preview)
        basic_layout.addWidget(self.entry_width_input, 3, 1)

        # Slider orientation
        self.orientation_label = QLabel("Orientation:")
        basic_layout.addWidget(self.orientation_label, 4, 0)
        self.orientation_combo = QComboBox()
        self.orientation_combo.addItems(["Vertical", "Horizontal"])
        self.orientation_combo.currentTextChanged.connect(self.update_preview)
        basic_layout.addWidget(self.orientation_combo, 4, 1)

        # Slider length
        self.slider_length_label = QLabel("Track Length:")
        basic_layout.addWidget(self.slider_length_label, 5, 0)
        self.slider_length_input = QSpinBox()
        self.slider_length_input.setRange(10, 60)
        self.slider_length_input.setValue(30)
        self.slider_length_input.valueChanged.connect(self.update_preview)
        basic_layout.addWidget(self.slider_length_input, 5, 1)

        # Hide entry width fields by default
        self.entry_width_label.hide()
        self.entry_width_input.hide()

        # Hide slider fields by default
        self.orientation_label.hide()
        self.orientation_combo.hide()
        self.slider_length_label.hide()
        self.slider_length_input.hide()

        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)

        # Set initial widget type (after connecting signals)
        self.set_widget_type("button")

        # Presets
        preset_group = QGroupBox("🎨 Style Presets")
        preset_layout = QVBoxLayout()

        self.preset_combo = QComboBox()
        self.preset_combo.addItems(ButtonPresetManager.get_presets().keys())
        self.preset_combo.currentTextChanged.connect(self.apply_preset)
        preset_layout.addWidget(self.preset_combo)

        preset_group.setLayout(preset_layout)
        layout.addWidget(preset_group)

        # Patterns (only for toggle switch)
        self.pattern_group = QGroupBox("🎨 Toggle Patterns")
        pattern_layout = QVBoxLayout()

        self.pattern_combo = QComboBox()
        self.pattern_combo.addItems(TogglePatternManager.get_patterns().keys())
        self.pattern_combo.setCurrentText('Standard')  # Default standard pattern
        self.pattern_combo.currentTextChanged.connect(self.apply_pattern)
        pattern_layout.addWidget(self.pattern_combo)

        self.pattern_group.setLayout(pattern_layout)
        layout.addWidget(self.pattern_group)
        self.pattern_group.hide()  # Initially hidden

        # Button patterns (only for button)
        self.button_pattern_group = QGroupBox("🎨 Button Patterns")
        button_pattern_layout = QVBoxLayout()

        self.button_pattern_combo = QComboBox()
        self.button_pattern_combo.addItems(ButtonPatternManager.get_patterns().keys())
        self.button_pattern_combo.setCurrentText('None')  # No pattern by default
        self.button_pattern_combo.currentTextChanged.connect(self.apply_button_pattern)
        button_pattern_layout.addWidget(self.button_pattern_combo)

        self.button_pattern_group.setLayout(button_pattern_layout)
        layout.addWidget(self.button_pattern_group)
        self.button_pattern_group.show()  # Shown for buttons by default

        # Options
        options_group = QGroupBox("⚡ Options")
        options_layout = QVBoxLayout()

        self.animation_check = QCheckBox("Enable Press Animation")
        self.animation_check.setChecked(True)
        self.animation_check.toggled.connect(self.update_preview)
        options_layout.addWidget(self.animation_check)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Action buttons
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
        """Create preview panel"""
        preview_widget = QWidget()
        layout = QVBoxLayout()

        # Preview
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

        # Generated widgets
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
        """Return another widget type when one was unchecked"""
        checkboxes = {
            "button": self.button_radio,
            "radio": self.radio_radio,
            "entry": self.entry_radio,
            "toggle": self.toggle_radio,
            "slider": self.slider_radio
        }

        # Find first selected checkbox (except the one that was unchecked)
        for widget_type, checkbox in checkboxes.items():
            if widget_type != unchecked_type and checkbox.isChecked():
                return widget_type
        return "button"

    def set_widget_type(self, widget_type):
        """Set widget type"""
        if widget_type != self.current_widget_type:
            self.current_widget_type = widget_type

            # Update checkboxes (only one can be selected)
            self.button_radio.setChecked(widget_type == "button")
            self.radio_radio.setChecked(widget_type == "radio")
            self.entry_radio.setChecked(widget_type == "entry")
            self.toggle_radio.setChecked(widget_type == "toggle")
            self.slider_radio.setChecked(widget_type == "slider")

            # Show/hide settings depending on type
            if widget_type == "button":
                # For buttons show size settings
                self.size_label_width.show()
                self.size_label_height.show()
                self.width_input.show()
                self.height_input.show()
                self.entry_width_label.hide()
                self.entry_width_input.hide()
                self.orientation_label.hide()
                self.orientation_combo.hide()
                self.slider_length_label.hide()
                self.slider_length_input.hide()
                # Show button patterns, hide toggle patterns
                self.button_pattern_group.show()
                self.pattern_group.hide()
            elif widget_type == "radio":
                # Hide settings for radio buttons
                self.size_label_width.hide()
                self.size_label_height.hide()
                self.width_input.hide()
                self.height_input.hide()
                self.entry_width_label.hide()
                self.entry_width_input.hide()
                self.orientation_label.hide()
                self.orientation_combo.hide()
                self.slider_length_label.hide()
                self.slider_length_input.hide()
                # Hide all patterns for radio
                self.button_pattern_group.hide()
                self.pattern_group.hide()
            elif widget_type == "entry":
                # For entry hide all size settings and patterns, show entry width
                self.size_label_width.hide()
                self.size_label_height.hide()
                self.width_input.hide()
                self.height_input.hide()
                self.entry_width_label.show()
                self.entry_width_input.show()
                self.orientation_label.hide()
                self.orientation_combo.hide()
                self.slider_length_label.hide()
                self.slider_length_input.hide()
                # Hide all patterns
                self.button_pattern_group.hide()
                self.pattern_group.hide()
            elif widget_type == "toggle":
                # For toggle hide all size settings
                self.size_label_width.hide()
                self.size_label_height.hide()
                self.width_input.hide()
                self.height_input.hide()
                self.entry_width_label.hide()
                self.entry_width_input.hide()
                self.orientation_label.hide()
                self.orientation_combo.hide()
                self.slider_length_label.hide()
                self.slider_length_input.hide()
                # Show toggle patterns, hide button patterns
                self.button_pattern_group.hide()
                self.pattern_group.show()
            elif widget_type == "slider":
                # For slider hide sizes, show orientation and length
                self.size_label_width.hide()
                self.size_label_height.hide()
                self.width_input.hide()
                self.height_input.hide()
                self.entry_width_label.hide()
                self.entry_width_input.hide()
                self.orientation_label.show()
                self.orientation_combo.show()
                self.slider_length_label.show()
                self.slider_length_input.show()
                # Hide all patterns
                self.button_pattern_group.hide()
                self.pattern_group.hide()

            self.update_preview()

    def update_preview(self):
        """Update widget preview"""
        # Remove old widgets
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

        # Create configuration depending on widget type
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
                'entry_width': self.entry_width_input.value(),
                'entry_height': 10,
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
        """Apply preset"""
        presets = ButtonPresetManager.get_presets()
        if preset_name in presets:
            self.current_config.update(presets[preset_name])
            self.update_preview()

    def apply_pattern(self, pattern_name):
        """Apply pattern for toggle switch"""
        if self.current_widget_type == "toggle" and self.preview_toggle:
            self.preview_toggle.set_pattern(pattern_name)
            self.update_preview()

    def apply_button_pattern(self, pattern_name):
        """Apply pattern for button"""
        if self.current_widget_type == "button" and self.preview_button:
            self.preview_button.set_pattern(pattern_name)

    def generate_widget(self):
        """Generate new widget"""
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
                'entry_width': self.entry_width_input.value(),
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
            print(f"Generated Entry (width: {self.entry_width_input.value()}px) with {self.preset_combo.currentText()} preset")

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
        """Clear generated widgets"""
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
        """Save preset"""
        QMessageBox.information(self, "Info", "Preset saved! (Demo)")

    def export_code(self):
        """Export code"""
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

# Create button (without text)
button = MinecraftButton("", button_config)

# Apply pattern
button.set_pattern("{button_pattern_name}")

# Click handler
button.clicked.connect(lambda: print("Button clicked!"))

# Programmatic button control
button.setEnabled(True)   # Enable/disable button
button.show()             # Show button

# Change pattern programmatically
available_patterns = ["None", "Configure", "Question", "Message", "Point 1", "Plus", "Arrow Up", "Arrow Down"]
button.set_pattern("Configure")  # Change pattern
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

# Create two radio buttons
radio1 = MinecraftRadioButton("Option 1", radio_config)
radio2 = MinecraftRadioButton("Option 2", radio_config)

# Create radio group (only one can be selected)
radio_group = MinecraftRadioGroup()
radio_group.add_radio_button(radio1)
radio_group.add_radio_button(radio2)

# Set initial state
radio1.set_selected(True)
radio2.set_selected(False)

# Event handlers
radio1.clicked.connect(lambda: print("Radio 1 clicked!"))
radio2.clicked.connect(lambda: print("Radio 2 clicked!"))
radio1.stateChanged.connect(lambda selected: print(f"Radio 1 {{'selected' if selected else 'deselected'}}"))
radio2.stateChanged.connect(lambda selected: print(f"Radio 2 {{'selected' if selected else 'deselected'}}"))

# Programmatic control
def select_option(option_number):
    if option_number == 1:
        radio1.set_selected(True)
    elif option_number == 2:
        radio2.set_selected(True)

# Check selected option
selected_radio = radio_group.get_selected()
if selected_radio == radio1:
    print("Option 1 is selected")
elif selected_radio == radio2:
    print("Option 2 is selected")

# Clear selection
radio_group.clear_selection()
'''

        elif self.current_widget_type == "entry":
            config = {
                'entry_width': self.entry_width_input.value(),
                'entry_height': 10,
                'scale': self.scale_input.value(),
                'placeholder': "Enter text..."
            }
            config.update(self.current_config)
            preset_name = self.preset_combo.currentText()
            scale_value = self.scale_input.value()
            calculated_font_size = scale_value * 4
            entry_width = self.entry_width_input.value()

            code = f'''# Generated Minecraft Entry Code
# Preset: {preset_name}
# Size: {entry_width}x10 proportional pixels (with 2px bottom margin)
# Scale: {scale_value} (Font size: {calculated_font_size} - auto-calculated)

from widgets.minecraft_entry import MinecraftEntry

entry_config = {config}

# Create text field
# Font size automatically calculated as: scale * 4
# Scale {scale_value} → Font size {calculated_font_size}
# Has bottom margin of 2 proportional pixels
entry = MinecraftEntry("Enter text...", entry_config)

# Set placeholder text
entry.set_placeholder("Your placeholder here")

# Event handlers
entry.textChanged.connect(lambda text: print(f"Text changed: {{text}}"))
entry.returnPressed.connect(lambda: print(f"Enter pressed: {{entry.get_text()}}"))

# Programmatic text operations
entry.set_text("Some initial text")  # Set text
current_text = entry.get_text()      # Get current text
entry.clear()                        # Clear text

# Read-only mode (optional)
entry.set_readonly(False)  # True for read-only mode

# Advanced event handlers
def on_text_changed(text):
    print(f"Entry text: {{text}}")
    if len(text) > 50:
        print("Warning: Text is getting long!")

def on_enter_pressed():
    text = entry.get_text()
    if text.strip():  # Check if text is not empty
        print(f"Submitted: {{text}}")
        entry.clear()  # Clear after submission
    else:
        print("Cannot submit empty text!")

entry.textChanged.connect(on_text_changed)
entry.returnPressed.connect(on_enter_pressed)

# Text validation
def validate_input():
    text = entry.get_text()
    if not text:
        return False, "Text is required"
    if len(text) < 3:
        return False, "Text must be at least 3 characters"
    return True, "Valid input"

# Using validation
is_valid, message = validate_input()
print(f"Validation: {{message}}")

# Note: At scale {scale_value} font size is automatically set to {calculated_font_size}
# Formula: font_size = scale * 4
# Text field has bottom margin of 2 proportional pixels for better appearance
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

# Create toggle switch
toggle = MinecraftToggleButton(toggle_config)

# Apply pattern
toggle.set_pattern("{pattern_name}")

# Set initial state (default is off)
toggle.set_toggled(False)

# Event handlers
toggle.clicked.connect(lambda: print("Toggle clicked!"))
toggle.stateChanged.connect(lambda toggled: print(f"Toggle {{'ON' if toggled else 'OFF'}}"))

# Programmatic control
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

# Check state
if toggle.is_toggled():
    print("Toggle is currently ON")
else:
    print("Toggle is currently OFF")

# Extended handler with logic
def on_toggle_changed(is_on):
    if is_on:
        print("Feature enabled!")
        # Add logic for enabled state here
    else:
        print("Feature disabled!")
        # Add logic for disabled state here

toggle.stateChanged.connect(on_toggle_changed)

# Change pattern programmatically
available_patterns = ["None", "Standard"]
toggle.set_pattern("Standard")  # Apply different pattern
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

# Create slider
slider = MinecraftSlider(slider_config)

# Set initial value (50%)
slider.set_value(0.5)

# Value change handler
slider.valueChanged.connect(lambda value: print(f"Slider value: {{value:.2f}}"))

# Get current value
current_value = slider.get_value()
print(f"Current value: {{current_value:.2f}}")

# Programmatic value changes
slider.set_value(0.75)  # Set to 75%
slider.set_value(0.0)   # Minimum value
slider.set_value(1.0)   # Maximum value

# Change orientation (if needed)
slider.set_orientation("{orientation}")  # "vertical" or "horizontal"

# Extended event handler with detailed information
def on_slider_changed(value):
    percentage = int(value * 100)
    print(f"Slider {orientation} (length: {track_length}px): {{value:.2f}} ({{percentage}}%)")
    
    # Additional logic depending on value
    if value < 0.25:
        print("Low range")
    elif value < 0.75:
        print("Medium range")
    else:
        print("High range")

slider.valueChanged.connect(on_slider_changed)

# Create functions for specific values
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

# Set value with validation
def set_value_safe(value):
    if 0.0 <= value <= 1.0:
        slider.set_value(value)
        return True
    else:
        print(f"Invalid value: {{value}}. Must be between 0.0 and 1.0")
        return False

# Usage example
set_value_safe(0.8)  # Valid value
set_value_safe(1.5)  # Invalid value
'''
        else:
            code = f"# Export for {self.current_widget_type} not implemented yet"

        # Show code in dialog
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