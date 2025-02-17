import unittest
from unittest.mock import patch, MagicMock
import win32api
import win32con
from src.display_config import DisplayConfig


class TestDisplayConfig(unittest.TestCase):
    def setUp(self):
        self.display_config = DisplayConfig()

    @patch("win32api.EnumDisplayDevices")
    @patch("ctypes.windll.user32.EnumDisplaySettingsW")
    def test_enumerate_displays(self, mock_enum_settings, mock_enum_devices):
        # Mock device
        mock_device = MagicMock()
        mock_device.DeviceName = r"\.\DISPLAY1"
        mock_device.StateFlags = win32con.DISPLAY_DEVICE_ATTACHED_TO_DESKTOP

        # Setup device enumeration
        mock_enum_devices.side_effect = [
            mock_device,
            win32api.error,  # End enumeration
        ]

        # Mock settings
        mock_enum_settings.return_value = 1

        # Test enumeration
        self.display_config.enumerate_displays()

        # Verify displays were enumerated
        self.assertIn(r"\.\DISPLAY1", self.display_config.displays)

    def test_get_display_info(self):
        # Setup test display
        test_display = MagicMock()
        test_display.dmPositionX = 0
        test_display.dmPositionY = 0
        test_display.dmPelsWidth = 1920
        test_display.dmPelsHeight = 1080
        test_display.dmDisplayOrientation = 0
        test_display.dmDisplayFrequency = 60
        test_display.dmDisplayFlags = 0

        self.display_config.displays = {r"\.\DISPLAY1": test_display}

        # Test getting display info
        info = self.display_config.get_display_info(r"\.\DISPLAY1")

        # Verify display info
        self.assertIsNotNone(info)
        self.assertEqual(info["width"], 1920)
        self.assertEqual(info["height"], 1080)
        self.assertEqual(info["refresh_rate"], 60)

    def test_set_position(self):
        # Test setting position
        self.display_config.displays = {r"\.\DISPLAY1": MagicMock()}

        # Set new position
        self.display_config.set_position(r"\.\DISPLAY1", 100, 200)

        # Verify pending changes
        self.assertIn(r"\.\DISPLAY1", self.display_config.pending_changes)
        self.assertEqual(self.display_config.pending_changes[r"\.\DISPLAY1"]["x"], 100)
        self.assertEqual(self.display_config.pending_changes[r"\.\DISPLAY1"]["y"], 200)


if __name__ == "__main__":
    unittest.main()
