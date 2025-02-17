import tkinter as tk
from typing import Dict, Optional, Callable


class DisplayCanvas(tk.Canvas):
    def __init__(self, master, on_display_moved: Callable, **kwargs):
        super().__init__(master, **kwargs)
        self.on_display_moved = on_display_moved
        self.displays: Dict[str, Dict] = {}
        self.selected: Optional[str] = None
        self.scale = 0.1
        self.offset_x = 100
        self.offset_y = 100

        # Add scroll support
        self.bind("<MouseWheel>", self.on_mousewheel)
        self.bind("<Control-MouseWheel>", self.on_zoom)

        # For panning
        self.bind("<Control-ButtonPress-1>", self.start_pan)
        self.bind("<Control-B1-Motion>", self.pan)

        # Drag handling
        self.bind("<ButtonPress-1>", self.start_drag)
        self.bind("<B1-Motion>", self.drag)
        self.bind("<ButtonRelease-1>", self.end_drag)
        self._drag_data = {"x": 0, "y": 0, "display": None}

    def screen_to_canvas(self, x: int, y: int) -> tuple[int, int]:
        """Convert screen coordinates to canvas coordinates"""
        return (
            int(x * self.scale + self.offset_x),
            int(y * self.scale + self.offset_y),
        )

    def canvas_to_screen(self, x: int, y: int) -> tuple[int, int]:
        """Convert canvas coordinates to screen coordinates"""
        return (
            int((x - self.offset_x) / self.scale),
            int((y - self.offset_y) / self.scale),
        )

    def update_displays(self, displays: Dict[str, Dict]) -> None:
        """Update the display layout"""
        self.displays = displays
        self.redraw()

    def redraw(self) -> None:
        """Redraw all displays"""
        self.delete("all")

        # Calculate grid parameters
        grid_step = 100  # Real screen coordinates (pixels)
        w = self.winfo_width()
        h = self.winfo_height()

        # Find visible area bounds in screen coordinates
        left = -self.offset_x / self.scale
        right = (w - self.offset_x) / self.scale
        top = -self.offset_y / self.scale
        bottom = (h - self.offset_y) / self.scale

        # Draw major grid lines (every 500 pixels)
        major_step = 500

        # Vertical major grid lines
        for x in range(
            int(left // major_step) * major_step, int(right) + major_step, major_step
        ):
            canvas_x = x * self.scale + self.offset_x
            self.create_line(canvas_x, 0, canvas_x, h, fill="#CCCCCC", width=2)
            self.create_text(
                canvas_x, 20, text=str(x), fill="#666666", font=("Arial", 8, "bold")
            )

        # Horizontal major grid lines
        for y in range(
            int(top // major_step) * major_step, int(bottom) + major_step, major_step
        ):
            canvas_y = y * self.scale + self.offset_y
            self.create_line(0, canvas_y, w, canvas_y, fill="#CCCCCC", width=2)
            self.create_text(
                20, canvas_y, text=str(y), fill="#666666", font=("Arial", 8, "bold")
            )

        # Draw minor grid lines
        for x in range(
            int(left // grid_step) * grid_step, int(right) + grid_step, grid_step
        ):
            if x % major_step != 0:  # Skip if major line
                canvas_x = x * self.scale + self.offset_x
                self.create_line(canvas_x, 0, canvas_x, h, fill="#EEEEEE")

        for y in range(
            int(top // grid_step) * grid_step, int(bottom) + grid_step, grid_step
        ):
            if y % major_step != 0:  # Skip if major line
                canvas_y = y * self.scale + self.offset_y
                self.create_line(0, canvas_y, w, canvas_y, fill="#EEEEEE")

        # Draw displays
        for name, display in self.displays.items():
            x, y = self.screen_to_canvas(display["x"], display["y"])
            width = int(display["width"] * self.scale)
            height = int(display["height"] * self.scale)

            # Display rectangle
            fill = "#E3F2FD" if name == self.selected else "white"
            self.create_rectangle(
                x,
                y,
                x + width,
                y + height,
                fill=fill,
                outline="#2196F3",
                width=2,
                tags=(name, "display"),
            )

            # Display information
            self.create_text(
                x + width / 2,
                y + height / 2,
                text=f"{name}\n{display['width']}x{display['height']}",
                tags=(name, "display"),
            )

    def select_display(self, name: Optional[str]) -> None:
        """Select a display"""
        self.selected = name
        self.redraw()

    def start_drag(self, event):
        """Start dragging a display"""
        x, y = event.x, event.y
        items = self.find_closest(x, y)

        for name in self.displays:
            if name in self.gettags(items[0]):
                self._drag_data = {"x": x, "y": y, "display": name}
                self.select_display(name)
                break

    def drag(self, event):
        """Handle display dragging"""
        if not self._drag_data["display"]:
            return

        # Calculate the distance moved
        dx = event.x - self._drag_data["x"]
        dy = event.y - self._drag_data["y"]

        # Update stored position
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

        # Convert to screen coordinates
        screen_x, screen_y = self.canvas_to_screen(event.x, event.y)

        # Notify about the move
        self.on_display_moved(self._drag_data["display"], screen_x, screen_y)

    def end_drag(self, event):
        """End display dragging"""
        self._drag_data = {"x": 0, "y": 0, "display": None}

    def on_mousewheel(self, event):
        """Handle scrolling"""
        if event.state != 0:  # Ignore if any modifier keys are pressed
            return

        # Scroll amount based on OS/platform
        delta = -1 * (event.delta // 120)
        self.offset_y += delta * 50
        self.redraw()

    def on_zoom(self, event):
        """Handle zooming with Ctrl+MouseWheel"""
        delta = event.delta // 120
        if delta > 0:
            self.scale *= 1.1
        else:
            self.scale /= 1.1

        # Limit scale range
        self.scale = max(0.01, min(1.0, self.scale))
        self.redraw()

    def start_pan(self, event):
        """Start canvas panning"""
        self._drag_data = {"x": event.x, "y": event.y, "display": None}

    def pan(self, event):
        """Handle canvas panning"""
        if not self._drag_data["display"]:  # Only pan if not dragging a display
            dx = event.x - self._drag_data["x"]
            dy = event.y - self._drag_data["y"]
            self.offset_x += dx
            self.offset_y += dy
            self._drag_data["x"] = event.x
            self._drag_data["y"] = event.y
            self.redraw()

    def reset_view(self):
        """Reset view to default position and scale"""
        self.scale = 0.1
        self.offset_x = 100
        self.offset_y = 100
        self.redraw()
