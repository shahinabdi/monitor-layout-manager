# Monitor Layout Manager

A Windows utility for precise monitor positioning and layout management. This tool provides more accurate control over multi-monitor setups than the default Windows display settings.

[![Tests](https://github.com/shahinabdi/monitor-layout-manager/actions/workflows/test.yml/badge.svg)](https://github.com/shahinabdi/monitor-layout-manager/actions/workflows/test.yml)
[![Build and Release](https://github.com/shahinabdi/monitor-layout-manager/actions/workflows/release.yml/badge.svg)](https://github.com/shahinabdi/monitor-layout-manager/actions/workflows/release.yml)

## Features

- Precise monitor positioning with exact coordinates
- Visual drag-and-drop interface with coordinate grid
- Support for monitor rotation
- Real-time preview of monitor layouts
- Changes are saved permanently
- Zoom and pan functionality for detailed positioning
- Administrative privileges handling

## Installation

### Option 1: Download Executable
1. Download the latest release from the [releases page](https://github.com/shahinabdi/monitor-layout-manager/releases)
2. Run the executable (requires administrator privileges)

### Option 2: Run from Source
1. Clone the repository:
```bash
git clone https://github.com/shahinabdi/monitor-layout-manager.git
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application (with administrator privileges):
```bash
python src/main.py
```

## Usage

1. Launch the application (requires administrator privileges)
2. Select a monitor from the dropdown list
3. Adjust position using:
   - Direct coordinate input
   - Drag and drop in the preview
   - Arrow keys for fine adjustments
4. Click "Apply Changes" to save your layout
5. Use Ctrl+MouseWheel to zoom and Ctrl+Drag to pan the preview

## Development

### Setup Development Environment

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install development dependencies:
```bash
pip install -r requirements.txt
```

### Running Tests

Run all tests:
```bash
python -m pytest tests/
```

Run tests with coverage:
```bash
python -m pytest tests/ --cov=src/ --cov-report=html
```

### Building from Source

To create an executable:

1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Build the executable:
```bash
pyinstaller monitor_app.spec
```

The executable will be created in the `dist` folder.

### CI/CD

The project uses GitHub Actions for:
- Automated testing on push and pull requests
- Building and releasing new versions when tags are pushed

To create a new release:
```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

## Project Structure

```
monitor-layout-manager/
├── src/                     # Source code
│   ├── main.py             # Main application
│   ├── display_config.py   # Windows display API interface
│   └── display_canvas.py   # Visual preview component
├── tests/                  # Test files
│   ├── conftest.py        # Test configuration
│   ├── test_display_config.py
│   └── test_display_canvas.py
├── .github/                # GitHub configuration
│   └── workflows/         # GitHub Actions workflows
├── requirements.txt        # Python dependencies
├── monitor_app.spec       # PyInstaller specification
└── README.md              # This file
```

## Requirements

- Windows 10/11
- Administrator privileges
- Python 3.8 or higher (for running from source)

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Run tests to ensure they pass
4. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
5. Push to the branch (`git push origin feature/AmazingFeature`)
6. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Shahin ABDI**
- GitHub: [@shahinabdi](https://github.com/shahinabdi)

## Support

If you encounter any issues or have suggestions:
1. Check the [Issues](https://github.com/shahinabdi/monitor-layout-manager/issues) page
2. Open a new issue if needed

## Acknowledgments

- Windows Display API documentation
- PyWin32 project