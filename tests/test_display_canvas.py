import unittest
from unittest.mock import MagicMock
import tkinter as tk
from src.display_canvas import DisplayCanvas


class TestDisplayCanvas(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.on_display_moved = MagicMock()
        self.canvas = DisplayCanvas(self.root, self.on_display_moved)

    def tearDown(self):
        self.root.destroy()

    def test_screen_to_canvas_conversion(self):
        # Test coordinate conversion
        screen_x, screen_y = 1920, 1080
        canvas_x, canvas_y = self.canvas.screen_to_canvas(screen_x, screen_y)

        # Convert back
        back_x, back_y = self.canvas.canvas_to_screen(canvas_x, canvas_y)

        # Verify roundtrip conversion
        self.assertAlmostEqual(screen_x, back_x, delta=1)
        self.assertAlmostEqual(screen_y, back_y, delta=1)

    def test_update_displays(self):
        # Test display update
        test_displays = {
            "DISPLAY1": {
                "x": 0,
                "y": 0,
                "width": 1920,
                "height": 1080,
                "orientation": 0,
            }
        }

        self.canvas.update_displays(test_displays)
        self.assertEqual(self.canvas.displays, test_displays)

    def test_select_display(self):
        # Test display selection
        self.canvas.select_display("DISPLAY1")
        self.assertEqual(self.canvas.selected, "DISPLAY1")

        # Test deselection
        self.canvas.select_display(None)
        self.assertIsNone(self.canvas.selected)


if __name__ == "__main__":
    unittest.main()
