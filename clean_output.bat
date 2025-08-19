@echo off
echo Cleaning TEST_IMAGE\OUTPUT directory...
echo.

if exist "TEST_IMAGE\OUTPUT" (
    echo Found OUTPUT directory. Removing all files...
    del /Q "TEST_IMAGE\OUTPUT\*.*"
    echo.
    echo ✓ Output directory cleaned successfully!
    echo.
    echo Files removed:
    dir "TEST_IMAGE\OUTPUT" /B 2>nul || echo (Directory is now empty)
) else (
    echo OUTPUT directory does not exist.
    echo Creating empty OUTPUT directory...
    mkdir "TEST_IMAGE\OUTPUT"
    echo ✓ Created empty OUTPUT directory.
)

echo.
pause 