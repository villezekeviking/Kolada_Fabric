@echo off
REM Setup script for Kolada Fabric deployment (Windows)
REM This script helps set up the required environment variables for deployment

echo ==============================================
echo Kolada Fabric - Environment Setup (Windows)
echo ==============================================
echo.

REM Check if .env file exists
if exist .env (
    echo Found existing .env file.
    echo Please edit .env file manually or delete it to start fresh.
    pause
    exit /b
)

echo Setting up environment variables...
echo.

REM Create .env file
echo # Microsoft Fabric Deployment Configuration > .env

REM Prompt for variables
set /p TENANT_ID="Enter your Azure AD Tenant ID: "
echo FABRIC_TENANT_ID=%TENANT_ID% >> .env

set /p CLIENT_ID="Enter your Service Principal Client ID: "
echo FABRIC_CLIENT_ID=%CLIENT_ID% >> .env

set /p CLIENT_SECRET="Enter your Service Principal Client Secret: "
echo FABRIC_CLIENT_SECRET=%CLIENT_SECRET% >> .env

set /p WORKSPACE_NAME="Enter your Fabric Workspace Name (press Enter for default 'KoladaWorkspace'): "
if "%WORKSPACE_NAME%"=="" set WORKSPACE_NAME=KoladaWorkspace
echo FABRIC_WORKSPACE_NAME=%WORKSPACE_NAME% >> .env

echo.
echo Environment setup complete!
echo Your configuration has been saved to .env
echo.
echo To deploy to Fabric, run:
echo   python deployment\deploy_to_fabric.py
echo.
echo Note: Make sure to set the environment variables from .env file before running:
echo   You can manually set them or use a tool like 'dotenv'
echo.
pause
