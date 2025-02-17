import pytest
import tkinter as tk


@pytest.fixture(scope="function")
def tk_root():
    root = tk.Tk()
    yield root
    root.destroy()


@pytest.fixture(scope="session")
def mock_display_data():
    return {
        r"\.\DISPLAY1": {
            "x": 0,
            "y": 0,
            "width": 1920,
            "height": 1080,
            "orientation": 0,
            "refresh_rate": 60,
        },
        r"\.\DISPLAY2": {
            "x": 1920,
            "y": 0,
            "width": 1920,
            "height": 1080,
            "orientation": 0,
            "refresh_rate": 144,
        },
    }
