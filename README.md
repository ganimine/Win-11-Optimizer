# Windows Optimizer App

A simple Windows 11 optimizer app built with Python and Tkinter.

## Features
- Clean temporary files
- Manage startup programs
- Clear Recycle Bin
- Free up RAM

## Requirements
- Python 3.8+
- Tkinter (usually included with Python)

## How to Build and Install (MSI Installer)
1. Build the standalone executable with PyInstaller (already done if you have `dist/main.exe`).
2. Install [WiX Toolset](https://wixtoolset.org/releases/) and ensure `candle` and `light` are in your PATH.
3. In this folder, run:
   ```sh
   candle Product.wxs
   light Product.wixobj -o Windows11Optimizer.msi
   ```
4. Double-click `Windows11Optimizer.msi` to install the app with a wizard.

## How to Run (Portable)
1. Install Python 3.8 or higher.
2. Install required packages (if any).
3. Run the main script:
   ```sh
   python main.py
   ```

## Notes
- This app is designed for Windows 11.
- Run as administrator for full functionality.
