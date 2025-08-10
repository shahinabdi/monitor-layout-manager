import tkinter as tk
from tkinter import ttk, messagebox
from src.display_config import DisplayConfig
from src.display_canvas import DisplayCanvas


class DisplayMatrixEditor:
    """A widget for editing display positions in a table format"""
    
    def __init__(self, parent, on_change_callback=None):
        self.parent = parent
        self.on_change_callback = on_change_callback
        self.displays_data = {}
        self.entries = {}
        
        # Create the matrix frame
        self.frame = ttk.LabelFrame(parent, text="Monitor Position Matrix", padding=10)
        
        # Headers
        self.create_headers()
        
    def create_headers(self):
        """Create table headers"""
        headers = ["Display", "X Position", "Y Position", "Width", "Height", "Primary"]
        for col, header in enumerate(headers):
            label = ttk.Label(self.frame, text=header, font=("Arial", 9, "bold"))
            label.grid(row=0, column=col, padx=5, pady=5, sticky="w")
    
    def update_displays(self, displays_data):
        """Update the matrix with current display data"""
        self.displays_data = displays_data
        self.clear_entries()
        self.create_entries()
    
    def clear_entries(self):
        """Clear existing entry widgets"""
        for widget in self.entries.values():
            if hasattr(widget, 'destroy'):
                widget.destroy()
        self.entries.clear()
        
        # Clear all widgets except headers (row 0)
        for widget in self.frame.winfo_children():
            grid_info = widget.grid_info()
            if grid_info and grid_info.get('row', 0) > 0:
                widget.destroy()
    
    def create_entries(self):
        """Create entry widgets for each display"""
        row = 1
        for display_name, display_info in self.displays_data.items():
            # Display name (read-only)
            display_label = ttk.Label(self.frame, text=self.format_display_name(display_name))
            display_label.grid(row=row, column=0, padx=5, pady=2, sticky="w")
            
            # X Position entry
            x_var = tk.StringVar(value=str(display_info.get('x', 0)))
            x_entry = ttk.Entry(self.frame, textvariable=x_var, width=10)
            x_entry.grid(row=row, column=1, padx=5, pady=2)
            x_entry.bind('<KeyRelease>', lambda e, name=display_name, coord='x', var=x_var: 
                        self.on_entry_change(name, coord, var.get()))
            
            # Y Position entry
            y_var = tk.StringVar(value=str(display_info.get('y', 0)))
            y_entry = ttk.Entry(self.frame, textvariable=y_var, width=10)
            y_entry.grid(row=row, column=2, padx=5, pady=2)
            y_entry.bind('<KeyRelease>', lambda e, name=display_name, coord='y', var=y_var: 
                        self.on_entry_change(name, coord, var.get()))
            
            # Width (read-only)
            width_label = ttk.Label(self.frame, text=str(display_info.get('width', 0)))
            width_label.grid(row=row, column=3, padx=5, pady=2)
            
            # Height (read-only)
            height_label = ttk.Label(self.frame, text=str(display_info.get('height', 0)))
            height_label.grid(row=row, column=4, padx=5, pady=2)
            
            # Primary indicator (read-only)
            primary_text = "Yes" if display_info.get('is_primary', False) else "No"
            primary_label = ttk.Label(self.frame, text=primary_text)
            primary_label.grid(row=row, column=5, padx=5, pady=2)
            
            # Store references
            self.entries[display_name] = {
                'x_var': x_var,
                'y_var': y_var,
                'x_entry': x_entry,
                'y_entry': y_entry
            }
            
            row += 1
    
    def format_display_name(self, name):
        """Format display name for better readability"""
        if name.startswith('\\\\.\\'):
            return name.replace('\\\\.\\', '').replace('DISPLAY', 'Monitor ')
        return name
    
    def on_entry_change(self, display_name, coordinate, value):
        """Handle entry value changes"""
        try:
            int_value = int(value)
            if self.on_change_callback:
                self.on_change_callback(display_name, coordinate, int_value)
        except ValueError:
            pass  # Invalid input, ignore
    
    def get_positions(self):
        """Get all positions from the matrix"""
        positions = {}
        for display_name, entries in self.entries.items():
            try:
                x = int(entries['x_var'].get())
                y = int(entries['y_var'].get())
                positions[display_name] = {'x': x, 'y': y}
            except ValueError:
                continue
        return positions
    
    def pack(self, **kwargs):
        """Pack the frame"""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Grid the frame"""
        self.frame.grid(**kwargs)


class DisplayManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Monitor Layout Manager - Enhanced")
        self.root.geometry("1200x800")

        self.display_config = DisplayConfig()
        self.setup_ui()

    def setup_ui(self):
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Visual Editor
        visual_frame = ttk.Frame(notebook)
        notebook.add(visual_frame, text="Visual Editor")
        self.setup_visual_tab(visual_frame)
        
        # Tab 2: Matrix Editor
        matrix_frame = ttk.Frame(notebook)
        notebook.add(matrix_frame, text="Matrix Editor")
        self.setup_matrix_tab(matrix_frame)

    def setup_visual_tab(self, parent):
        """Setup the original visual editor tab"""
        # Main container
        main = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        main.pack(fill=tk.BOTH, expand=True)

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

    def setup_matrix_tab(self, parent):
        """Setup the matrix editor tab"""
        # Main container
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Instructions
        instructions = ttk.Label(
            main_frame, 
            text="Edit monitor positions by modifying X and Y coordinates in the table below.\n"
                 "Changes are applied immediately to the preview. Click 'Apply All Changes' to save.",
            font=("Arial", 10)
        )
        instructions.pack(pady=(0, 10))
        
        # Matrix editor
        self.matrix_editor = DisplayMatrixEditor(main_frame, self.on_matrix_change)
        self.matrix_editor.pack(fill=tk.X, pady=10)
        
        # Quick positioning buttons
        quick_frame = ttk.LabelFrame(main_frame, text="Quick Positioning", padding=10)
        quick_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(quick_frame, text="Horizontal Line", command=self.arrange_horizontal).pack(side=tk.LEFT, padx=5)
        ttk.Button(quick_frame, text="Vertical Stack", command=self.arrange_vertical).pack(side=tk.LEFT, padx=5)
        ttk.Button(quick_frame, text="Reset to Origin", command=self.reset_to_origin).pack(side=tk.LEFT, padx=5)
        
        # Preview canvas for matrix tab
        preview_matrix_frame = ttk.LabelFrame(main_frame, text="Layout Preview", padding=5)
        preview_matrix_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.matrix_canvas = DisplayCanvas(
            preview_matrix_frame, self.on_matrix_display_moved, bg="white", width=800, height=300
        )
        self.matrix_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Matrix action buttons
        matrix_btn_frame = ttk.Frame(main_frame)
        matrix_btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(matrix_btn_frame, text="Apply All Changes", command=self.apply_changes).pack(side=tk.LEFT, padx=5)
        ttk.Button(matrix_btn_frame, text="Discard All Changes", command=self.discard_changes).pack(side=tk.LEFT, padx=5)
        ttk.Button(matrix_btn_frame, text="Refresh Matrix", command=self.refresh_matrix).pack(side=tk.LEFT, padx=5)

        # Keyboard shortcuts
        self.root.bind("<Control-a>", lambda e: self.apply_changes())
        self.root.bind("<Escape>", lambda e: self.discard_changes())

        # Initialize display list
        self.update_display_list()

    def on_matrix_change(self, display_name, coordinate, value):
        """Handle changes from the matrix editor"""
        if coordinate == 'x':
            current_y = self.display_config.get_display_info(display_name).get('y', 0)
            self.display_config.set_position(display_name, value, current_y)
        elif coordinate == 'y':
            current_x = self.display_config.get_display_info(display_name).get('x', 0)
            self.display_config.set_position(display_name, current_x, value)
        
        self.refresh_preview()
    
    def on_matrix_display_moved(self, display_name, x, y):
        """Handle display being moved in the matrix canvas"""
        self.display_config.set_position(display_name, x, y)
        # Update matrix entries
        if hasattr(self, 'matrix_editor') and display_name in self.matrix_editor.entries:
            self.matrix_editor.entries[display_name]['x_var'].set(str(x))
            self.matrix_editor.entries[display_name]['y_var'].set(str(y))
        self.refresh_preview()
    
    def arrange_horizontal(self):
        """Arrange all monitors in a horizontal line"""
        displays = list(self.display_config.displays.keys())
        x_offset = 0
        
        for display_name in displays:
            info = self.display_config.get_display_info(display_name)
            if info:
                self.display_config.set_position(display_name, x_offset, 0)
                x_offset += info['width']
        
        self.refresh_matrix()
        self.refresh_preview()
    
    def arrange_vertical(self):
        """Arrange all monitors in a vertical stack"""
        displays = list(self.display_config.displays.keys())
        y_offset = 0
        
        for display_name in displays:
            info = self.display_config.get_display_info(display_name)
            if info:
                self.display_config.set_position(display_name, 0, y_offset)
                y_offset += info['height']
        
        self.refresh_matrix()
        self.refresh_preview()
    
    def reset_to_origin(self):
        """Reset all monitors to origin (0,0)"""
        for display_name in self.display_config.displays.keys():
            self.display_config.set_position(display_name, 0, 0)
        
        self.refresh_matrix()
        self.refresh_preview()

    def update_display_list(self):
        """Update the display selection dropdown"""
        displays = self.display_config.displays
        if hasattr(self, 'display_list'):
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

        if hasattr(self, 'canvas'):
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
        if hasattr(self, 'display_list') and display_name == self.display_list.get():
            self.x_var.set(str(x))
            self.y_var.set(str(y))
        self.refresh_preview()

    def refresh_preview(self):
        """Update the canvas preview with current display information"""
        displays = {
            name: self.display_config.get_display_info(name)
            for name in self.display_config.displays.keys()
        }
        
        if hasattr(self, 'canvas'):
            self.canvas.update_displays(displays)
        if hasattr(self, 'matrix_canvas'):
            self.matrix_canvas.update_displays(displays)
    
    def refresh_matrix(self):
        """Refresh the matrix editor with current display data"""
        if hasattr(self, 'matrix_editor'):
            displays = {
                name: self.display_config.get_display_info(name)
                for name in self.display_config.displays.keys()
            }
            self.matrix_editor.update_displays(displays)

    def apply_changes(self):
        """Apply all pending changes"""
        if self.display_config.apply_changes():
            messagebox.showinfo("Success", "Display settings updated successfully")
            self.refresh_preview()
            self.refresh_matrix()
        else:
            messagebox.showerror("Error", "Failed to update display settings")

    def discard_changes(self):
        """Discard all pending changes"""
        self.display_config.discard_changes()
        self.refresh_preview()
        self.refresh_matrix()
        # Reset UI to current settings
        if hasattr(self, 'display_list'):
            self.on_display_selected(None)

    def run(self):
        """Start the application"""
        # Initialize both editors
        self.refresh_matrix()
        self.refresh_preview()
        self.root.mainloop()


if __name__ == "__main__":
    app = DisplayManager()
    app.run()