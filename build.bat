@echo off
echo Building VoiceCommand executable...
pyinstaller voicecommand.spec --clean
echo Build completed. Executable is in the dist folder.
pause 