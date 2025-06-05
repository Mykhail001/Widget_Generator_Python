"""
Менеджер кольорових пресетів
"""

class ButtonPresetManager:
    """
    Менеджер пресетів кнопок

    Містить кольорові схеми:
    - MC_AE2_LIGHT: світла тема Applied Energistics 2
    - MC_AE2_DARK: темна тема Applied Energistics 2
    """

    @staticmethod
    def get_presets():
        """Повертає словник з усіма доступними пресетами"""
        return {
            'MC_AE2_LIGHT': {
                'button_normal': '#9A9FB4',
                'button_hover': '#9CD3FF',
                'button_selected': '#9CD3FF',
                'border_normal': '#ADB0C4',
                'border_hover': '#DAFFFF',
                'border_selected': '#DAFFFF',
                'bottom_normal': '#9A9FB4',
                'bottom_hover': '#708CBA',
                'indicator_color': '#DAFFFF',
                'indicator_line_color': '#708CBA',
                'bottom_space_normal': '#696D88',
                'bottom_space_hover': '#708CBA',
                'bottom_space_selected': '#708CBA'
            },
            'MC_AE2_DARK': {
                'button_normal': '#696D88',
                'button_hover': '#9CD3FF',
                'button_pressed': '#9CD3FF',
                'button_selected': '#9CD3FF',
                'border_normal': '#878FA5',
                'border_hover': '#DAFFFF',
                'border_pressed': '#DAFFFF',
                'border_selected': '#DAFFFF',
                'bottom_normal': '#4D4D67',
                'bottom_hover': '#708CBA',
                'bottom_pressed': '#708CBA',
                'indicator_color': '#DAFFFF',
                'indicator_line_color': '#708CBA',
                'bottom_space_normal': '#696D88',
                'bottom_space_hover': '#708CBA',
                'bottom_space_selected': '#708CBA'
            }
        }