import unittest
from unittest.mock import patch, MagicMock
import win32api
import win32con
import ctypes
from src.display_config import DisplayConfig, DEVMODE


class TestDisplayConfig(unittest.TestCase):
    def setUp(self):
        self.display_config = DisplayConfig()
        self.display_name = "\\\\.\\DISPLAY1"  # Correct Windows display name format

    def create_mock_devmode(self):
        """Helper to create a mock DEVMODE structure"""
        devmode = DEVMODE()
        devmode.dmSize = ctypes.sizeof(DEVMODE)
        devmode.dmPositionX = 0
        devmode.dmPositionY = 0
        devmode.dmPelsWidth = 1920
        devmode.dmPelsHeight = 1080
        devmode.dmDisplayOrientation = 0
        devmode.dmDisplayFrequency = 60
        devmode.dmDisplayFlags = 0
        return devmode

    @patch("win32api.EnumDisplayDevices")
    @patch("ctypes.windll.user32.EnumDisplaySettingsW")
    def test_enumerate_displays(self, mock_enum_settings, mock_enum_devices):
        # Create mock device
        mock_device = MagicMock()
        mock_device.DeviceName = self.display_name
        mock_device.StateFlags = win32con.DISPLAY_DEVICE_ATTACHED_TO_DESKTOP

        # Setup mock returns
        mock_enum_devices.side_effect = [mock_device, win32api.error]
        mock_enum_settings.return_value = 1

        # Test enumeration
        self.display_config.enumerate_displays()

        # Verify displays were enumerated
        self.assertIn(self.display_name, self.display_config.displays)

    def test_get_display_info_nonexistent(self):
        """Test getting info for non-existent display"""
        info = self.display_config.get_display_info("NONEXISTENT")
        self.assertIsNone(info)

    def test_get_display_info_with_pending_changes(self):
        """Test getting display info with pending changes"""
        # Setup
        self.display_config.displays[self.display_name] = self.create_mock_devmode()
        self.display_config.pending_changes[self.display_name] = {
            "x": 100,
            "y": 200,
            "orientation": 1,
        }

        # Test
        info = self.display_config.get_display_info(self.display_name)

        # Verify
        self.assertEqual(info["x"], 100)
        self.assertEqual(info["y"], 200)
        self.assertEqual(info["orientation"], 1)

    @patch("ctypes.windll.user32.ChangeDisplaySettingsExW")
    def test_apply_changes(self, mock_change_settings):
        """Test applying changes"""
        # Setup
        self.display_config.displays[self.display_name] = self.create_mock_devmode()
        self.display_config.pending_changes[self.display_name] = {
            "x": 100,
            "y": 200,
            "orientation": 1,
        }

        # Mock successful settings change
        mock_change_settings.return_value = 0

        # Apply changes
        result = self.display_config.apply_changes()

        # Verify
        self.assertTrue(result)
        self.assertEqual(self.display_config.pending_changes, {})
