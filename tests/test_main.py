import unittest
from unittest.mock import patch, MagicMock
import win32api
import win32con
from src.main import DisplayManager


class MockTkVariable:
    def __init__(self, master=None, value=None, name=None):
        self._value = value if value is not None else ""
        self._trace_callbacks = []

    def get(self):
        return self._value

    def set(self, value):
        self._value = value
        for callback in self._trace_callbacks:
            callback()

    def trace_add(self, mode, callback):
        self._trace_callbacks.append(callback)

    def trace_variable(self, mode, callback):
        self._trace_callbacks.append(callback)


class MockText(MagicMock):
    def __init__(self, master=None, **kwargs):
        super().__init__()
        self.content = ""
        self.pack = MagicMock()
        self.grid = MagicMock()
        self.bind = MagicMock()

    def delete(self, start, end):
        self.content = ""

    def insert(self, index, text):
        self.content = text

    def get(self, start, end):
        return self.content


class MockCanvas(MagicMock):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.displays = {}  # Use displays instead of items to match DisplayCanvas
        self.selected = None
        self.pack = MagicMock()
        self.grid = MagicMock()
        self.bind = MagicMock()

    def select_display(self, display):
        self.selected = display

    def update_displays(self, displays):
        self.displays = displays

    def screen_to_canvas(self, x, y):
        return x, y

    def canvas_to_screen(self, x, y):
        return x, y


@patch("tkinter.StringVar", MockTkVariable)
@patch("tkinter.Text", MockText)
class TestDisplayManager(unittest.TestCase):
    def setUp(self):
        self.display_name = "\\\\.\\DISPLAY1"
        self.mock_device = MagicMock()
        self.mock_device.DeviceName = self.display_name
        self.mock_device.StateFlags = win32con.DISPLAY_DEVICE_ATTACHED_TO_DESKTOP

    @patch("tkinter.Tk")
    @patch("tkinter.ttk.PanedWindow")
    @patch("tkinter.ttk.Frame")
    @patch("tkinter.ttk.LabelFrame")
    @patch("tkinter.ttk.Label")
    @patch("tkinter.ttk.Entry")
    @patch("tkinter.ttk.Combobox")
    @patch("tkinter.ttk.Button")
    @patch("src.display_canvas.DisplayCanvas", MockCanvas)
    def create_manager_with_mocks(
        self,
        mock_button,
        mock_combo,
        mock_entry,
        mock_label,
        mock_labelframe,
        mock_frame,
        mock_paned,
        mock_tk,
    ):
        # Setup root window mock
        root = MagicMock()
        root.title = MagicMock()
        root.geometry = MagicMock()
        root.bind = MagicMock()
        mock_tk.return_value = root

        # Setup widget mocks with common methods
        mock_widgets = [
            mock_paned,
            mock_frame,
            mock_labelframe,
            mock_combo,
            mock_entry,
            mock_button,
        ]
        for widget in mock_widgets:
            mock_instance = MagicMock()
            mock_instance.pack = MagicMock()
            mock_instance.grid = MagicMock()
            mock_instance.bind = MagicMock()
            widget.return_value = mock_instance

        # Setup specific widget behaviors
        mock_combo.return_value.set = MagicMock()
        mock_combo.return_value.get = MagicMock(return_value=self.display_name)
        mock_combo.return_value.configure = MagicMock()

        with (
            patch("win32api.EnumDisplayDevices") as mock_enum_devices,
            patch("ctypes.windll.user32.EnumDisplaySettingsW") as mock_enum_settings,
        ):
            # Setup device enumeration
            mock_enum_devices.side_effect = [self.mock_device, win32api.error]
            mock_enum_settings.return_value = 1

            # Create manager
            manager = DisplayManager()
            return manager, mock_enum_devices, mock_enum_settings

    def test_setup_ui(self, *mocks):
        """Test UI initialization"""
        manager, _, _ = self.create_manager_with_mocks(*mocks)
        self.assertIsNotNone(manager.display_list)
        self.assertIsNotNone(manager.canvas)
        self.assertIsNotNone(manager.x_var)
        self.assertIsNotNone(manager.y_var)
        self.assertIsNotNone(manager.rotation_var)

    @patch("tkinter.messagebox.showerror")
    def test_update_position_invalid_input(self, mock_error, *mocks):
        """Test handling invalid position input"""
        manager, _, _ = self.create_manager_with_mocks(*mocks)
        manager.x_var.set("invalid")
        manager.y_var.set("200")
        manager.update_position()

        mock_error.assert_called_with("Error", "Position must be a number")

    def test_update_position_valid_input(self, *mocks):
        """Test handling valid position input"""
        manager, _, _ = self.create_manager_with_mocks(*mocks)
        manager.display_list.set(self.display_name)
        manager.x_var.set("100")
        manager.y_var.set("200")
        manager.update_position()

        changes = manager.display_config.pending_changes.get(self.display_name, {})
        self.assertEqual(changes.get("x"), 100)
        self.assertEqual(changes.get("y"), 200)

    def test_update_rotation(self, *mocks):
        """Test rotation update"""
        manager, _, _ = self.create_manager_with_mocks(*mocks)
        manager.display_list.set(self.display_name)
        manager.rotation_var.set("90")
        manager.update_rotation()

        changes = manager.display_config.pending_changes.get(self.display_name, {})
        self.assertEqual(changes.get("orientation"), 1)

    @patch("ctypes.windll.user32.ChangeDisplaySettingsExW")
    @patch("tkinter.messagebox.showinfo")
    def test_apply_changes_success(self, mock_info, mock_change_settings, *mocks):
        """Test successful changes application"""
        manager, _, _ = self.create_manager_with_mocks(*mocks)
        mock_change_settings.return_value = 0

        # Make some changes
        manager.display_list.set(self.display_name)
        manager.x_var.set("100")
        manager.y_var.set("200")
        manager.update_position()

        # Apply changes
        manager.apply_changes()
        mock_info.assert_called_with("Success", "Display settings updated successfully")

    @patch("ctypes.windll.user32.ChangeDisplaySettingsExW")
    @patch("tkinter.messagebox.showerror")
    def test_apply_changes_failure(self, mock_error, mock_change_settings, *mocks):
        """Test failed changes application"""
        manager, _, _ = self.create_manager_with_mocks(*mocks)
        mock_change_settings.return_value = 1

        # Make some changes
        manager.display_list.set(self.display_name)
        manager.x_var.set("100")
        manager.y_var.set("200")
        manager.update_position()

        # Apply changes
        manager.apply_changes()
        mock_error.assert_called_with("Error", "Failed to update display settings")

    def test_discard_changes(self, *mocks):
        """Test discarding changes"""
        manager, _, _ = self.create_manager_with_mocks(*mocks)
        manager.display_list.set(self.display_name)
        manager.x_var.set("100")
        manager.y_var.set("200")
        manager.update_position()

        manager.discard_changes()
        self.assertEqual(manager.display_config.pending_changes, {})

    def test_on_display_moved(self, *mocks):
        """Test display movement callback"""
        manager, _, _ = self.create_manager_with_mocks(*mocks)
        manager.display_list.set(self.display_name)
        manager.on_display_moved(self.display_name, 100, 200)

        self.assertEqual(manager.x_var.get(), "100")
        self.assertEqual(manager.y_var.get(), "200")

    def test_refresh_preview(self, *mocks):
        """Test preview refresh"""
        manager, _, _ = self.create_manager_with_mocks(*mocks)

        # Make some changes to have data to refresh
        manager.display_list.set(self.display_name)
        manager.x_var.set("100")
        manager.y_var.set("200")
        manager.update_position()

        # Test refresh
        manager.refresh_preview()

        # Verify that canvas was updated with display information
        self.assertTrue(isinstance(manager.canvas.displays, dict))
        self.assertIn(self.display_name, manager.canvas.displays)

    def test_display_selection(self, *mocks):
        """Test display selection handling"""
        manager, _, _ = self.create_manager_with_mocks(*mocks)
        mock_info = {
            "x": 100,
            "y": 200,
            "width": 1920,
            "height": 1080,
            "orientation": 0,
            "refresh_rate": 60,
            "is_primary": True,
        }

        with patch.object(
            manager.display_config, "get_display_info", return_value=mock_info
        ):
            manager.display_list.set(self.display_name)
            manager.on_display_selected(None)

            self.assertEqual(manager.x_var.get(), "100")
            self.assertEqual(manager.y_var.get(), "200")
            self.assertEqual(manager.rotation_var.get(), "0")

    def test_keyboard_shortcuts(self, *mocks):
        """Test keyboard shortcuts"""
        manager, _, _ = self.create_manager_with_mocks(*mocks)

        # Test Ctrl+A shortcut
        with patch.object(manager, "apply_changes") as mock_apply:
            manager.root.bind.call_args_list[0][0][1](MagicMock(state=4, keysym="a"))
            mock_apply.assert_called_once()

        # Test Escape shortcut
        with patch.object(manager, "discard_changes") as mock_discard:
            manager.root.bind.call_args_list[1][0][1](MagicMock(keysym="Escape"))
            mock_discard.assert_called_once()


if __name__ == "__main__":
    unittest.main()
