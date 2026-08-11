@echo off
title IDX Screener Hadi Lie — Scan Harian
color 0A
cls

echo ============================================================
echo   IDX SCREENER — Hadi Lie
echo   Sistem Pola Candlestick Proprietary
echo ============================================================
echo.

:: Pindah ke folder screener (otomatis dari lokasi .bat)
cd /d "%~dp0"

:: Cek apakah Python ada
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python tidak ditemukan!
    echo Silakan install Python dari https://python.org
    echo Pastikan centang "Add Python to PATH" saat install.
    pause
    exit /b
)

:: Cek apakah ada file di folder data\
set DATACOUNT=0
for %%f in (data\*.xls data\*.xlsx data\*.csv) do set /a DATACOUNT+=1

if %DATACOUNT%==0 (
    echo [WARNING] Tidak ada file data di folder data\
    echo.
    echo Pilih mode:
    echo   1. Gunakan data yfinance otomatis (delay ~15 menit)
    echo   2. Keluar dan taruh file XLS dulu
    echo.
    set /p PILIH="Pilihan (1/2): "
    if "!PILIH!"=="1" goto AUTO
    goto END
)

echo [OK] Ditemukan %DATACOUNT% file data
echo.

:MENU
echo Pilih mode scan:
echo   1. Scan Harian (dari file XLS RTI)
echo   2. Scan Otomatis (yfinance, delay 15 menit)
echo   3. Screening Opening Pagi
echo   4. Keluar
echo.
set /p MODE="Pilihan (1/2/3/4): "

if "%MODE%"=="1" goto HARIAN
if "%MODE%"=="2" goto AUTO
if "%MODE%"=="3" goto OPENING
if "%MODE%"=="4" goto END
goto MENU

:HARIAN
echo.
echo [>>] Menjalankan Scan Harian dari file XLS...
echo.
python run_screener.py
goto DONE

:AUTO
echo.
echo [>>] Mengambil data dari yfinance (butuh internet)...
echo.
python run_screener.py --auto
goto DONE

:OPENING
echo.
echo [>>] Menjalankan Screening Opening Pagi...
echo.
python run_intraday.py
goto DONE

:DONE
echo.
echo ============================================================
echo   Selesai! Hasil tersimpan di folder output\
echo ============================================================
echo.

:END
pause
