"""
Minecraft-style text entry field
"""
from PyQt6.QtWidgets import QFrame, QLineEdit
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

class MinecraftEntry(QFrame):
    """
    Minecraft-style text entry field
    Size: configurable width x 10 proportional pixels, text takes full height
    """
    textChanged = pyqtSignal(str)
    returnPressed = pyqtSignal()

    def __init__(self, placeholder="", style_config=None, parent=None):
        super().__init__(parent)

        # Default configuration for Entry
        self.default_config = {
            'entry_width': 60,          # Width in proportional pixels
            'entry_height': 10,         # Height in proportional pixels
            'scale': 8,
            'border_color': '#F2F2F2',      # Light border
            'top_space_color': '#696D88',   # Top space color
            'background_color': '#9A9FB4',  # Main background
            'text_color': 'white',
            'font_family': 'Minecraft Standard',
            'placeholder': placeholder
        }

        # Apply user configuration
        self.config = self.default_config.copy()
        if style_config:
            self.config.update(style_config)

        self.focused = False
        self.setup_entry()

    def setup_entry(self):
        """Setup text entry field"""
        try:
            self.scale = self.config['scale']

            # Calculate dimensions with borders
            entry_width = self.config['entry_width']
            entry_height = self.config['entry_height']

            # Total dimensions: borders (1+1) + main area
            self.base_width = (entry_width + 2) * self.scale
            self.base_height = (entry_height + 2) * self.scale

            self.setFixedSize(self.base_width, self.base_height)

            # Create elements
            self.create_entry_border()
            self.create_entry_background()
            self.create_text_input()
        except Exception as e:
            print(f"Setup error: {e}")

    def create_entry_border(self):
        """Create Entry border"""
        border_color = self.config['border_color']  # #F2F2F2

        # Top border
        self.top_border = QFrame(self)
        self.top_border.setGeometry(0, 0, self.base_width, self.scale)
        self.top_border.setStyleSheet(f"background-color: {border_color}; border-radius: 0px;")

        # Left border
        self.left_border = QFrame(self)
        self.left_border.setGeometry(0, self.scale, self.scale, self.config['entry_height'] * self.scale)
        self.left_border.setStyleSheet(f"background-color: {border_color}; border-radius: 0px;")

        # Right border
        self.right_border = QFrame(self)
        self.right_border.setGeometry((self.config['entry_width'] + 1) * self.scale, self.scale,
                                     self.scale, self.config['entry_height'] * self.scale)
        self.right_border.setStyleSheet(f"background-color: {border_color}; border-radius: 0px;")

        # Bottom border
        self.bottom_border = QFrame(self)
        self.bottom_border.setGeometry(0, (self.config['entry_height'] + 1) * self.scale,
                                     self.base_width, self.scale)
        self.bottom_border.setStyleSheet(f"background-color: {border_color}; border-radius: 0px;")

    def create_entry_background(self):
        """Create Entry background"""
        entry_width = self.config['entry_width']
        entry_height = self.config['entry_height']

        # Top space (2 proportional pixels after border)
        self.top_space = QFrame(self)
        self.top_space.setGeometry(self.scale, self.scale,
                                 entry_width * self.scale, 2 * self.scale)
        self.top_space.setStyleSheet(f"background-color: {self.config['top_space_color']}; border-radius: 0px;")

        # Main area (remainder after top space)
        main_height = entry_height - 2  # Subtract 2 pixels of top space
        self.main_background = QFrame(self)
        self.main_background.setGeometry(self.scale, (1 + 2) * self.scale,
                                       entry_width * self.scale, main_height * self.scale)
        self.main_background.setStyleSheet(f"background-color: {self.config['background_color']}; border-radius: 0px;")

    def create_text_input(self):
        """Create text input field"""
        entry_width = self.config['entry_width']
        entry_height = self.config['entry_height']

        # Position text field 2 proportional pixels above border (in main area)
        text_y = (1 + 2) * self.scale - 2 * self.scale  # After border + after top space - 2 pixels up

        # Height of main area WITHOUT bottom margin + compensation for upward movement
        text_height = (entry_height - 2) * self.scale + 2 * self.scale  # +2 pixels to compensate movement

        self.text_input = QLineEdit(self)

        # Keep full width but add internal padding through CSS
        self.text_input.setGeometry(
            self.scale,  # Only border offset
            text_y,
            entry_width * self.scale,  # Full width
            text_height
        )

        # Calculate font size based on scale
        # Formula: font_size = scale * 4 (for larger, readable text)
        calculated_font_size = self.scale * 4

        # If font_size is explicitly specified in config, use it
        if 'font_size' in self.config:
            font_size = self.config['font_size']
        else:
            font_size = calculated_font_size

        # Setup font with scaled size
        font = QFont(self.config['font_family'], font_size)
        self.text_input.setFont(font)

        # Styles for text field
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

        # Connect signals
        self.text_input.textChanged.connect(self.textChanged.emit)
        self.text_input.returnPressed.connect(self.returnPressed.emit)

        # Safe focus handlers through signals
        self.text_input.focusInEvent = lambda event: self.handle_focus_in(event)
        self.text_input.focusOutEvent = lambda event: self.handle_focus_out(event)

    def handle_focus_in(self, event):
        """Safe focus in handler"""
        try:
            self.focused = True
            self.update_entry_styles()
            # Call original handler
            QLineEdit.focusInEvent(self.text_input, event)
        except Exception as e:
            print(f"Focus in error: {e}")

    def handle_focus_out(self, event):
        """Safe focus out handler"""
        try:
            self.focused = False
            self.update_entry_styles()
            # Call original handler
            QLineEdit.focusOutEvent(self.text_input, event)
        except Exception as e:
            print(f"Focus out error: {e}")

    def update_entry_styles(self):
        """Update styles on focus change"""
        try:
            if self.focused:
                # On focus, can change border or background color
                # Currently keeping as is, but effects can be added
                pass
            else:
                # Without focus - standard colors
                pass
        except Exception as e:
            print(f"Style update error: {e}")

    def get_text(self):
        """Get text"""
        return self.text_input.text()

    def set_text(self, text):
        """Set text"""
        self.text_input.setText(text)

    def clear(self):
        """Clear text"""
        self.text_input.clear()

    def set_placeholder(self, placeholder):
        """Set placeholder text"""
        self.text_input.setPlaceholderText(placeholder)

    def set_readonly(self, readonly):
        """Set read-only mode"""
        self.text_input.setReadOnly(readonly)