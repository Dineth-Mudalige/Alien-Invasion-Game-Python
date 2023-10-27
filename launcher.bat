@ECHO OFF

REM Activate the virtual environment
call "C:\Users\mudaliged\OneDrive - The University of Melbourne\r_game\Alien-Invasion-Game-Python\virtualenv\Scripts\activate"

REM Start the sensor based classifier first
start "sensor" cmd /k "python sensor.py"

REM Start the game 
start "alien_invasion" cmd /k "python alien_invasion.py"

REM Monitor the game and close the sensor when the first one is closed
:MonitorLoop
tasklist /FI "IMAGENAME eq python.exe" | find "alien_invasion.py" >NUL
if errorlevel 1 (
    echo Second script is closed.
    taskkill /F /IM "python.exe" /FI "WINDOWTITLE eq sensor"
    echo First script is closed.
    exit
)
goto MonitorLoop
