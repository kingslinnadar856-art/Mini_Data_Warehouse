@echo off
title Mini Data Warehouse using DuckDB and Python
cls
echo ==============================================================================
echo           MINI DATA WAREHOUSE USING DUCKDB AND PYTHON
echo           BTech 3rd-Year Data Engineering Practical Case Study
echo ==============================================================================
echo.
echo Please choose an option to execute:
echo.
echo  [1] Run Full Warehouse Pipeline (Generate - Load - Validate - Views - Reports)
echo  [2] Launch Streamlit Interactive Dashboard
echo  [3] Run Full Pipeline + Launch Dashboard (Live College Demo)
echo  [4] Run Data Generation Only (src/generate_data.py)
echo  [5] Run Data Loading Only (src/load_data.py)
echo  [6] Run Data Cleaning & Views (src/transform.py)
echo  [7] Run Analytics & Report Export (src/analytics.py)
echo  [8] Install / Verify Requirements (requirements.txt)
echo  [9] Exit
echo.
set /p choice="Enter your choice (1-9): "

if "%choice%"=="1" (
    cls
    echo [*] Running full warehouse pipeline...
    python src\main.py
    pause
    goto end
)

if "%choice%"=="2" (
    cls
    echo [*] Launching Streamlit Reporting Dashboard on http://localhost:8501 ...
    python -m streamlit run dashboard\app.py
    goto end
)

if "%choice%"=="3" (
    cls
    echo [*] Step 1: Executing Warehouse Pipeline...
    python src\main.py
    echo.
    echo [*] Step 2: Launching Streamlit Dashboard...
    python -m streamlit run dashboard\app.py
    goto end
)

if "%choice%"=="4" (
    cls
    echo [*] Generating datasets...
    python src\generate_data.py
    pause
    goto end
)

if "%choice%"=="5" (
    cls
    echo [*] Loading data into DuckDB...
    python src\load_data.py
    pause
    goto end
)

if "%choice%"=="6" (
    cls
    echo [*] Performing validation and creating analytical views...
    python src\transform.py
    pause
    goto end
)

if "%choice%"=="7" (
    cls
    echo [*] Running analytics and exporting reports...
    python src\analytics.py
    pause
    goto end
)

if "%choice%"=="8" (
    cls
    echo [*] Installing dependencies from requirements.txt...
    python -m pip install -r requirements.txt
    pause
    goto end
)

if "%choice%"=="9" (
    exit
)

:end
