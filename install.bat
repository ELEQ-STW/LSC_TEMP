@ECHO OFF

SET COMPORT=""
SET /A FLASH=0
SET /A SETUP=0
SET /A PACKAGE=0

:: If no arguments are given:
IF "%1" == "" ( GOTO :NOARGS )

:: Looping through the arguments given...
:LOOP
IF NOT "%1" == "" (
    :: If variable is equal to -p or --port
    IF "%1" == "-p" (
        IF "%2" == "" ( GOTO :NOARGS )
        SET COMPORT=%2
        SHIFT
    )
    IF "%1" == "--port" (
        IF "%2" == "" ( GOTO :NOARGS )
        SET COMPORT=%2
        SHIFT
    )
    :: If variable is equal to -f or --flash
    IF "%1" == "-f" ( SET /A FLASH=1 )
    IF "%1" == "--flash" ( SET /A FLASH=1 )
    :: If variable is equal to -s or --setup
    IF "%1" == "-s" ( SET /A SETUP=1 )
    IF "%1" == "--setup" ( SET /A SETUP=1 )
    :: If variable is equal to -h or --help
    IF "%1" == "-h" ( GOTO :HELP )
    IF "%1" == "--help" ( GOTO :HELP )
    SHIFT
    GOTO :LOOP
)

:: Check if variable COMPORT is not left empty
IF NOT "%COMPORT%" == """" (
    IF %SETUP% == 1 ( GOTO :SETUP )
    IF %FLASH% == 1 ( GOTO :FLASH )
) ELSE ( GOTO :NOARGS )

:: Package installer
:PACKAGE
    ECHO Making sure the package installer is up to date...
    py -m pip install --upgrade pip
    ECHO.
    ECHO Installing Python packages...
    py -m pip install -r requirements.txt
    SET PACKAGE=1
    EXIT /B

:: (Re-)Flash function for the ESP32
:FLASH
    IF NOT %PACKAGE% == 1 ( CALL :PACKAGE )
    :: Flashing the ESP32
    py -m esptool --port %COMPORT% erase_flash
    py -m esptool --chip esp32 --port %COMPORT% --baud 460800 write_flash -z 0x1000 ESP32\esp32-20220117-v1.18.bin

    SET /A FLASH=0
    TIMEOUT /T 1 >NUL
    EXIT /B

:: Setup function for the ESP32
:SETUP
    IF NOT %PACKAGE% == 1 ( CALL :PACKAGE )
    IF %FLASH% == 1 ( CALL :FLASH )

    SETLOCAL ENABLEDELAYEDEXPANSION
    :: For loop through the directories
    SET I=0&SET "STR_FOLDERS= BASE SENSOR UMQTT WIRELESS"
    SET "STR_FOLDERS=%STR_FOLDERS: ="&SET /A I+=1&SET "STR_FOLDERS[!I!]=%"
    SET I=0&SET "CD_FOLDERS= .\ESP32\ .\sensor\ ..\umqtt\ ..\wireless\"
    SET "CD_FOLDERS=%CD_FOLDERS: ="&SET /A I+=1&SET "CD_FOLDERS[!I!]=%"
    SET I=0&SET "FOLDERS= none sensor umqtt wireless"
    SET "FOLDERS=%FOLDERS: ="&SET /A I+=1&SET "FOLDERS[!I!]=%"

    FOR /L %%D IN (1,1,4) DO (
        ECHO UPLOADING !STR_FOLDERS[%%D]! FILES...
        cd !CD_FOLDERS[%%D]!
        IF %%D == 1 (
            FOR %%F IN (*.py) DO ( ampy --port %COMPORT% --baud 115200 --delay 1 put %%F )
        ) ELSE (
            ampy --port %COMPORT% --baud 115200 --delay 1 mkdir !FOLDERS[%%D]!
            FOR %%F IN (*.py) DO ( ampy --port %COMPORT% --baud 115200 --delay 1 put %%F /!FOLDERS[%%D]!/%%F )
        )
    )
    ECHO DONE! You can safely disconnect the ESP32.
    EXIT

:: Go here if the script is used improperly
:NOARGS
    ECHO Use -h or --help for help.
    EXIT

:: Go here if flags -h or --help are used
:HELP
    ECHO Welcome to the Install Batch file for the LSC_TEMP project.
    ECHO This tool is used to configure the ESP32 microcontrollers for deployment.
    ECHO. 
    ECHO The tool has to following commands:
    ECHO    -h OR --help
    ECHO        Use this flag to get the help display.
    ECHO. 
    ECHO    -p OR --port COMx
    ECHO        Indicate which port you want to use.
    ECHO        Connect the ESP32 microcontroller and find the correct COM port via the Device Manager on your Windows PC.
    ECHO. 
    ECHO    -f OR --flash
    ECHO        Use this flag if you want to (re-)flash the device.
    ECHO        The -p OR --port flag is required for this command.
    ECHO        CAUTION: All data on the device will be erased if this flag is used.
    ECHO. 
    ECHO    -s OR --setup
    ECHO        Use this flag to setup the ESP32 device.
    ECHO        All necessary packages and files will be installed and uploaded to the ESP32 device.
    ECHO        The -p OR --port flag is required for this command.
    ECHO        If the ESP32 device has not been used before, a flash is recommended.
    ECHO        Use the -f OR --flash flag.
    EXIT
