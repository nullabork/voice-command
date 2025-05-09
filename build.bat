@echo off
echo Building VoiceCommand executable with Nuitka...

:: Clean previous build
echo Cleaning previous build...
rd /s /q "dist" 2>nul
rd /s /q "build" 2>nul
rd /s /q "VoiceCommand.dist" 2>nul
rd /s /q "VoiceCommand.build" 2>nul
rd /s /q "__pycache__" 2>nul

:: Check if Nuitka is installed, install if not
pip show nuitka >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installing Nuitka...
    pip install nuitka
)

:: Build the application with Nuitka
echo Building with Nuitka...
python -m nuitka --standalone ^
    --include-package=flask ^
    --include-package=flask_cors ^
    --include-package=flask_socketio ^
    --include-package=speech_recognition ^
    --include-package=pynput ^
    --include-data-dir=public=public ^
    --enable-plugin=pyside6 ^
    --disable-console ^
    --output-dir=dist ^
    --remove-output ^
    --company-name="Voice Command System" ^
    --product-name="Voice Command System" ^
    --file-version=1.0.0 ^
    --windows-icon-from-ico=public/favicon.ico ^
    app.py

:: Check if build succeeded
if not exist "dist\app.exe" if not exist "dist\app.dist\app.exe" (
    echo Build failed. Trying with simpler options...
    
    :: Try a simpler build
    python -m nuitka --standalone ^
        --include-data-dir=public=public ^
        --output-dir=dist ^
        app.py
)

:: Copy the database file to the output directory if it exists, or create a placeholder
echo.
echo Copying database file...
if exist "voicecommand.db" (
    if exist "dist\app.dist" (
        copy "voicecommand.db" "dist\app.dist\" /y
    ) else (
        copy "voicecommand.db" "dist\" /y
    )
) else (
    echo Database file not found. A new one will be created on first run.
)

:: Create a README.txt file with instructions
echo Creating README file...
(
echo Voice Command System
echo ====================
echo.
echo This application requires the voicecommand.db file to be present in the same folder.
echo If the database file is missing, the application will create a new empty database.
echo.
echo To start the application, run app.exe
) > dist\README.txt

echo.
echo Build completed.
echo.
echo If the build was successful, the executable is in the dist folder.
echo Make sure to copy the voicecommand.db file along with the executable when distributing.
echo.
pause 