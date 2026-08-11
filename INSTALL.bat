@echo off
title IDX Screener — Instalasi Pertama Kali
color 0B
cls

echo ============================================================
echo   IDX SCREENER — INSTALASI PERTAMA KALI
echo   Hadi Lie | Sistem Pola Candlestick Proprietary
echo ============================================================
echo.

cd /d "%~dp0"

:: Cek Python
echo [1/3] Mengecek Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Python tidak ditemukan!
    echo.
    echo Silakan:
    echo   1. Buka https://python.org/downloads
    echo   2. Download Python 3.11 atau terbaru
    echo   3. Jalankan installer
    echo   4. PENTING: Centang "Add Python to PATH"
    echo   5. Setelah selesai, jalankan INSTALL.bat ini lagi
    echo.
    pause
    exit /b
)
python --version
echo [OK] Python ditemukan!
echo.

:: Install dependensi
echo [2/3] Menginstall dependensi Python...
echo (Proses ini butuh internet, tunggu 1-2 menit)
echo.
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo [ERROR] Gagal install dependensi.
    echo Pastikan koneksi internet aktif, lalu coba lagi.
    pause
    exit /b
)
echo.
echo [OK] Semua dependensi berhasil diinstall!
echo.

:: Test import
echo [3/3] Mengecek instalasi...
python -c "import pandas, numpy, yfinance, openpyxl; print('Semua library OK!')"
if errorlevel 1 (
    echo [ERROR] Ada library yang gagal diimport.
    pause
    exit /b
)
echo.

:: Buat folder jika belum ada
if not exist "data" mkdir data
if not exist "output" mkdir output
if not exist "logs" mkdir logs

echo ============================================================
echo   INSTALASI SELESAI!
echo ============================================================
echo.
echo Cara pakai selanjutnya:
echo   1. Taruh file .xls dari RTI ke folder:  data\
echo   2. Double-click:                         SCAN_HARIAN.bat
echo   3. Lihat hasil di folder:                output\
echo.
echo Atau jalankan langsung:
echo   python run_screener.py          (dari file XLS)
echo   python run_screener.py --auto   (dari yfinance)
echo   python run_intraday.py          (screening opening)
echo.
pause
