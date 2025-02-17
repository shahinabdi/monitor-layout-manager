import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk
from src.display_canvas import DisplayCanvas


class TestDisplayCanvas(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.on_display_moved = MagicMock()
        self.canvas = DisplayCanvas(self.root, self.on_display_moved)
        self.test_displays = {
            "DISPLAY1": {
                "x": 0,
                "y": 0,
                "width": 1920,
                "height": 1080,
                "orientation": 0,
            }
        }

    def tearDown(self):
        self.root.destroy()

    def test_coordinate_conversion_roundtrip(self):
        """Test coordinate conversion in both directions"""
        original_x, original_y = 1920, 1080
        canvas_x, canvas_y = self.canvas.screen_to_canvas(original_x, original_y)
        screen_x, screen_y = self.canvas.canvas_to_screen(canvas_x, canvas_y)

        self.assertAlmostEqual(original_x, screen_x, delta=1)
        self.assertAlmostEqual(original_y, screen_y, delta=1)

    def test_screen_to_canvas_origin(self):
        """Test conversion of screen origin"""
        canvas_x, canvas_y = self.canvas.screen_to_canvas(0, 0)
        self.assertEqual(canvas_x, self.canvas.offset_x)
        self.assertEqual(canvas_y, self.canvas.offset_y)

    def test_canvas_to_screen_origin(self):
        """Test conversion of canvas origin"""
        screen_x, screen_y = self.canvas.canvas_to_screen(
            self.canvas.offset_x, self.canvas.offset_y
        )
        self.assertEqual(screen_x, 0)
        self.assertEqual(screen_y, 0)

    def test_update_displays(self):
        """Test display update functionality"""
        self.canvas.update_displays(self.test_displays)
        self.assertEqual(self.canvas.displays, self.test_displays)

    def test_select_display(self):
        """Test display selection"""
        # Test selection
        self.canvas.select_display("DISPLAY1")
        self.assertEqual(self.canvas.selected, "DISPLAY1")

        # Test deselection
        self.canvas.select_display(None)
        self.assertIsNone(self.canvas.selected)

    def test_start_drag(self):
        """Test drag initiation"""
        # Setup mock event
        event = MagicMock()
        event.x = 100
        event.y = 100

        # Setup canvas with mock find_closest
        with patch.object(self.canvas, "find_closest", return_value=(1,)):
            with patch.object(self.canvas, "gettags", return_value=("DISPLAY1",)):
                self.canvas.update_displays(self.test_displays)
                self.canvas.start_drag(event)

                self.assertEqual(self.canvas._drag_data["x"], event.x)
                self.assertEqual(self.canvas._drag_data["y"], event.y)
                self.assertEqual(self.canvas._drag_data["display"], "DISPLAY1")

    def test_drag(self):
        """Test drag operation"""
        # Setup
        self.canvas.update_displays(self.test_displays)

        # Initial drag setup
        start_event = MagicMock()
        start_event.x = 100
        start_event.y = 100

        with patch.object(self.canvas, "find_closest", return_value=(1,)):
            with patch.object(self.canvas, "gettags", return_value=("DISPLAY1",)):
                self.canvas.start_drag(start_event)

        # Test drag
        drag_event = MagicMock()
        drag_event.x = 150  # Moved 50px right
        drag_event.y = 150  # Moved 50px down

        self.canvas.drag(drag_event)

        # Verify on_display_moved was called with correct coordinates
        screen_x, screen_y = self.canvas.canvas_to_screen(drag_event.x, drag_event.y)
        self.on_display_moved.assert_called_with("DISPLAY1", screen_x, screen_y)

    def test_end_drag(self):
        """Test ending drag operation"""
        # Setup drag
        self.canvas._drag_data = {"x": 100, "y": 100, "display": "DISPLAY1"}

        # End drag
        self.canvas.end_drag(None)

        # Verify drag data is reset
        self.assertIsNone(self.canvas._drag_data["display"])
        self.assertEqual(self.canvas._drag_data["x"], 0)
        self.assertEqual(self.canvas._drag_data["y"], 0)

    def test_reset_view(self):
        """Test view reset functionality"""
        # Change view parameters
        self.canvas.scale = 0.5
        self.canvas.offset_x = 200
        self.canvas.offset_y = 200

        # Reset view
        self.canvas.reset_view()

        # Verify defaults are restored
        self.assertEqual(self.canvas.scale, 0.1)
        self.assertEqual(self.canvas.offset_x, 100)
        self.assertEqual(self.canvas.offset_y, 100)

    @patch("tkinter.Canvas.create_line")
    @patch("tkinter.Canvas.create_rectangle")
    @patch("tkinter.Canvas.create_text")
    def test_redraw(self, mock_create_text, mock_create_rectangle, mock_create_line):
        """Test canvas redraw functionality"""
        self.canvas.update_displays(self.test_displays)
        self.canvas.redraw()

        # Verify that drawing methods were called
        mock_create_line.assert_called()  # Grid lines
        mock_create_rectangle.assert_called()  # Display rectangles
        mock_create_text.assert_called()  # Display labels

    def test_on_mousewheel(self):
        """Test mousewheel scrolling"""
        event = MagicMock()
        event.delta = 120  # Scroll up
        event.state = 0  # No modifier keys

        original_offset = self.canvas.offset_y
        self.canvas.on_mousewheel(event)

        # Verify offset changed
        self.assertNotEqual(self.canvas.offset_y, original_offset)

    def test_on_zoom(self):
        """Test zoom functionality"""
        event = MagicMock()
        event.delta = 120  # Zoom in

        original_scale = self.canvas.scale
        self.canvas.on_zoom(event)

        # Verify scale changed
        self.assertNotEqual(self.canvas.scale, original_scale)

        # Test zoom limits
        # Test minimum zoom
        for _ in range(100):  # Zoom out many times
            event.delta = -120
            self.canvas.on_zoom(event)
        self.assertGreaterEqual(self.canvas.scale, 0.01)

        # Test maximum zoom
        for _ in range(100):  # Zoom in many times
            event.delta = 120
            self.canvas.on_zoom(event)
        self.assertLessEqual(self.canvas.scale, 1.0)


if __name__ == "__main__":
    unittest.main()
