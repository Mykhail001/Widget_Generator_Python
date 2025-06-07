"""
Minecraft-style radio buttons
"""
from PyQt6.QtWidgets import QFrame, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

class MinecraftRadioButton(QFrame):
    """
    Minecraft-style radio button
    """
    clicked = pyqtSignal()
    stateChanged = pyqtSignal(bool)  # True when selected

    def __init__(self, text="", style_config=None, parent=None):
        super().__init__(parent)
        # Default configuration for radio button
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
            'indicator_line_color': '#708CBA',  # Line color (51 74 97)
            'bottom_space_normal': '#696D88',   # Bottom space color (inactive)
            'bottom_space_hover': '#708CBA',    # Bottom space color (hover)
            'bottom_space_selected': '#708CBA', # Bottom space color (selected)
            'text_color': 'white',
            'font_family': 'Minecraftia'
        }

        # Apply user configuration
        self.config = self.default_config.copy()
        if style_config:
            self.config.update(style_config)
        self.selected = False
        self.hover_state = False
        self.setup_radio_button()

    def setup_radio_button(self):
        """Setup radio button"""
        self.scale = self.config['scale']

        # Dimensions: reduced main area (10x9) + borders + bottom space
        main_width = 10  # was 12, minus 1 left and 1 right
        main_height = 9  # was 12, minus 1 top and 2 bottom
        self.radio_width = (main_width + 2) * self.scale  # +2 for borders
        self.radio_height = (main_height + 2 + 2) * self.scale  # +2 for borders +2 for bottom space

        # If there's text, add space for it
        text_width = 0
        if self.config['text']:
            text_width = len(self.config['text']) * 10 + 10  # Fixed calculation

        total_width = self.radio_width + text_width
        self.setFixedSize(total_width, self.radio_height)

        # Create elements
        self.create_radio_borders()
        self.create_radio_main()
        self.create_radio_indicator()
        self.create_radio_bottom_space()
        self.create_radio_text()
        self.update_radio_styles()

    def create_radio_borders(self):
        """Create radio button borders"""
        border_color = self.config['border_color']

        # Top border
        self.top_border = QFrame(self)
        self.top_border.setGeometry(0, 0, self.radio_width, self.scale)
        self.top_border.setStyleSheet(f"background-color: {border_color}; border-radius: 0px;")

        # Left border (height for main area 9 + bottom space 2)
        self.left_border = QFrame(self)
        self.left_border.setGeometry(0, self.scale, self.scale, 11 * self.scale)
        self.left_border.setStyleSheet(f"background-color: {border_color}; border-radius: 0px;")

        # Right border (position for width 10+1)
        self.right_border = QFrame(self)
        self.right_border.setGeometry(11 * self.scale, self.scale, self.scale, 11 * self.scale)
        self.right_border.setStyleSheet(f"background-color: {border_color}; border-radius: 0px;")

        # Bottom border (position for height 9+2+1)
        self.bottom_border = QFrame(self)
        self.bottom_border.setGeometry(0, 12 * self.scale, self.radio_width, self.scale)
        self.bottom_border.setStyleSheet(f"background-color: {border_color}; border-radius: 0px;")

    def create_radio_main(self):
        """Create main radio button area"""
        self.main_area = QFrame(self)
        # New main area: 10x9 pixels
        self.main_area.setGeometry(self.scale, self.scale, 10 * self.scale, 9 * self.scale)

    def create_radio_indicator(self):
        """Create center indicator for selected state"""
        # Center square 4x4 with new margins
        # Left: 3 pixels (was 4, minus 1)
        # Top: 3 pixels (was 4, minus 1)
        indicator_size = 4 * self.scale
        indicator_x = self.scale + 3 * self.scale  # 3 pixel offset from left edge of main area
        indicator_y = self.scale + 3 * self.scale  # 3 pixel offset from top edge

        self.indicator = QFrame(self)
        self.indicator.setGeometry(indicator_x, indicator_y, indicator_size, indicator_size)
        self.indicator.hide()  # Initially hidden

        # Horizontal line inside indicator (4x1 pixel) - in first row
        line_y = indicator_y  # In first row of square
        self.indicator_line = QFrame(self)
        self.indicator_line.setGeometry(indicator_x, line_y, indicator_size, self.scale)
        self.indicator_line.hide()  # Initially hidden

    def create_radio_bottom_space(self):
        """Create radio button bottom space"""
        # Bottom space takes full width of new main area (10 pixels)
        space_width = 10 * self.scale  # Full width inside borders
        space_x = self.scale  # Starts right after left border
        space_y = 10 * self.scale  # Under main area (1 + 9)

        self.radio_bottom_space = QFrame(self)
        self.radio_bottom_space.setGeometry(space_x, space_y, space_width, 2 * self.scale)

    def create_radio_text(self):
        """Create radio button text"""
        if self.config['text']:
            self.text_label = QLabel(self.config['text'], self)
            font = QFont(self.config['font_family'], 16)  # Fixed size
            self.text_label.setFont(font)
            self.text_label.setStyleSheet(f"color: {self.config['text_color']}; background: transparent;")

            # Position text to the right of radio button
            text_x = self.radio_width + 5
            text_y = (self.radio_height - 16) // 2  # Fixed font size
            self.text_label.move(text_x, text_y)

    def mousePressEvent(self, event):
        """Handle press"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if click was on radio button (not on text)
            if event.pos().x() <= self.radio_width:
                self.toggle_selection()
        super().mousePressEvent(event)

    def enterEvent(self, event):
        """Handle mouse enter"""
        self.hover_state = True
        self.update_radio_styles()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave"""
        self.hover_state = False
        self.update_radio_styles()
        super().leaveEvent(event)

    def toggle_selection(self):
        """Toggle selection state"""
        self.selected = not self.selected
        self.update_radio_styles()
        self.clicked.emit()
        self.stateChanged.emit(self.selected)

    def set_selected(self, selected):
        """Set selection state programmatically"""
        if self.selected != selected:
            self.selected = selected
            self.update_radio_styles()
            self.stateChanged.emit(self.selected)

    def is_selected(self):
        """Return selection state"""
        return self.selected

    def update_radio_styles(self):
        """Update radio button styles"""
        if self.selected:
            # Selected state (like pressed button)
            button_bg = self.config['button_selected']
            border_color = self.config['border_selected']
            bottom_space_color = self.config['bottom_space_selected']

            # Move main area down by 1 pixel
            self.main_area.setGeometry(self.scale, 2 * self.scale, 10 * self.scale, 9 * self.scale)

            # Bottom space reduces to 1 pixel (like pressed button)
            self.radio_bottom_space.setGeometry(self.scale, 11 * self.scale, 10 * self.scale, 1 * self.scale)

            # Show indicator
            self.indicator.show()
            self.indicator_line.show()

            # Change top border
            self.top_border.setStyleSheet("background-color: #CBCCD4; border-radius: 0px;")

        elif self.hover_state:
            # Hover state
            button_bg = self.config['button_hover']
            border_color = self.config['border_hover']
            bottom_space_color = self.config['bottom_space_hover']

            # Normal position
            self.main_area.setGeometry(self.scale, self.scale, 10 * self.scale, 9 * self.scale)

            # Normal bottom space size (2 pixels)
            self.radio_bottom_space.setGeometry(self.scale, 10 * self.scale, 10 * self.scale, 2 * self.scale)

            # Hide indicator
            self.indicator.hide()
            self.indicator_line.hide()

            # Restore top border
            self.top_border.setStyleSheet(f"background-color: {self.config['border_color']}; border-radius: 0px;")

        else:
            # Normal state
            button_bg = self.config['button_normal']
            border_color = self.config['border_normal']
            bottom_space_color = self.config['bottom_space_normal']

            # Normal position
            self.main_area.setGeometry(self.scale, self.scale, 10 * self.scale, 9 * self.scale)

            # Normal bottom space size (2 pixels)
            self.radio_bottom_space.setGeometry(self.scale, 10 * self.scale, 10 * self.scale, 2 * self.scale)

            # Hide indicator
            self.indicator.hide()
            self.indicator_line.hide()

            # Restore top border
            self.top_border.setStyleSheet(f"background-color: {self.config['border_color']}; border-radius: 0px;")

        # Apply styles
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
    Radio button group (only one can be selected at a time)
    """
    def __init__(self):
        self.radio_buttons = []
        self.selected_button = None

    def add_radio_button(self, radio_button):
        """Add radio button to group"""
        if radio_button not in self.radio_buttons:
            self.radio_buttons.append(radio_button)
            radio_button.clicked.connect(lambda: self.on_radio_clicked(radio_button))

    def on_radio_clicked(self, clicked_button):
        """Handle radio button click"""
        # Deselect all buttons
        for button in self.radio_buttons:
            if button != clicked_button:
                button.set_selected(False)

        # Select clicked button
        self.selected_button = clicked_button
        clicked_button.set_selected(True)

    def get_selected(self):
        """Return selected radio button"""
        return self.selected_button

    def clear_selection(self):
        """Clear selection"""
        for button in self.radio_buttons:
            button.set_selected(False)
        self.selected_button = None