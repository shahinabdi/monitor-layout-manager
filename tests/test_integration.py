import unittest
from unittest.mock import patch, MagicMock
import tkinter as tk
import win32api
import win32con
from src.display_config import DisplayConfig
from src.display_canvas import DisplayCanvas


class TestDisplayManagerIntegration(unittest.TestCase):
    def setUp(self):
        # Create root window first
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window

        self.display_name = "\\\\.\\DISPLAY1"
        self.mock_device = self.create_mock_device(self.display_name, True)

    def tearDown(self):
        self.root.destroy()

    def create_mock_device(self, name, is_primary):
        device = MagicMock()
        device.DeviceName = name
        device.StateFlags = win32con.DISPLAY_DEVICE_ATTACHED_TO_DESKTOP
        if is_primary:
            device.StateFlags |= win32con.DISPLAY_DEVICE_PRIMARY_DEVICE
        return device

    @patch("win32api.EnumDisplayDevices")
    @patch("ctypes.windll.user32.EnumDisplaySettingsW")
    def test_display_enumeration(self, mock_enum_settings, mock_enum_devices):
        """Test display enumeration process"""
        # Setup device enumeration
        mock_enum_devices.side_effect = [self.mock_device, win32api.error]
        mock_enum_settings.return_value = 1

        # Create display config
        config = DisplayConfig()

        # Verify enumeration
        self.assertIn(self.display_name, config.displays)

    @patch("win32api.EnumDisplayDevices")
    @patch("ctypes.windll.user32.EnumDisplaySettingsW")
    @patch("ctypes.windll.user32.ChangeDisplaySettingsExW")
    def test_display_changes(
        self, mock_change_settings, mock_enum_settings, mock_enum_devices
    ):
        """Test display changes process"""
        # Setup initial enumeration
        mock_enum_devices.side_effect = [
            self.mock_device,
            win32api.error,
            self.mock_device,  # For re-enumeration after changes
            win32api.error,
        ]

        # Mock settings enumeration for both initial and after changes
        def enum_settings_side_effect(*args, **kwargs):
            return 1

        mock_enum_settings.side_effect = enum_settings_side_effect

        # Mock successful settings change
        mock_change_settings.return_value = 0

        # Create config
        config = DisplayConfig()

        # Make changes
        config.set_position(self.display_name, 100, 200)

        # Apply changes
        result = config.apply_changes()
        self.assertTrue(result)
        self.assertEqual(config.pending_changes, {})

    @patch("win32api.EnumDisplayDevices")
    @patch("ctypes.windll.user32.EnumDisplaySettingsW")
    def test_canvas_display(self, mock_enum_settings, mock_enum_devices):
        """Test canvas display functionality"""
        # Setup mocks
        mock_enum_devices.side_effect = [self.mock_device, win32api.error]
        mock_enum_settings.return_value = 1

        # Create canvas
        on_moved = MagicMock()
        canvas = DisplayCanvas(self.root, on_moved)

        # Update displays
        displays = {
            self.display_name: {
                "x": 0,
                "y": 0,
                "width": 1920,
                "height": 1080,
                "orientation": 0,
            }
        }
        canvas.update_displays(displays)

        # Test display selection
        canvas.select_display(self.display_name)
        self.assertEqual(canvas.selected, self.display_name)

    def test_coordinate_conversion(self):
        """Test coordinate conversion in canvas"""
        canvas = DisplayCanvas(self.root, MagicMock())

        # Test conversion
        screen_x, screen_y = 1920, 1080
        canvas_x, canvas_y = canvas.screen_to_canvas(screen_x, screen_y)
        back_x, back_y = canvas.canvas_to_screen(canvas_x, canvas_y)

        # Verify roundtrip conversion
        self.assertAlmostEqual(screen_x, back_x, delta=1)
        self.assertAlmostEqual(screen_y, back_y, delta=1)


if __name__ == "__main__":
    unittest.main()
