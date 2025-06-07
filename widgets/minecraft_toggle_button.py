"""
Minecraft-style toggle switch
"""
from PyQt6.QtWidgets import QFrame
from PyQt6.QtCore import Qt, pyqtSignal

from managers import TogglePatternManager
from .minecraft_button import MinecraftButton

class MinecraftToggleButton(QFrame):
    """
    Minecraft-style toggle switch
    """
    clicked = pyqtSignal()
    stateChanged = pyqtSignal(bool)  # True when enabled

    def __init__(self, style_config=None, parent=None):
        super().__init__(parent)

        # Default configuration for toggle switch (without text)
        self.default_config = {
            'scale': 8,
            'border_color': '#413F54',  # (65, 63, 84)
            'left_area_color': '#9CD3FF',  # Left area
            'right_area_color': '#696D88',  # Right area
            'button_normal': '#9A9FB4',
            'button_pressed': '#9CD3FF',
            'border_normal': '#ADB0C4',
            'border_pressed': '#DAFFFF',
            'bottom_normal': '#9A9FB4',
            'bottom_pressed': '#708CBA'
        }

        # Apply user configuration
        self.config = self.default_config.copy()
        if style_config:
            self.config.update(style_config)

        self.toggled = False  # Toggle state
        self.hover_state = False  # Mouse hover state
        self.hover_active = True  # Whether hover effect is active (resets after click)
        self.pattern_name = 'Standard'  # Standard pattern by default
        self.pattern_pixels = []  # List of QFrame elements for pattern
        self.setup_toggle()

    def setup_toggle(self):
        """Setup toggle switch"""
        self.scale = self.config['scale']

        # Dimensions: 20x9 + borders (1+1)x(1+1) = 22x13
        # Add extra space on top for moving button
        self.toggle_width = 22 * self.scale
        self.toggle_height = 13 * self.scale

        self.setFixedSize(self.toggle_width, self.toggle_height)

        # Create elements
        self.create_toggle_borders()
        self.create_toggle_areas()
        self.create_pattern()  # Create pattern before moving button
        self.create_moving_button()
        self.update_toggle_styles()

    def create_toggle_borders(self):
        """Create toggle switch borders"""
        border_color = self.config['border_color']

        # Moved down by 2 pixels for space under moving button
        # Top border
        self.top_border = QFrame(self)
        self.top_border.setGeometry(0, 2 * self.scale, self.toggle_width, self.scale)
        self.top_border.setStyleSheet(f"background-color: {border_color}; border-radius: 0px;")

        # Left border (height 9 pixels)
        self.left_border = QFrame(self)
        self.left_border.setGeometry(0, 3 * self.scale, self.scale, 9 * self.scale)
        self.left_border.setStyleSheet(f"background-color: {border_color}; border-radius: 0px;")

        # Right border (position 21)
        self.right_border = QFrame(self)
        self.right_border.setGeometry(21 * self.scale, 3 * self.scale, self.scale, 9 * self.scale)
        self.right_border.setStyleSheet(f"background-color: {border_color}; border-radius: 0px;")

        # Bottom border (position 12)
        self.bottom_border = QFrame(self)
        self.bottom_border.setGeometry(0, 12 * self.scale, self.toggle_width, self.scale)
        self.bottom_border.setStyleSheet(f"background-color: {border_color}; border-radius: 0px;")

    def create_toggle_areas(self):
        """Create left and right areas"""
        # Moved down by 2 pixels for space under moving button
        # Left area (11x9)
        self.left_area = QFrame(self)
        self.left_area.setGeometry(self.scale, 3 * self.scale, 11 * self.scale, 9 * self.scale)
        self.left_area.setStyleSheet(f"background-color: {self.config['left_area_color']}; border-radius: 0px;")

        # Right area (9x9)
        self.right_area = QFrame(self)
        self.right_area.setGeometry(12 * self.scale, 3 * self.scale, 9 * self.scale, 9 * self.scale)
        self.right_area.setStyleSheet(f"background-color: {self.config['right_area_color']}; border-radius: 0px;")

    def create_pattern(self):
        """Create pattern on background"""
        self.clear_pattern()  # Clear previous pattern

        patterns = TogglePatternManager.get_patterns()
        colors = TogglePatternManager.get_pattern_colors()

        if self.pattern_name not in patterns or patterns[self.pattern_name] is None:
            return  # No pattern

        pattern_data = patterns[self.pattern_name]

        # Create pattern pixels (18x7 inside areas)
        max_rows = min(7, len(pattern_data))  # Maximum 7 rows
        for row_idx in range(max_rows):
            row = pattern_data[row_idx]
            max_cols = min(18, len(row))  # Maximum 18 columns
            for col_idx in range(max_cols):
                symbol = row[col_idx]
                if symbol != '0':  # Not transparent pixel
                    color = colors.get(symbol)
                    if color:
                        # Pixel position (moved down by 3 for borders)
                        pixel_x = (1 + col_idx) * self.scale  # +1 for left border
                        pixel_y = (3 + row_idx) * self.scale  # +3 for top border

                        pixel = QFrame(self)
                        pixel.setGeometry(pixel_x, pixel_y, self.scale, self.scale)
                        pixel.setStyleSheet(f"background-color: {color}; border: none;")
                        pixel.show()

                        self.pattern_pixels.append(pixel)

    def clear_pattern(self):
        """Clear previous pattern"""
        for pixel in self.pattern_pixels:
            pixel.deleteLater()
        self.pattern_pixels.clear()

    def set_pattern(self, pattern_name):
        """Set new pattern"""
        self.pattern_name = pattern_name
        self.create_pattern()
        # Ensure moving button stays on top
        if hasattr(self, 'moving_button'):
            self.moving_button.raise_()

    def create_moving_button(self):
        """Create moving button as real MinecraftButton"""
        # Configuration for moving button (10x8)
        button_config = {
            'button_width': 10,  # Main area width
            'button_height': 8,  # Main area height
            'scale': self.scale,
            'border_color': '#413F54',  # Dark border
            'button_normal': '#9A9FB4',  # Lighter color for visibility
            'button_hover': '#9A9FB4',   # No hover effect
            'button_pressed': '#9A9FB4', # No pressed effect
            'border_normal': '#ADB0C4',  # Light border for contrast
            'border_hover': '#ADB0C4',   # No hover effect
            'border_pressed': '#ADB0C4', # No pressed effect
            'bottom_normal': '#9A9FB4',  # Shadow
            'bottom_hover': '#9A9FB4',   # No hover effect
            'bottom_pressed': '#9A9FB4', # No pressed effect
            'text_color': 'white',
            'font_family': 'Minecraftia',
            'has_shadow': True,
            'animation_enabled': False  # Disable press animation
        }

        # Create real Minecraft button
        self.moving_button = MinecraftButton('', button_config, self)

        # Ensure button is visible
        self.moving_button.show()
        self.moving_button.raise_()  # Bring to front

        # Initial position (off - left)
        self.update_button_position()

    def mousePressEvent(self, event):
        """Handle press"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Reset hover effect after press
            self.hover_active = False
            self.toggle_state()
        super().mousePressEvent(event)

    def enterEvent(self, event):
        """Handle mouse enter"""
        self.hover_state = True
        self.update_button_position()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave"""
        self.hover_state = False
        # Restore hover effect possibility on next enter
        self.hover_active = True
        self.update_button_position()
        super().leaveEvent(event)

    def toggle_state(self):
        """Toggle state"""
        self.toggled = not self.toggled
        self.update_button_position()
        self.update_toggle_styles()
        self.clicked.emit()
        self.stateChanged.emit(self.toggled)

    def set_toggled(self, toggled):
        """Set state programmatically"""
        if self.toggled != toggled:
            self.toggled = toggled
            self.update_button_position()
            self.update_toggle_styles()
            self.stateChanged.emit(self.toggled)

    def is_toggled(self):
        """Return toggle state"""
        return self.toggled

    def update_button_position(self):
        """Update moving button position"""
        base_x = 0  # Base position

        if self.toggled:
            # Enabled - right
            base_x = 10 * self.scale
            if self.hover_state and self.hover_active:
                # On hover move left by 2 pixels (only if hover is active)
                button_x = base_x - 2 * self.scale
            else:
                button_x = base_x
        else:
            # Disabled - left
            base_x = 0 * self.scale
            if self.hover_state and self.hover_active:
                # On hover move right by 2 pixels (only if hover is active)
                button_x = base_x + 2 * self.scale
            else:
                button_x = base_x

        button_y = 1 * self.scale  # Now in reserved space on top
        self.moving_button.move(button_x, button_y)

        # Additional checks for visibility
        self.moving_button.show()
        self.moving_button.raise_()

    def update_toggle_styles(self):
        """Update toggle switch styles"""
        # Button always has same color regardless of toggle state
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
            # Ensure borders always have correct color
            'border_color': '#413F54'
        })

        # Force set hover=False, pressed=False state
        self.moving_button.hover_state = False
        self.moving_button.pressed_state = False

        # Apply updated styles to button
        self.moving_button.update_styles()
        # Top part has background color, not border color
        self.setStyleSheet(f"background-color: #CBCCD4; border-radius: 0px;")