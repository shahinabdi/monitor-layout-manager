import unittest
from unittest.mock import MagicMock
import tkinter as tk


class TkinterTestCase(unittest.TestCase):
    """Base class for Tkinter tests that handles window creation and cleanup"""

    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window

    def tearDown(self):
        self.root.destroy()

    def simulate_event(self, widget, event_name, event_data=None):
        """Simulate a Tkinter event"""
        if event_data is None:
            event_data = {}

        event = MagicMock()
        for key, value in event_data.items():
            setattr(event, key, value)

        widget.event_generate(event_name)
        return event


def create_mock_display(
    name, x=0, y=0, width=1920, height=1080, orientation=0, is_primary=False
):
    """Create a mock display for testing"""
    return {
        "name": name,
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "orientation": orientation,
        "is_primary": is_primary,
    }


def create_mock_event(**kwargs):
    """Create a mock event with given attributes"""
    event = MagicMock()
    for key, value in kwargs.items():
        setattr(event, key, value)
    return event
