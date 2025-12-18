@echo off
echo ========================================
echo BDD Automation AI Agents - Setup and Run
echo ========================================
echo.

echo Step 1: Installing dependencies...
pip install -r requirements.txt
echo.

echo Step 2: Checking for .env file...
if not exist .env (
    echo [WARNING] .env file not found!
    echo Please create .env file with your GROQ_API_KEY
    echo You can copy env_template.txt to .env and edit it
    echo.
    pause
    exit /b 1
) else (
    echo [OK] .env file found
)
echo.

echo Step 3: Running system test...
python test_system.py
echo.

echo Setup complete!
echo.
echo To run the pipeline, use:
echo   python orchestrator.py --requirements "Your requirements here" --feature-name test
echo.
pause










