@echo off
echo Building Monitor Manager...
pyinstaller --clean monitor_app.spec
echo Done!
pause