@ECHO OFF

SET COMPORT=""
SET /A RESET=0
SET /A SETUP=0
SET /A APPROVE=0
SET /A PACKAGE=0

IF "%1" == "" ( GOTO :NOARGS )

@REM Looping through the arguments given...
:LOOP
IF NOT "%1" == "" (
    @REM If variable is equal to -p or --port
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

    @REM If variable is equal to -r or --reset
    IF "%1" == "-r" ( SET /A RESET=1 )
    IF "%1" == "--reset" ( SET /A RESET=1 )

    @REM If variable is equal to -s or --setup
    IF "%1" == "-s" ( SET /A SETUP=1 )
    IF "%1" == "--setup" ( SET /A SETUP=1 )

    @REM If variable is equal to -h or --help
    IF "%1" == "-h" ( GOTO HELP )
    IF "%1" == "--help" ( GOTO HELP )

    @REM If variable is equal to -y or --yes
    IF "%1" == "-y" ( SET /A APPROVE=1 )
    IF "%1" == "--yes" ( SET /A APPROVE=1 )
    SHIFT
    GOTO :LOOP
)

@REM Check if variable COMPORT is not left empty
IF NOT "%COMPORT%" == """" (
    IF %SETUP% == 1 (
        GOTO :SETUP
    )
    IF %RESET% == 1 (
        GOTO :RESET
    )
) ELSE (
    GOTO :NOARGS
)

@REM Package installer
:PACKAGE
    ECHO Making sure the package installer is up to date...
    py -m pip install --upgrade pip
    ECHO.
    ECHO Installing Python packages...
    py -m pip install -r requirements.txt
    SET PACKAGE=1

@REM Reset function for the ESP32
:RESET
    IF NOT %PACKAGE% == 1 ( CALL :PACKAGE )
    IF NOT %APPROVE% == 1 (
        ECHO Do you want to reset your device? y/n
        SET /P INPUT=Enter yes or no: 
        IF NOT "%INPUT%" == "y" (
            ECHO Aborted reset. Exiting...
            GOTO :EndOfFunction
        )
    )
    py -m esptool --port %COMPORT% erase_flash
    py -m esptool --chip esp32 --port %COMPORT% --baud 460800 write_flash -z 0x1000 ESP32\esp32-20220117-v1.18.bin
    SET /A RESET=0
    TIMEOUT /T 1 >NUL

@REM Setup function for the ESP32
:SETUP
    IF NOT %PACKAGE% == 1 ( CALL :PACKAGE )
    IF %RESET% == 1 ( CALL :RESET )

    ECHO UPLOADING FILES TO ESP32... Please do not disconnect the device until the upload is done.
    ECHO UPLOADING BASE FILES...
    cd .\ESP32\
    FOR %%F in (*.py) DO ampy --port %COMPORT% --baud 115200 --delay 1 put %%F
    
    ECHO UPLOADING SENSOR FILES...
    ampy --port %COMPORT% --baud 115200 --delay 1 mkdir sensor
    cd .\sensor\
    FOR %%F in (*.py) DO ampy --port %COMPORT% --baud 115200 --delay 1 put %%F /sensor/%%F

    ECHO UPLOADING UMQTT FILES...
    cd ..
    cd .\umqtt\
    ampy --port %COMPORT% --baud 115200 --delay 1 mkdir umqtt
    FOR %%F in (*.py) DO ampy --port %COMPORT% --baud 115200 --delay 1 put %%F /umqtt/%%F

    ECHO UPLOADING WIRELESS FILES...
    cd ..
    cd .\wireless\
    ampy --port %COMPORT% --baud 115200 --delay 1 mkdir wireless
    FOR %%F in (*.py) DO ampy --port %COMPORT% --baud 115200 --delay 1 put %%F /wireless/%%F

    ECHO DONE! You can safely disconnect the ESP32.
    GOTO :EndOfFunction

@REM Go here if the script is used improperly
:NOARGS
    ECHO Use -h or --help for help.
    GOTO :EndOfFunction

@REM Go here if flags -h or --help are used
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
    ECHO    -r OR --reset
    ECHO        Use this flag if a complete reset is desired.
    ECHO        The -p OR --port flag is required for this command.
    ECHO        CAUTION: All data on the device will be erased if this flag is used.
    ECHO. 
    ECHO    -s OR --setup
    ECHO        Use this flag to setup the ESP32 device.
    ECHO        All necessary packages and files will be installed and uploaded to the ESP32 device.
    ECHO        The -p OR --port flag is required for this command.
    ECHO.
    ECHO    -y OR --yes
    ECHO        This flag can be used to avoid further user input.
    ECHO        At this moment, it is only used for resetting the ESP32.
    GOTO :EndOfFunction

:EndOfFunction
