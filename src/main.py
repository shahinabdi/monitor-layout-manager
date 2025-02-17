import tkinter as tk
from tkinter import ttk, messagebox
from src.display_config import DisplayConfig
from src.display_canvas import DisplayCanvas


class DisplayManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Display Manager")
        self.root.geometry("1000x600")

        self.display_config = DisplayConfig()
        self.setup_ui()

    def setup_ui(self):
        # Main container
        main = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left control panel
        controls = ttk.Frame(main)
        main.add(controls, weight=1)

        # Display selection
        select_frame = ttk.LabelFrame(controls, text="Select Display", padding=5)
        select_frame.pack(fill=tk.X, pady=5)

        self.display_list = ttk.Combobox(select_frame, state="readonly")
        self.display_list.pack(fill=tk.X)
        self.display_list.bind("<<ComboboxSelected>>", self.on_display_selected)

        # Position controls
        pos_frame = ttk.LabelFrame(controls, text="Position", padding=5)
        pos_frame.pack(fill=tk.X, pady=5)

        # X position
        ttk.Label(pos_frame, text="X:").grid(row=0, column=0, padx=5)
        self.x_var = tk.StringVar()
        self.x_entry = ttk.Entry(pos_frame, textvariable=self.x_var, width=8)
        self.x_entry.grid(row=0, column=1, padx=5)
        self.x_entry.bind("<Return>", lambda e: self.update_position())

        # Y position
        ttk.Label(pos_frame, text="Y:").grid(row=0, column=2, padx=5)
        self.y_var = tk.StringVar()
        self.y_entry = ttk.Entry(pos_frame, textvariable=self.y_var, width=8)
        self.y_entry.grid(row=0, column=3, padx=5)
        self.y_entry.bind("<Return>", lambda e: self.update_position())

        # Orientation
        ttk.Label(pos_frame, text="Rotation:").grid(row=1, column=0, padx=5, pady=5)
        self.rotation_var = tk.StringVar(value="0")
        rotation = ttk.Combobox(
            pos_frame,
            textvariable=self.rotation_var,
            values=["0", "90", "180", "270"],
            state="readonly",
            width=5,
        )
        rotation.grid(row=1, column=1, padx=5, pady=5)
        rotation.bind("<<ComboboxSelected>>", self.update_rotation)

        # Action buttons
        btn_frame = ttk.Frame(controls)
        btn_frame.pack(fill=tk.X, pady=10)

        ttk.Button(btn_frame, text="Apply Changes", command=self.apply_changes).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(
            btn_frame, text="Discard Changes", command=self.discard_changes
        ).pack(side=tk.LEFT)

        # Display information
        info_frame = ttk.LabelFrame(controls, text="Display Information", padding=5)
        info_frame.pack(fill=tk.X, pady=5)
        self.info_text = tk.Text(info_frame, height=5, width=30)
        self.info_text.pack(fill=tk.X)

        # Canvas/Preview area
        preview_frame = ttk.LabelFrame(main, text="Layout Preview", padding=5)
        main.add(preview_frame, weight=2)

        self.canvas = DisplayCanvas(
            preview_frame, self.on_display_moved, bg="white", width=600, height=400
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Add view controls
        view_frame = ttk.Frame(preview_frame)
        view_frame.pack(fill=tk.X, pady=5)
        ttk.Button(view_frame, text="Reset View", command=self.canvas.reset_view).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Label(
            view_frame, text="Tip: Ctrl+MouseWheel to zoom, Ctrl+Drag to pan"
        ).pack(side=tk.LEFT)

        # Keyboard shortcuts
        self.root.bind("<Control-a>", lambda e: self.apply_changes())
        self.root.bind("<Escape>", lambda e: self.discard_changes())

        # Initialize display list
        self.update_display_list()

    def update_display_list(self):
        """Update the display selection dropdown"""
        displays = self.display_config.displays
        self.display_list["values"] = list(displays.keys())
        if displays and not self.display_list.get():
            self.display_list.set(list(displays.keys())[0])
            self.on_display_selected(None)

    def on_display_selected(self, event):
        """Handle display selection change"""
        selected = self.display_list.get()
        if not selected:
            return

        info = self.display_config.get_display_info(selected)
        if info:
            self.x_var.set(str(info["x"]))
            self.y_var.set(str(info["y"]))
            self.rotation_var.set(str(info["orientation"] * 90))

            # Update info text
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(
                1.0,
                (
                    f"Resolution: {info['width']}x{info['height']}\n"
                    f"Refresh Rate: {info['refresh_rate']}Hz\n"
                    f"Primary: {'Yes' if info['is_primary'] else 'No'}\n"
                    f"Current Position: ({info['x']}, {info['y']})"
                ),
            )

        self.canvas.select_display(selected)

    def update_position(self):
        """Update display position from entry fields"""
        selected = self.display_list.get()
        if not selected:
            return

        try:
            x = int(self.x_var.get())
            y = int(self.y_var.get())
            self.display_config.set_position(selected, x, y)
            self.refresh_preview()
        except ValueError:
            messagebox.showerror("Error", "Position must be a number")

    def update_rotation(self, event=None):
        """Update display rotation"""
        selected = self.display_list.get()
        if not selected:
            return

        try:
            rotation = int(self.rotation_var.get()) // 90
            self.display_config.set_orientation(selected, rotation)
            self.refresh_preview()
        except ValueError:
            messagebox.showerror("Error", "Invalid rotation value")

    def on_display_moved(self, display_name: str, x: int, y: int):
        """Handle display being moved in the canvas"""
        self.display_config.set_position(display_name, x, y)
        if display_name == self.display_list.get():
            self.x_var.set(str(x))
            self.y_var.set(str(y))
        self.refresh_preview()

    def refresh_preview(self):
        """Update the canvas preview with current display information"""
        displays = {
            name: self.display_config.get_display_info(name)
            for name in self.display_config.displays.keys()
        }
        self.canvas.update_displays(displays)

    def apply_changes(self):
        """Apply all pending changes"""
        if self.display_config.apply_changes():
            messagebox.showinfo("Success", "Display settings updated successfully")
            self.refresh_preview()
        else:
            messagebox.showerror("Error", "Failed to update display settings")

    def discard_changes(self):
        """Discard all pending changes"""
        self.display_config.discard_changes()
        self.refresh_preview()
        # Reset UI to current settings
        self.on_display_selected(None)

    def run(self):
        """Start the application"""
        self.root.mainloop()


if __name__ == "__main__":
    app = DisplayManager()
    app.run()
