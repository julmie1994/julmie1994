@echo off
setlocal

if not exist .venv (
  echo [INFO] Creating virtual environment...
  py -3 -m venv .venv
)

call .venv\Scripts\activate
pip install -e .[dev]

pyinstaller --noconfirm --name OpenVisionStudio --windowed ^
  --collect-all openvisionstudio ^
  --add-data "src/openvisionstudio/resources;openvisionstudio/resources" ^
  -m openvisionstudio

echo Build complete. See dist\OpenVisionStudio
endlocal
