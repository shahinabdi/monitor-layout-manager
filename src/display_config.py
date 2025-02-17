# display_config.py
import ctypes
import win32api
import win32con
from typing import Dict, Optional


class DEVMODE(ctypes.Structure):
    _fields_ = [
        ("dmDeviceName", ctypes.c_wchar * 32),
        ("dmSpecVersion", ctypes.c_ushort),
        ("dmDriverVersion", ctypes.c_ushort),
        ("dmSize", ctypes.c_ushort),
        ("dmDriverExtra", ctypes.c_ushort),
        ("dmFields", ctypes.c_ulong),
        ("dmPositionX", ctypes.c_long),
        ("dmPositionY", ctypes.c_long),
        ("dmDisplayOrientation", ctypes.c_ulong),
        ("dmDisplayFixedOutput", ctypes.c_ulong),
        ("dmColor", ctypes.c_short),
        ("dmDuplex", ctypes.c_short),
        ("dmYResolution", ctypes.c_short),
        ("dmTTOption", ctypes.c_short),
        ("dmCollate", ctypes.c_short),
        ("dmFormName", ctypes.c_wchar * 32),
        ("dmLogPixels", ctypes.c_ushort),
        ("dmBitsPerPel", ctypes.c_ulong),
        ("dmPelsWidth", ctypes.c_ulong),
        ("dmPelsHeight", ctypes.c_ulong),
        ("dmDisplayFlags", ctypes.c_ulong),
        ("dmDisplayFrequency", ctypes.c_ulong),
    ]


class DisplayConfig:
    def __init__(self):
        self.displays: Dict[str, DEVMODE] = {}
        self.pending_changes: Dict[str, Dict] = {}
        self.enumerate_displays()

    def enumerate_displays(self) -> None:
        """Get all connected displays and their current settings"""
        i = 0
        self.displays.clear()

        while True:
            try:
                device = win32api.EnumDisplayDevices(None, i)
                if not device.StateFlags & win32con.DISPLAY_DEVICE_ATTACHED_TO_DESKTOP:
                    i += 1
                    continue

                settings = DEVMODE()
                settings.dmSize = ctypes.sizeof(DEVMODE)

                if ctypes.windll.user32.EnumDisplaySettingsW(
                    device.DeviceName,
                    -1,  # ENUM_CURRENT_SETTINGS
                    ctypes.byref(settings),
                ):
                    self.displays[device.DeviceName] = settings

                i += 1
            except win32api.error:
                break

    def get_display_info(self, device_name: str) -> Optional[Dict]:
        """Get display information in a dictionary format"""
        if device_name not in self.displays:
            return None

        display = self.displays[device_name]
        pending = self.pending_changes.get(device_name, {})

        return {
            "name": device_name,
            "x": pending.get("x", display.dmPositionX),
            "y": pending.get("y", display.dmPositionY),
            "width": display.dmPelsWidth,
            "height": display.dmPelsHeight,
            "orientation": pending.get("orientation", display.dmDisplayOrientation),
            "refresh_rate": display.dmDisplayFrequency,
            "is_primary": bool(
                display.dmDisplayFlags & 0x00000001
            ),  # Primary display flag
        }

    def set_position(self, device_name: str, x: int, y: int) -> None:
        """Queue position change for a display"""
        if device_name not in self.displays:
            return

        if device_name not in self.pending_changes:
            self.pending_changes[device_name] = {}

        self.pending_changes[device_name].update({"x": x, "y": y})

    def set_orientation(self, device_name: str, orientation: int) -> None:
        """Queue orientation change for a display"""
        if device_name not in self.displays:
            return

        if device_name not in self.pending_changes:
            self.pending_changes[device_name] = {}

        self.pending_changes[device_name]["orientation"] = orientation % 4

    def apply_changes(self) -> bool:
        """Apply all pending changes"""
        success = True
        for device_name, changes in self.pending_changes.items():
            display = self.displays[device_name]

            if "x" in changes:
                display.dmPositionX = changes["x"]
            if "y" in changes:
                display.dmPositionY = changes["y"]
            if "orientation" in changes:
                display.dmDisplayOrientation = changes["orientation"]

            # Combine flags to make changes permanent
            flags = (
                0x00000001  # CDS_UPDATEREGISTRY
                | 0x00000002  # CDS_NORESET
                | 0x00000004  # CDS_GLOBAL
            )

            # First update with NORESET flag
            result = ctypes.windll.user32.ChangeDisplaySettingsExW(
                device_name, ctypes.byref(display), None, flags, None
            )

            # Then apply changes globally
            ctypes.windll.user32.ChangeDisplaySettingsExW(
                None,
                None,
                None,
                0,  # APPLY NOW
                None,
            )

            if result != 0:  # DISP_CHANGE_SUCCESSFUL
                success = False

        self.pending_changes.clear()
        self.enumerate_displays()  # Refresh display information
        return success

    def discard_changes(self) -> None:
        """Discard all pending changes"""
        self.pending_changes.clear()
