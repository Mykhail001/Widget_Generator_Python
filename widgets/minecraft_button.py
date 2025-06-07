"""
Minecraft-style button with pattern support
"""
from PyQt6.QtWidgets import QFrame, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from managers import ButtonPatternManager

class MinecraftButton(QFrame):
    """
    Base class for Minecraft-style buttons with customization support
    Features:
    - Main area size configuration
    - Press animations
    - Color schemes
    - Proportional scaling
    - Button patterns
    """
    clicked = pyqtSignal()
    def __init__(self, text="", style_config=None, parent=None):
        super().__init__(parent)

        # Default style configuration
        self.default_config = {
            'button_width': 16,  # Main area width in proportional pixels
            'button_height': 15, # Main area height in proportional pixels
            'scale': 8,
            'border_color': '#413F54',
            'button_normal': '#9A9FB4',
            'button_hover': '#9CD3FF',
            'button_pressed': '#9CD3FF',
            'border_normal': '#ADB0C4',
            'border_hover': '#DAFFFF',
            'border_pressed': '#DAFFFF',
            'bottom_normal': '#9A9FB4',
            'bottom_hover': '#708CBA',
            'bottom_pressed': '#708CBA',
            'text_color': 'white',
            'font_family': 'Minecraftia',
            'has_shadow': True,
            'animation_enabled': True
        }
        # Apply user configuration
        self.config = self.default_config.copy()
        if style_config:
            self.config.update(style_config)

        # Pattern variables
        self.pattern_name = 'None'  # Current pattern name
        self.pattern_pixels = []    # List of QFrame elements for pattern

        self.setup_button()

    def setup_button(self):
        """Setup button based on configuration"""
        self.scale = self.config['scale']

        # Calculate dimensions based on main area
        button_width = self.config['button_width']  # proportional pixels
        button_height = self.config['button_height']  # proportional pixels

        # Total dimensions: borders (1+1) + main area + bottom space (2)
        self.base_width = (button_width + 2) * self.scale  # +2 for left and right borders
        self.base_height = (1 + button_height + 2 + 1) * self.scale  # top + button + space + bottom
        self.setFixedSize(self.base_width, self.base_height)
        self.pressed_state = False
        self.hover_state = False

        # Create all button elements
        self.create_borders()
        self.create_main_button()
        self.create_pattern()  # Create pattern after main button
        self.create_bottom_space()
        self.update_styles()

    def create_borders(self):
        """Create button borders"""
        border_color = self.config['border_color']
        button_width = self.config['button_width']
        button_height = self.config['button_height']

        # Top border
        self.top_border = QFrame(self)
        self.top_border.setGeometry(0, 0, self.base_width, self.scale)
        self.top_border.setStyleSheet(f"background-color: {border_color}; border-radius: 0px;")

        # Left border
        self.left_border = QFrame(self)
        self.left_border.setGeometry(0, self.scale, self.scale, (button_height + 2) * self.scale)
        self.left_border.setStyleSheet(f"background-color: {border_color}; border-radius: 0px;")
        # Right border
        self.right_border = QFrame(self)
        self.right_border.setGeometry((button_width + 1) * self.scale, self.scale, self.scale, (button_height + 2) * self.scale)
        self.right_border.setStyleSheet(f"background-color: {border_color}; border-radius: 0px;")
        # Bottom border
        self.bottom_border = QFrame(self)
        self.bottom_border.setGeometry(0, self.base_height - self.scale, self.base_width, self.scale)
        self.bottom_border.setStyleSheet(f"background-color: {border_color}; border-radius: 0px;")

    def create_main_button(self):
        """Create main button"""
        button_width = self.config['button_width']
        button_height = self.config['button_height']

        self.button = QPushButton('', self)  # Always without text
        self.button.setGeometry(self.scale, self.scale, button_width * self.scale, button_height * self.scale)

        # Font setup
        font = QFont(self.config['font_family'], 16)  # Fixed size
        self.button.setFont(font)

        # Disable mouse events on button
        self.button.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def create_pattern(self):
        """Create pattern on button"""
        self.clear_pattern()  # Clear previous pattern

        patterns = ButtonPatternManager.get_patterns()
        colors = ButtonPatternManager.get_pattern_colors()

        if self.pattern_name not in patterns or patterns[self.pattern_name] is None:
            return  # No pattern

        pattern_data = patterns[self.pattern_name]
        button_width = self.config['button_width']
        button_height = self.config['button_height']

        # Create pattern pixels inside button (start after border)
        max_rows = min(button_height, len(pattern_data))  # Limit by button height
        for row_idx in range(max_rows):
            row = pattern_data[row_idx]
            max_cols = min(button_width, len(row))  # Limit by button width
            for col_idx in range(max_cols):
                symbol = row[col_idx]
                if symbol != '0':  # Not transparent pixel
                    color = colors.get(symbol)
                    if color:
                        # Pixel position (start after left and top borders)
                        pixel_x = (1 + col_idx) * self.scale  # +1 for left border
                        pixel_y = (1 + row_idx) * self.scale  # +1 for top border

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

    def update_pattern_position(self, offset_y=0):
        """Update pattern position (for press animation)"""
        if not self.pattern_pixels:
            return

        # Recalculate positions of all pattern pixels
        patterns = ButtonPatternManager.get_patterns()
        if self.pattern_name not in patterns or patterns[self.pattern_name] is None:
            return

        pattern_data = patterns[self.pattern_name]
        button_width = self.config['button_width']
        button_height = self.config['button_height']

        pixel_index = 0
        max_rows = min(button_height, len(pattern_data))
        for row_idx in range(max_rows):
            row = pattern_data[row_idx]
            max_cols = min(button_width, len(row))
            for col_idx in range(max_cols):
                symbol = row[col_idx]
                if symbol != '0' and pixel_index < len(self.pattern_pixels):
                    # New position with offset
                    pixel_x = (1 + col_idx) * self.scale
                    pixel_y = (1 + row_idx + offset_y) * self.scale

                    self.pattern_pixels[pixel_index].setGeometry(pixel_x, pixel_y, self.scale, self.scale)
                    pixel_index += 1

    def create_bottom_space(self):
        """Create bottom space (shadow)"""
        button_width = self.config['button_width']
        button_height = self.config['button_height']

        self.bottom_space = QFrame(self)
        self.bottom_space.setGeometry(self.scale, (1 + button_height) * self.scale, button_width * self.scale, 2 * self.scale)

    def mousePressEvent(self, event):
        """Handle mouse press"""
        if event.button() == Qt.MouseButton.LeftButton and self.config['animation_enabled']:
            self.on_pressed()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        if event.button() == Qt.MouseButton.LeftButton:
            if self.config['animation_enabled']:
                self.on_released()
            if self.rect().contains(event.pos()):
                self.clicked.emit()
        super().mouseReleaseEvent(event)

    def enterEvent(self, event):
        """Handle mouse enter"""
        self.hover_state = True
        self.update_styles()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave"""
        self.hover_state = False
        self.update_styles()
        super().leaveEvent(event)

    def on_pressed(self):
        """Press animation"""
        self.pressed_state = True
        button_width = self.config['button_width']
        button_height = self.config['button_height']
        # Button moves down by 1 proportional pixel
        self.button.setGeometry(self.scale, 2 * self.scale, button_width * self.scale, button_height * self.scale)
        # Bottom space decreases by 1 proportional pixel
        self.bottom_space.setGeometry(self.scale, (2 + button_height) * self.scale, button_width * self.scale, self.scale)
        # Pattern also moves down
        self.update_pattern_position(offset_y=1)
        # Make top border match background color
        self.top_border.setStyleSheet("background-color: #CBCCD4; border-radius: 0px;")
        self.update_styles()

    def on_released(self):
        """Restore after press"""
        self.pressed_state = False
        button_width = self.config['button_width']
        button_height = self.config['button_height']

        # Return button and space to normal state
        self.button.setGeometry(self.scale, self.scale, button_width * self.scale, button_height * self.scale)
        self.bottom_space.setGeometry(self.scale, (1 + button_height) * self.scale, button_width * self.scale, 2 * self.scale)
        # Return pattern to normal position
        self.update_pattern_position(offset_y=0)

        # Restore top border color
        self.top_border.setStyleSheet(f"background-color: {self.config['border_color']}; border-radius: 0px;")
        self.update_styles()

    def update_styles(self):
        """Update styles based on state"""
        if self.pressed_state:
            button_bg = self.config['button_pressed']
            border_color = self.config['border_pressed']
            bottom_color = self.config['bottom_pressed']
        elif self.hover_state:
            button_bg = self.config['button_hover']
            border_color = self.config['border_hover']
            bottom_color = self.config['bottom_hover']
        else:
            button_bg = self.config['button_normal']
            border_color = self.config['border_normal']
            bottom_color = self.config['bottom_normal']

        # Button styles
        button_style = f"""
        QPushButton {{
            border: {self.scale}px solid {border_color};
            background-color: {button_bg};
            color: {self.config['text_color']};
            padding: 0px;
            margin: 0px;
            border-radius: 0px;
        }}
        """

        bottom_style = f"""QFrame {{ 
            background-color: {bottom_color}; 
            border: none; 
            border-radius: 0px;
        }}"""

        self.button.setStyleSheet(button_style)
        self.bottom_space.setStyleSheet(bottom_style)
        self.setStyleSheet(f"background-color: {self.config['border_color']}; border-radius: 0px;")